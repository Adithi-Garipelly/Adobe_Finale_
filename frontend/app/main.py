# backend/app/main.py
import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from .indexer import (
    upload_and_index, get_documents, delete_document, 
    reindex, get_index_status, cleanup_orphaned_files
)
from .llm_adapter import generate_insights
from .tts_adapter import generate_podcast_with_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Document Insight & Engagement System",
    description="AI-powered PDF analysis with semantic search and podcast generation",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directories
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

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

# Health and status endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from .indexer import get_index
        index = get_index()
        stats = index.get_stats()
        return {
            "status": "healthy",
            "service": "Document Insight & Engagement System",
            "version": "2.0.0",
            "index_stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/status")
async def get_status():
    """Get comprehensive system status"""
    try:
        from .llm_adapter import get_llm_status
        from .tts_adapter import get_tts_status
        
        return {
            "status": "success",
            "system": {
                "name": "Document Insight & Engagement System",
                "version": "2.0.0",
                "backend": "FastAPI",
                "frontend": "React + Adobe Embed API"
            },
            "llm": get_llm_status(),
            "tts": get_tts_status(),
            "index": get_index_status()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# File management endpoints
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files and add them to the semantic index"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only PDF files allowed. Got: {file.filename}"
                )
        
        # Upload and index files
        result = await upload_and_index(files)
        
        if result["status"] == "success":
            logger.info(f"✅ Upload successful: {result['total_files']} files")
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """Get list of indexed documents"""
    try:
        result = get_documents()
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get documents"))
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_id}")
async def remove_document(doc_id: str):
    """Delete a document and its index entries"""
    try:
        result = delete_document(doc_id)
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Document not found"))
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analysis endpoints
@app.post("/selection/analyze")
async def analyze_selection(request: SelectionRequest):
    """Analyze selected text and generate insights"""
    try:
        from .indexer import get_index
        
        # Get semantic index
        index = get_index()
        
        # Search for related sections
        related = index.search(request.selected_text, top_k=request.top_k)
        
        # Generate insights
        insights = generate_insights(request.selected_text, related)
        
        # Format response
        response = {
            "status": "success",
            "selected_text": request.selected_text,
            "current_doc_name": request.current_doc_name,
            "related_sections": related,
            "insights": insights,
            "generated_at": "now"  # Could be enhanced with actual timestamp
        }
        
        logger.info(f"✅ Insights generated for text: {request.selected_text[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text/analyze")
async def analyze_text(request: SelectionRequest):
    """Analyze text input (alternative to selection)"""
    return await analyze_selection(request)

# Podcast generation endpoints
@app.post("/podcast/generate")
async def generate_podcast(request: PodcastRequest):
    """Generate podcast from insights"""
    try:
        # Generate podcast with transcript
        result = generate_podcast_with_transcript(
            selected_text=request.selected_text,
            related=request.related,
            insights=request.insights,
            voice=request.voice,
            speaker_mode=request.speaker_mode
        )
        
        if result["status"] == "success":
            logger.info(f"✅ Podcast generated: {result['filename']}")
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Podcast generation failed"))
            
    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File serving endpoints
@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded PDF files"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files"""
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

# Management endpoints
@app.post("/reindex")
async def rebuild_index():
    """Rebuild the entire semantic index"""
    try:
        result = reindex()
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Reindex failed"))
    except Exception as e:
        logger.error(f"Error reindexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup")
async def cleanup_files():
    """Clean up orphaned files"""
    try:
        result = cleanup_orphaned_files()
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Cleanup failed"))
    except Exception as e:
        logger.error(f"Error cleaning up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Debug endpoints
@app.get("/debug/index")
async def debug_index():
    """Debug endpoint to inspect index state"""
    try:
        from .indexer import get_index
        index = get_index()
        return {
            "status": "success",
            "index_stats": index.get_stats(),
            "meta_count": len(index.meta),
            "index_ntotal": index.index.ntotal if index.index else 0
        }
    except Exception as e:
        logger.error(f"Debug index error: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/debug/search/{query}")
async def debug_search(query: str):
    """Debug endpoint to test search functionality"""
    try:
        from .indexer import get_index
        index = get_index()
        results = index.search(query, top_k=3)
        return {
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results)
        }
    except Exception as e:
        logger.error(f"Debug search error: {e}")
        return {"status": "error", "error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Document Insight & Engagement System",
        "version": "2.0.0",
        "description": "AI-powered PDF analysis with semantic search and podcast generation",
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
            "Universal PDF processing",
            "Semantic search with FAISS",
            "AI-powered insights generation",
            "Professional podcast creation",
            "Adobe Embed API integration"
        ]
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("🚀 Starting Document Insight & Engagement System...")
    
    # Ensure data directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # Initialize semantic index
    try:
        from .indexer import get_index
        index = get_index()
        stats = index.get_stats()
        logger.info(f"✅ Index initialized: {stats['total_sections']} sections from {stats['documents']} documents")
    except Exception as e:
        logger.error(f"❌ Failed to initialize index: {e}")
    
    logger.info("✅ System startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Document Insight & Engagement System...")
    # Add any cleanup logic here
    logger.info("✅ System shutdown complete")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )
