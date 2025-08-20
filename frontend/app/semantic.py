# backend/app/semantic.py
import os
import json
import re
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from pypdf import PdfReader
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
INDEX_DIR = os.path.join(DATA_DIR, "index")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def _is_heading(line: str) -> bool:
    """Detect if a line is a heading using universal heuristics"""
    line = line.strip()
    if not line:
        return False
    
    # Simple universal heuristics: numbered headings, Title Case, known words
    if re.match(r"^(abstract|introduction|related work|background|method|methods|approach|results|discussion|conclusion|references)$", line.strip().lower()):
        return True
    
    if re.match(r"^(\d+(\.\d+)*)\s+.+", line):  # 1., 1.1, 2.3.4 ...
        return True
    
    # Title Case with few words
    if len(line.split()) <= 10 and line[:1].isupper() and sum(w[0].isupper() for w in line.split()) >= max(2, len(line.split())//2):
        return True
    
    return False

def _clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    return text.strip()

def _split_into_sections(text: str) -> List[Dict[str, Any]]:
    """Split text into logical sections using universal heuristics"""
    sections = []
    current = {"heading": "Document", "content": []}
    
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if _is_heading(line):
            if current["content"]:
                sections.append({
                    "heading": current["heading"], 
                    "content": _clean_text("\n".join(current["content"]))
                })
            current = {"heading": line, "content": []}
        else:
            current["content"].append(raw_line)
    
    if current["content"]:
        sections.append({
            "heading": current["heading"], 
            "content": _clean_text("\n".join(current["content"]))
        })
    
    return sections

def _snippets_from_text(text: str, query: str, max_sents=4) -> str:
    """Extract query-biased snippets from text"""
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sents:
        return ""
    
    q = set(re.findall(r"\w+", query.lower()))
    scored = []
    
    for i, s in enumerate(sents):
        toks = set(re.findall(r"\w+", s.lower()))
        overlap = len(q & toks)
        scored.append((overlap, i, s))
    
    scored.sort(reverse=True)
    
    # Pick top sentences, keep order
    chosen_idx = sorted([i for _, i, _ in scored[:max_sents]])
    snippet = " ".join(sents[i] for i in chosen_idx)
    
    return snippet.strip()

class SectionMeta(BaseModel):
    id: str
    doc_id: str
    doc_name: str
    heading: str
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None

class SemanticIndex:
    def __init__(self, index_dir: str = INDEX_DIR, model_name: str = MODEL_NAME):
        self.index_dir = index_dir
        self.meta_path = os.path.join(index_dir, "sections_meta.json")
        self.faiss_path = os.path.join(index_dir, "faiss.index")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.meta: List[SectionMeta] = []
        self._load()
    
    def _load(self):
        """Load existing index and metadata"""
        try:
            if os.path.exists(self.meta_path) and os.path.exists(self.faiss_path):
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.meta = [SectionMeta(**m) for m in json.load(f)]
                self.index = faiss.read_index(self.faiss_path)
                logger.info(f"✅ Loaded existing index with {len(self.meta)} sections")
            else:
                self.index = faiss.IndexFlatIP(self.dim)
                logger.info("🆕 Created new FAISS index")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self.index = faiss.IndexFlatIP(self.dim)
            self.meta = []
    
    def _save(self, embeddings: Optional[np.ndarray] = None):
        """Save index and metadata"""
        try:
            if embeddings is not None and self.index.ntotal == 0:
                self.index = faiss.IndexFlatIP(self.dim)
                self.index.add(embeddings)
            
            faiss.write_index(self.index, self.faiss_path)
            
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump([m.dict() for m in self.meta], f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Saved index with {len(self.meta)} sections")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def clear(self):
        """Clear the entire index"""
        self.index = faiss.IndexFlatIP(self.dim)
        self.meta = []
        
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)
        if os.path.exists(self.faiss_path):
            os.remove(self.faiss_path)
        
        logger.info("🗑️ Index cleared")
    
    def _normalize(self, X: np.ndarray) -> np.ndarray:
        """Normalize embeddings for cosine similarity"""
        norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
        return X / norms
    
    def ingest_pdf(self, file_path: str, doc_id: Optional[str] = None, doc_name: Optional[str] = None):
        """Ingest a single PDF file"""
        try:
            doc_id = doc_id or uuid.uuid4().hex
            doc_name = doc_name or os.path.basename(file_path)
            
            logger.info(f"📄 Ingesting PDF: {doc_name}")
            
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            
            sections = _split_into_sections(text)
            new_embeddings = []
            new_meta = []
            
            for sec in sections:
                if len(sec["content"].strip()) < 200:  # Skip tiny sections
                    continue
                
                s_id = uuid.uuid4().hex
                meta = SectionMeta(
                    id=s_id,
                    doc_id=doc_id,
                    doc_name=doc_name,
                    heading=sec["heading"],
                    content=sec["content"]
                )
                
                new_meta.append(meta)
                new_embeddings.append(self.model.encode(sec["content"], normalize_embeddings=True))
            
            if not new_meta:
                logger.warning(f"No valid sections found in {doc_name}")
                return
            
            new_embeddings = np.vstack(new_embeddings).astype("float32")
            
            if self.index is None or self.index.d != self.dim:
                self.index = faiss.IndexFlatIP(self.dim)
            
            self.index.add(new_embeddings)
            self.meta.extend(new_meta)
            
            self._save()
            logger.info(f"✅ Ingested {len(new_meta)} sections from {doc_name}")
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {file_path}: {e}")
            raise
    
    def scan_and_ingest(self, upload_dir: str = UPLOAD_DIR):
        """Scan directory and ingest all PDFs"""
        try:
            pdfs = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) 
                   if f.lower().endswith(".pdf")]
            
            logger.info(f"🔍 Found {len(pdfs)} PDFs to process")
            
            for p in pdfs:
                # Naive "already ingested" guard: doc_name match
                if any(os.path.basename(p) == m.doc_name for m in self.meta):
                    logger.info(f"⏭️ Already ingested: {os.path.basename(p)}")
                    continue
                
                self.ingest_pdf(p, doc_name=os.path.basename(p))
            
            logger.info(f"✅ Scan and ingest complete. Total sections: {len(self.meta)}")
            
        except Exception as e:
            logger.error(f"Error in scan and ingest: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant sections"""
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("Index is empty, cannot search")
                return []
            
            q_emb = self.model.encode([query], normalize_embeddings=True).astype("float32")
            scores, idxs = self.index.search(q_emb, top_k)
            
            results = []
            for j, score in zip(idxs[0], scores[0]):
                if j == -1:
                    continue
                
                m = self.meta[j]
                snippet = _snippets_from_text(m.content, query, max_sents=4)
                
                results.append({
                    "score": float(score),
                    "doc_id": m.doc_id,
                    "doc_name": m.doc_name,
                    "heading": m.heading,
                    "snippet": snippet,
                    "section_id": m.id,
                })
            
            logger.info(f"🔍 Search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            return {
                "total_sections": len(self.meta),
                "indexed_vectors": self.index.ntotal if self.index else 0,
                "embedding_dimension": self.dim,
                "model_name": self.model_name,
                "documents": len(set(m.doc_id for m in self.meta))
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
