import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .search_index import DocIndex
from .insights import build_insights_payload, generate_insights_from_selection
from .tts import synthesize_podcast

# ---------- ENV ----------
ADOBE_EMBED_API_KEY = os.getenv("ADOBE_EMBED_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "azure")

UPLOAD_DIR = os.path.abspath(os.getenv("UPLOAD_DIR", "./data/uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- APP ----------
app = FastAPI(title="Adobe Finale Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- GLOBAL INDEX ----------
index = DocIndex(storage_dir=UPLOAD_DIR)

# ---------- MODELS ----------
class AnalyzeSelectionReq(BaseModel):
    current_pdf: str
    selected_text: str
    max_sections: int = 5

class PodcastReq(BaseModel):
    script: str
    speaker_mode: str = "duo"  # "duo" or "single"

# ---------- ROUTES ----------
@app.get("/health")
def health():
    return {"status": "ok", "pdf_count": len(index.documents)}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    if len(files) == 0:
        raise HTTPException(400, "No files provided.")
    if len(files) > 50:
        raise HTTPException(400, "Max 50 files per batch.")

    saved = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(400, f"Only PDF allowed: {f.filename}")
        safe_name = f.filename.replace("/", "_")
        out_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(out_path, "wb") as w:
            w.write(await f.read())
        saved.append(safe_name)

    # (Re)index new PDFs incrementally
    index.add_pdfs([os.path.join(UPLOAD_DIR, s) for s in saved])
    return {"files": saved}

@app.get("/files")
def list_files():
    return {"files": sorted(index.list_pdf_names())}

@app.get("/files/{filename}")
def get_file(filename: str):
    safe = filename.replace("/", "_")
    path = os.path.join(UPLOAD_DIR, safe)
    if not os.path.isfile(path):
        raise HTTPException(404, "File not found.")
    # Ensure CORS works: FastAPI static file response
    return FileResponse(path, media_type="application/pdf", filename=safe)

@app.post("/analyze_selection")
def analyze_selection(req: AnalyzeSelectionReq):
    # 1) semantic search for relevant sections (excluding current_pdf if you want)
    results = index.search_sections(req.selected_text, top_k=req.max_sections, exclude_pdf=req.current_pdf)

    # 2) pick 2–4 sentence snippets per section
    snippets = index.make_snippets(results)

    # 3) insights with Gemini (grounded strictly on snippets)
    insights, podcast_script = generate_insights_from_selection(
        selection=req.selected_text,
        related=snippets
    )

    payload = build_insights_payload(
        current_pdf=req.current_pdf,
        selection=req.selected_text,
        snippets=snippets,
        insights=insights,
        podcast_script=podcast_script
    )
    return payload

@app.post("/generate_podcast")
def generate_podcast(req: PodcastReq):
    out_name = f"podcast_{uuid.uuid4().hex}.mp3"
    out_path = os.path.join(UPLOAD_DIR, out_name)

    synthesize_podcast(
        script=req.script,
        out_path=out_path,
        provider=TTS_PROVIDER  # "azure"
    )
    return {"audio": f"/files/{out_name}", "transcript": req.script}
