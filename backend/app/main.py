import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pydantic import BaseModel

# Load environment variables from .env file
from dotenv import load_dotenv
import os

# Load .env from the backend directory (current working directory when running uvicorn)
load_dotenv()

from .search_index import DocIndex
from .insights import build_insights_payload, generate_insights_from_selection
from .tts import synthesize_podcast
from .llm_adapter import gemini_complete

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
_index = None

def get_index():
    global _index
    if _index is None:
        _index = DocIndex(storage_dir=UPLOAD_DIR)
    return _index

# ---------- MODELS ----------
class AnalyzeSelectionReq(BaseModel):
    current_pdf: str
    selected_text: str
    max_sections: int = 5

class PodcastReq(BaseModel):
    script: str
    speaker_mode: str = "duo"  # "duo" or "single"

class ChatQuery(BaseModel):
    question: str
    pdf_name: str

# ---------- ROUTES ----------
@app.get("/health")
def health():
    return {"status": "ok", "pdf_count": len(get_index().documents)}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(..., alias="files")):
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

    # Return immediately, index in background
    import asyncio
    asyncio.create_task(index_pdfs_async(saved))
    
    return {"files": saved, "message": "Files uploaded successfully. Indexing in background..."}

async def index_pdfs_async(saved_files: List[str]):
    """Index PDFs asynchronously without blocking the upload response"""
    try:
        paths = [os.path.join(UPLOAD_DIR, s) for s in saved_files]
        get_index().add_pdfs(paths)
        print(f"✅ Indexed {len(saved_files)} PDFs in background")
    except Exception as e:
        print(f"❌ Background indexing failed: {e}")

@app.get("/files")
def list_files():
    return {"files": sorted(get_index().list_pdf_names())}

@app.get("/files/{filename}")
def get_file(filename: str):
    safe = filename.replace("/", "_")
    path = os.path.join(UPLOAD_DIR, safe)
    if not os.path.isfile(path):
        raise HTTPException(404, "File not found.")
    
    # Determine correct media type based on file extension
    if filename.lower().endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.lower().endswith('.mp3'):
        media_type = "audio/mpeg"
    elif filename.lower().endswith('.wav'):
        media_type = "audio/wav"
    else:
        media_type = "application/octet-stream"
    
    # Ensure CORS works: FastAPI static file response
    return FileResponse(path, media_type=media_type, filename=safe)



@app.post("/analyze_selection")
def analyze_selection(req: AnalyzeSelectionReq):
    # 1) semantic search for relevant sections (excluding current_pdf if you want)
    results = get_index().search_sections(req.selected_text, top_k=req.max_sections, exclude_pdf=req.current_pdf)

    # 2) pick 2–4 sentence snippets per section
    snippets = get_index().make_snippets(results)

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

# ---------- NEW CHAT ENDPOINTS ----------
@app.post("/chat/ask")
async def ask_pdf(query: ChatQuery):
    """Ask a question about a specific PDF using Gemini"""
    try:
        # Get the PDF content for context
        pdf_path = os.path.join(UPLOAD_DIR, query.pdf_name.replace("/", "_"))
        if not os.path.exists(pdf_path):
            raise HTTPException(404, "PDF not found")
        
        # Use our existing Gemini integration
        system_prompt = f"""You are a helpful assistant answering questions about a PDF document. 
        Answer based ONLY on the content of the PDF: {query.pdf_name}
        Be concise, accurate, and helpful. If the question cannot be answered from the PDF content, say so."""
        
        user_prompt = f"Question: {query.question}\n\nPlease answer based on the PDF content."
        
        answer = gemini_complete(system_prompt=system_prompt, user_prompt=user_prompt)
        
        return {"answer": answer, "pdf_name": query.pdf_name, "question": query.question}
        
    except Exception as e:
        raise HTTPException(500, f"Error processing question: {str(e)}")

@app.post("/chat/speak")
async def speak_answer(text: str = Form(...)):
    """Convert text answer to speech using Azure TTS"""
    try:
        out_name = f"chat_answer_{uuid.uuid4().hex}.mp3"
        out_path = os.path.join(UPLOAD_DIR, out_name)
        
        synthesize_podcast(
            script=text,
            out_path=out_path,
            provider=TTS_PROVIDER
        )
        
        return {"audio": f"/files/{out_name}", "text": text}
        
    except Exception as e:
        raise HTTPException(500, f"Error generating speech: {str(e)}")

# ---------- TTS STATUS ROUTE ----------
@app.get("/tts/status")
def get_tts_status():
    """Get TTS configuration status for debugging"""
    from .tts import tts_status
    return tts_status()

# ---------- STATIC FILES ----------
# Mount frontend build files AFTER all API routes to avoid conflicts
if os.path.exists("frontend-build"):
    app.mount("/", StaticFiles(directory="frontend-build", html=True), name="static")
