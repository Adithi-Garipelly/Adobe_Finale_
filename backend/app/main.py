# backend/app/main.py
import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

from .indexer import (
    get_index, upload_and_index, reindex, get_documents, 
    delete_document, get_index_status, cleanup_orphaned_files
)
from .llm_adapter import generate_insights, get_llm_status
from .tts_adapter import (
    generate_podcast_with_transcript, get_tts_status, 
    get_available_voices
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Document Insight & Engagement System",
    description="AI-powered PDF analysis with semantic search, insights generation, and podcast creation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SelectionRequest(BaseModel):
    selected_text: str
    current_doc_name: Optional[str] = None
    top_k: int = 5

class PodcastRequest(BaseModel):
    selected_text: str
    related: List[Dict[str, Any]]
    insights: str
    voice: Optional[str] = "en-US-JennyNeural"
    speaker_mode: Optional[str] = "single"

class TextAnalysisRequest(BaseModel):
    text: str
    top_k: int = 5

# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health and status endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        index = get_index()
        stats = index.get_stats()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "index": {
                "sections": stats.get("total_sections", 0),
                "vectors": stats.get("indexed_vectors", 0),
                "documents": stats.get("documents", 0)
            },
            "services": {
                "llm": get_llm_status(),
                "tts": get_tts_status()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/status")
async def get_status():
    """Get comprehensive system status"""
    try:
        return {
            "status": "operational",
            "timestamp": time.time(),
            "index": get_index_status(),
            "llm": get_llm_status(),
            "tts": get_tts_status(),
            "voices": get_available_voices()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload and management
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and index PDF files"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only PDF files allowed. Received: {file.filename}"
                )
        
        # Upload and index
        result = await upload_and_index(files)
        
        logger.info(f"Upload completed: {len(files)} files processed")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """Get list of all indexed documents"""
    try:
        docs = get_documents()
        return {
            "status": "success",
            "documents": docs,
            "count": len(docs)
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_name}")
async def remove_document(doc_name: str):
    """Delete a document and its index entries"""
    try:
        result = delete_document(doc_name)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {doc_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Index management
@app.post("/reindex")
async def rebuild_index():
    """Rebuild the entire semantic index"""
    try:
        result = reindex()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("Index rebuild completed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup")
async def cleanup_files():
    """Clean up orphaned files"""
    try:
        result = cleanup_orphaned_files()
        return result
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Text analysis and insights
@app.post("/selection/analyze")
async def analyze_selection(request: SelectionRequest):
    """Analyze selected text and find related sections"""
    try:
        if not request.selected_text.strip():
            raise HTTPException(status_code=400, detail="Selected text cannot be empty")
        
        # Get semantic index
        index = get_index()
        
        # Search for related sections
        related = index.search(request.selected_text, top_k=request.top_k)
        
        # Generate insights
        insights = generate_insights(request.selected_text, related)
        
        logger.info(f"Analysis completed: {len(related)} related sections found")
        
        return {
            "status": "success",
            "selected_text": request.selected_text,
            "current_doc_name": request.current_doc_name,
            "related": related,
            "insights": insights,
            "analysis_timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text/analyze")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze arbitrary text input (for testing)"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get semantic index
        index = get_index()
        
        # Search for related sections
        related = index.search(request.text, top_k=request.top_k)
        
        # Generate insights
        insights = generate_insights(request.text, related)
        
        return {
            "status": "success",
            "input_text": request.text,
            "related": related,
            "insights": insights,
            "analysis_timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Podcast generation
@app.post("/podcast/generate")
async def generate_podcast(request: PodcastRequest):
    """Generate podcast audio and transcript"""
    try:
        if not request.selected_text.strip():
            raise HTTPException(status_code=400, detail="Selected text cannot be empty")
        
        if not request.related:
            raise HTTPException(status_code=400, detail="No related sections provided")
        
        if not request.insights.strip():
            raise HTTPException(status_code=400, detail="No insights provided")
        
        # Generate podcast
        result = generate_podcast_with_transcript(
            selected_text=request.selected_text,
            related=request.related,
            insights=request.insights,
            voice=request.voice,
            speaker_mode=request.speaker_mode
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"Podcast generated successfully: {result['filename']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Podcast generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File serving
@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve audio files"""
    try:
        file_path = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Determine media type
        if filename.endswith('.mp3'):
            media_type = "audio/mpeg"
        elif filename.endswith('.txt'):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(file_path, media_type=media_type)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploads/{filename}")
async def serve_pdf(filename: str):
    """Serve uploaded PDF files"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(file_path, media_type="application/pdf")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving PDF file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Debug and development endpoints
@app.get("/debug/index")
async def debug_index():
    """Debug endpoint for index information"""
    try:
        index = get_index()
        return {
            "index_stats": index.get_stats(),
            "sample_sections": index.meta[:5] if index.meta else [],
            "upload_dir_contents": os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
        }
    except Exception as e:
        logger.error(f"Debug index failed: {e}")
        return {"error": str(e)}

@app.get("/debug/search/{query}")
async def debug_search(query: str, top_k: int = 3):
    """Debug endpoint for search testing"""
    try:
        index = get_index()
        results = index.search(query, top_k=top_k)
        return {
            "query": query,
            "results": results,
            "result_count": len(results)
        }
    except Exception as e:
        logger.error(f"Debug search failed: {e}")
        return {"error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Document Insight & Engagement System",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "upload": "/upload",
            "documents": "/documents",
            "analyze": "/selection/analyze",
            "podcast": "/podcast/generate",
            "docs": "/docs"
        },
        "features": [
            "Semantic PDF search with FAISS",
            "AI-powered insights generation",
            "Azure TTS podcast creation",
            "Multi-document analysis",
            "Competition-ready architecture"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "path": str(request.url.path),
            "message": "The requested resource was not found"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": str(request.url.path),
            "message": "An unexpected error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    try:
        logger.info("🚀 Starting Document Insight & Engagement System...")
        
        # Initialize index
        index = get_index()
        stats = index.get_stats()
        
        logger.info(f"✅ System initialized successfully!")
        logger.info(f"   📚 Indexed sections: {stats.get('total_sections', 0)}")
        logger.info(f"   📄 Documents: {stats.get('documents', 0)}")
        logger.info(f"   🧠 Model: {stats.get('model_name', 'Unknown')}")
        logger.info(f"   📁 Data directory: {DATA_DIR}")
        
    except Exception as e:
        logger.error(f"❌ System startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Document Insight & Engagement System...")
