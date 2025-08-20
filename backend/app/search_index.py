import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pdfminer.high_level import extract_text

# Lightweight, fast model (<100MB)
_EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@dataclass
class Section:
    pdf_name: str
    heading: str
    page_start: int
    page_end: int
    text: str
    vector: np.ndarray

class DocIndex:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.model = SentenceTransformer(_EMB_MODEL)
        self.sections: List[Section] = []
        self.documents: Dict[str, Dict[str, Any]] = {}  # name -> {"pages": int}
        self.faiss_index = None
        self.id2idx: Dict[int, int] = {}

        # Boot from disk PDFs if present
        self._cold_boot()

    # ---------- Public ----------
    def list_pdf_names(self) -> List[str]:
        return [f for f in os.listdir(self.storage_dir) if f.lower().endswith(".pdf")]

    def add_pdfs(self, paths: List[str]):
        secs = []
        for p in paths:
            name = os.path.basename(p)
            if name in self.documents:
                continue
            try:
                full_text = extract_text(p) or ""
            except Exception:
                full_text = ""
            pages = max(1, full_text.count("\x0c"))  # crude page count fallback
            self.documents[name] = {"pages": pages}

            # Split into sections using heading heuristics (Round 1A-ish)
            split_sections = self._split_into_sections(full_text)
            
            # Batch embed all sections at once (much faster)
            if split_sections:
                texts = [s["text"] for s in split_sections]
                embeddings = self._embed(texts)
                
                for i, s in enumerate(split_sections):
                    secs.append(Section(
                        pdf_name=name,
                        heading=s["heading"],
                        page_start=s["page_start"],
                        page_end=s["page_end"],
                        text=s["text"],
                        vector=embeddings[i]
                    ))
        
        # Merge & rebuild FAISS
        if secs:
            self.sections.extend(secs)
            self._rebuild_faiss()



    def search_sections(self, query: str, top_k: int = 5, exclude_pdf: Optional[str] = None):
        if not self.sections:
            return []
        qv = self._embed([query])[0].astype("float32")
        D, I = self.faiss_index.search(np.array([qv]), top_k * 3)  # overfetch, filter later
        hits = []
        for idx in I[0]:
            if int(idx) == -1:
                continue
            s = self.sections[idx]
            if exclude_pdf and s.pdf_name == exclude_pdf:
                continue
            hits.append(s)
            if len(hits) == top_k:
                break
        return hits

    def make_snippets(self, sections: List[Section]) -> List[Dict[str, Any]]:
        """
        Return 2–4 sentence snippets per section, with navigation metadata.
        """
        out = []
        for s in sections:
            sents = self._split_sentences(s.text)
            # pick the densest 3 sentences near the middle as snippet
            if len(sents) <= 4:
                snippet = " ".join(sents)
            else:
                mid = len(sents) // 2
                win = sents[max(0, mid-2): min(len(sents), mid+2)]
                snippet = " ".join(win)
            out.append({
                "pdf": s.pdf_name,
                "heading": s.heading,
                "page_start": s.page_start,
                "page_end": s.page_end,
                "snippet": snippet.strip()
            })
        return out

    # ---------- Internal ----------
    def _cold_boot(self):
        paths = [os.path.join(self.storage_dir, p) for p in self.list_pdf_names()]
        if paths:
            self.add_pdfs(paths)

    def _rebuild_faiss(self):
        vecs = np.array([s.vector for s in self.sections], dtype="float32")
        if vecs.size == 0:
            return
        d = vecs.shape[1]
        index = faiss.IndexFlatIP(d)  # cosine via normalized vectors
        faiss.normalize_L2(vecs)
        index.add(vecs)
        self.faiss_index = index

    def _embed(self, texts: List[str]) -> np.ndarray:
        emb = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return np.array(emb, dtype="float32")

    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Very simple sectionizer:
        - Heading: line with Title Case or ALL CAPS and followed by blank line or longer text
        - Derive pseudo pages by splitting on form feeds if present
        """
        # page hints
        pages = text.split("\x0c")
        sections = []
        for p_idx, page_txt in enumerate(pages):
            lines = [l.strip() for l in page_txt.splitlines() if l.strip()]
            if not lines:
                continue
            cur_heading = f"Page {p_idx+1}"
            cur_buf = []
            for ln in lines:
                if self._looks_like_heading(ln):
                    # flush previous
                    if cur_buf:
                        sections.append({
                            "heading": cur_heading,
                            "page_start": p_idx+1,
                            "page_end": p_idx+1,
                            "text": "\n".join(cur_buf)
                        })
                        cur_buf = []
                    cur_heading = ln
                else:
                    cur_buf.append(ln)
            if cur_buf:
                sections.append({
                    "heading": cur_heading,
                    "page_start": p_idx+1,
                    "page_end": p_idx+1,
                    "text": "\n".join(cur_buf)
                })
        # Fallback: if nothing was detected, create one section
        if not sections and text.strip():
            sections = [{
                "heading": "Document",
                "page_start": 1,
                "page_end": max(1, text.count("\x0c")),
                "text": text
            }]
        return sections

    @staticmethod
    def _looks_like_heading(line: str) -> bool:
        if len(line) > 120:  # too long, probably body
            return False
        # Title Case or ALL CAPS or numbered
        return bool(
            re.match(r"^([A-Z][a-z]+(\s[A-Z][a-z]+)*)$", line) or
            re.match(r"^[A-Z0-9 \-–:]{3,}$", line) or
            re.match(r"^(\d+(\.\d+)*)\s+", line)
        )

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        # naive splitter that works okay on academic PDFs
        s = re.split(r'(?<=[.!?])\s+(?=[A-Z(])', text.strip())
        return [x.strip() for x in s if x.strip()]
