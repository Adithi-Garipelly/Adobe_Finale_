# backend/app/semantic.py
import os
import json
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from pypdf import PdfReader
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
INDEX_DIR = os.path.join(DATA_DIR, "index")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def _is_heading(line: str) -> bool:
    """Enhanced heading detection with competition-ready heuristics"""
    line = line.strip()
    if not line:
        return False
    
    # Academic paper patterns
    academic_patterns = [
        r"^(abstract|introduction|related work|background|method|methods|approach|results|discussion|conclusion|references|bibliography|acknowledgments|appendix)$",
        r"^(literature review|theoretical framework|experimental setup|evaluation|analysis|findings|implications|future work)$",
        r"^(problem statement|hypothesis|objectives|contributions|limitations|assumptions)$"
    ]
    
    for pattern in academic_patterns:
        if re.match(pattern, line.lower()):
            return True
    
    # Numbered headings (1., 1.1, 2.3.4, etc.)
    if re.match(r"^(\d+(\.\d+)*)\s+.+", line):
        return True
    
    # Roman numerals (I., II., III., etc.)
    if re.match(r"^[IVX]+\.\s+.+", line):
        return True
    
    # Title Case with few words (likely headings)
    if len(line.split()) <= 12 and line[:1].isupper() and sum(w[0].isupper() for w in line.split()) >= max(2, len(line.split())//2):
        return True
    
    # All caps (common in technical documents)
    if line.isupper() and len(line.split()) <= 8:
        return True
    
    return False

def _clean_text(text: str) -> str:
    """Clean and normalize text for better processing"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '-')
    
    return text.strip()

def _split_into_sections(text: str) -> List[Dict[str, Any]]:
    """Enhanced section splitting with better content handling"""
    # Clean text first
    text = _clean_text(text)
    
    sections = []
    current = {"heading": "Document", "content": []}
    
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
            
        if _is_heading(line):
            # Save previous section if it has content
            if current["content"] and len(" ".join(current["content"]).strip()) > 50:
                sections.append({
                    "heading": current["heading"], 
                    "content": " ".join(current["content"]).strip()
                })
            current = {"heading": line, "content": []}
        else:
            current["content"].append(raw_line)
    
    # Add the last section
    if current["content"] and len(" ".join(current["content"]).strip()) > 50:
        sections.append({
            "heading": current["heading"], 
            "content": " ".join(current["content"]).strip()
        })
    
    return sections

def _snippets_from_text(text: str, query: str, max_sents: int = 4) -> str:
    """Enhanced query-biased snippet extraction"""
    # Clean text
    text = _clean_text(text)
    
    # Split into sentences (more robust)
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sents:
        return text[:300] + "..." if len(text) > 300 else text
    
    # Extract query keywords
    query_words = set(re.findall(r"\w+", query.lower()))
    
    # Score sentences based on query relevance
    scored = []
    for i, sent in enumerate(sents):
        sent_words = set(re.findall(r"\w+", sent.lower()))
        
        # Calculate relevance score
        overlap = len(query_words & sent_words)
        density = overlap / max(len(sent_words), 1)  # Normalize by sentence length
        
        # Bonus for sentences with more query words
        score = overlap + (density * 0.5)
        
        scored.append((score, i, sent))
    
    # Sort by relevance score
    scored.sort(reverse=True)
    
    # Pick top sentences, maintaining order
    chosen_idx = sorted([i for _, i, _ in scored[:max_sents]])
    snippet = " ".join(sents[i] for i in chosen_idx)
    
    # Ensure snippet isn't too long
    if len(snippet) > 500:
        snippet = snippet[:500] + "..."
    
    return snippet.strip()

class SectionMeta(BaseModel):
    """Enhanced section metadata with competition-ready fields"""
    id: str
    doc_id: str
    doc_name: str
    heading: str
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    word_count: int = 0
    created_at: str = ""
    updated_at: str = ""

class SemanticIndex:
    """Enhanced semantic index with competition-ready features"""
    
    def __init__(self, index_dir: str = INDEX_DIR, model_name: str = MODEL_NAME):
        self.index_dir = index_dir
        self.meta_path = os.path.join(index_dir, "sections_meta.json")
        self.faiss_path = os.path.join(index_dir, "faiss.index")
        self.model_name = model_name
        
        # Initialize with error handling
        try:
            self.model = SentenceTransformer(model_name)
            self.dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ SentenceTransformer loaded: {model_name} (dim: {self.dim})")
        except Exception as e:
            logger.error(f"❌ Failed to load SentenceTransformer: {e}")
            raise
        
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
                logger.info(f"✅ Loaded existing index: {len(self.meta)} sections, {self.index.ntotal} vectors")
            else:
                self.index = faiss.IndexFlatIP(self.dim)
                logger.info("🆕 Created new FAISS index")
        except Exception as e:
            logger.error(f"❌ Error loading index: {e}")
            self.index = faiss.IndexFlatIP(self.dim)
            self.meta = []
    
    def _save(self, embeddings: Optional[np.ndarray] = None):
        """Save index and metadata with error handling"""
        try:
            if embeddings is not None and self.index.ntotal == 0:
                self.index = faiss.IndexFlatIP(self.dim)
                self.index.add(embeddings)
            
            faiss.write_index(self.index, self.faiss_path)
            
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump([m.dict() for m in self.meta], f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Index saved: {len(self.meta)} sections, {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"❌ Error saving index: {e}")
            raise
    
    def clear(self):
        """Clear all indexed data"""
        try:
            self.index = faiss.IndexFlatIP(self.dim)
            self.meta = []
            
            if os.path.exists(self.meta_path):
                os.remove(self.meta_path)
            if os.path.exists(self.faiss_path):
                os.remove(self.faiss_path)
            
            logger.info("🗑️ Index cleared successfully")
        except Exception as e:
            logger.error(f"❌ Error clearing index: {e}")
    
    def _normalize(self, X: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity"""
        norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
        return X / norms
    
    def ingest_pdf(self, file_path: str, doc_id: Optional[str] = None, doc_name: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced PDF ingestion with better error handling"""
        try:
            doc_id = doc_id or uuid.uuid4().hex
            doc_name = doc_name or os.path.basename(file_path)
            
            logger.info(f"📚 Processing PDF: {doc_name}")
            
            # Read PDF with error handling
            try:
                reader = PdfReader(file_path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                logger.error(f"❌ Error reading PDF {doc_name}: {e}")
                return {"error": f"Failed to read PDF: {e}"}
            
            if not text.strip():
                logger.warning(f"⚠️ PDF {doc_name} has no extractable text")
                return {"warning": "No text content found"}
            
            # Split into sections
            sections = _split_into_sections(text)
            logger.info(f"📖 Extracted {len(sections)} sections from {doc_name}")
            
            new_embeddings = []
            new_meta = []
            
            for sec in sections:
                if len(sec["content"].strip()) < 100:  # Skip very short sections
                    continue
                
                s_id = uuid.uuid4().hex
                meta = SectionMeta(
                    id=s_id,
                    doc_id=doc_id,
                    doc_name=doc_name,
                    heading=sec["heading"],
                    content=sec["content"],
                    word_count=len(sec["content"].split()),
                    created_at=str(np.datetime64('now')),
                    updated_at=str(np.datetime64('now'))
                )
                
                new_meta.append(meta)
                
                # Generate embedding
                try:
                    embedding = self.model.encode(sec["content"], normalize_embeddings=True)
                    new_embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"❌ Error encoding section {s_id}: {e}")
                    continue
            
            if not new_meta:
                logger.warning(f"⚠️ No valid sections found in {doc_name}")
                return {"warning": "No valid sections extracted"}
            
            # Add to index
            new_embeddings = np.vstack(new_embeddings).astype("float32")
            
            if self.index is None or self.index.d != self.dim:
                self.index = faiss.IndexFlatIP(self.dim)
            
            self.index.add(new_embeddings)
            self.meta.extend(new_meta)
            
            # Save updated index
            self._save()
            
            logger.info(f"✅ Successfully indexed {len(new_meta)} sections from {doc_name}")
            return {
                "success": True,
                "doc_name": doc_name,
                "sections_added": len(new_meta),
                "total_sections": len(self.meta)
            }
            
        except Exception as e:
            logger.error(f"❌ Error ingesting PDF {file_path}: {e}")
            return {"error": f"Failed to ingest PDF: {e}"}
    
    def scan_and_ingest(self, upload_dir: str = UPLOAD_DIR) -> Dict[str, Any]:
        """Scan upload directory and ingest new PDFs"""
        try:
            pdfs = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) 
                   if f.lower().endswith(".pdf")]
            
            logger.info(f"🔍 Found {len(pdfs)} PDFs in upload directory")
            
            results = []
            for pdf_path in pdfs:
                doc_name = os.path.basename(pdf_path)
                
                # Check if already ingested
                if any(doc_name == m.doc_name for m in self.meta):
                    logger.info(f"⏭️ Skipping already indexed: {doc_name}")
                    continue
                
                result = self.ingest_pdf(pdf_path, doc_name=doc_name)
                results.append(result)
            
            return {
                "scanned": len(pdfs),
                "ingested": len([r for r in results if r.get("success")]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Error scanning upload directory: {e}")
            return {"error": f"Scan failed: {e}"}
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Enhanced semantic search with better error handling"""
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("⚠️ No indexed content available for search")
                return []
            
            if not query.strip():
                logger.warning("⚠️ Empty query provided")
                return []
            
            # Generate query embedding
            try:
                q_emb = self.model.encode([query], normalize_embeddings=True).astype("float32")
            except Exception as e:
                logger.error(f"❌ Error encoding query: {e}")
                return []
            
            # Search with error handling
            try:
                scores, idxs = self.index.search(q_emb, min(top_k, self.index.ntotal))
            except Exception as e:
                logger.error(f"❌ Error searching index: {e}")
                return []
            
            # Process results
            results = []
            for j, score in zip(idxs[0], scores[0]):
                if j == -1 or j >= len(self.meta):
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
                    "word_count": m.word_count,
                    "full_content": m.content[:1000] + "..." if len(m.content) > 1000 else m.content
                })
            
            logger.info(f"🔍 Search completed: {len(results)} results for query '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in search: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            return {
                "total_sections": len(self.meta),
                "indexed_vectors": self.index.ntotal if self.index else 0,
                "embedding_dimension": self.dim,
                "model_name": self.model_name,
                "documents": len(set(m.doc_id for m in self.meta)),
                "index_size_mb": os.path.getsize(self.faiss_path) / (1024 * 1024) if os.path.exists(self.faiss_path) else 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}
