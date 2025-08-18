# backend/app/indexer.py
import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from .semantic import SemanticIndex, UPLOAD_DIR

logger = logging.getLogger(__name__)

# Global index instance
_index = None

def get_index() -> SemanticIndex:
    """Get the global semantic index instance"""
    global _index
    if _index is None:
        _index = SemanticIndex()
        # Scan and ingest any existing PDFs
        _index.scan_and_ingest(UPLOAD_DIR)
    return _index

async def save_pdf(file: UploadFile) -> str:
    """Save uploaded PDF file securely"""
    try:
        # Create safe filename
        safe_filename = _create_safe_filename(file.filename)
        dest_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"✅ PDF saved: {safe_filename}")
        return dest_path
        
    except Exception as e:
        logger.error(f"Error saving PDF {file.filename}: {e}")
        raise

def _create_safe_filename(filename: str) -> str:
    """Create a safe filename for storage"""
    import re
    from datetime import datetime
    
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Add timestamp to prevent conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(safe_name)
    
    return f"{name}_{timestamp}{ext}"

async def upload_and_index(files: List[UploadFile]) -> Dict[str, Any]:
    """Upload PDFs and add them to the semantic index"""
    try:
        saved_files = []
        index = get_index()
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue
            
            # Save file
            file_path = await save_pdf(file)
            filename = os.path.basename(file_path)
            
            # Add to index
            try:
                index.ingest_pdf(file_path, doc_name=filename)
                saved_files.append(filename)
                logger.info(f"✅ Indexed: {filename}")
            except Exception as e:
                logger.error(f"Failed to index {filename}: {e}")
                # Remove failed file
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return {
            "status": "success",
            "uploaded": saved_files,
            "total_files": len(saved_files),
            "index_stats": index.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Error in upload and index: {e}")
        return {
            "status": "error",
            "error": str(e),
            "uploaded": [],
            "total_files": 0
        }

def reindex() -> Dict[str, Any]:
    """Rebuild the entire semantic index"""
    try:
        index = get_index()
        index.clear()
        index.scan_and_ingest(UPLOAD_DIR)
        
        stats = index.get_stats()
        logger.info(f"✅ Reindex complete. Stats: {stats}")
        
        return {
            "status": "success",
            "message": "Index rebuilt successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error reindexing: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_documents() -> Dict[str, Any]:
    """Get list of indexed documents"""
    try:
        index = get_index()
        docs = {}
        
        for meta in index.meta:
            doc_id = meta.doc_id
            if doc_id not in docs:
                docs[doc_id] = {
                    "id": doc_id,
                    "filename": meta.doc_name,
                    "sections": 0,
                    "uploaded_at": "unknown"  # Could be enhanced with file metadata
                }
            docs[doc_id]["sections"] += 1
        
        return {
            "status": "success",
            "documents": list(docs.values()),
            "total_documents": len(docs),
            "total_sections": len(index.meta)
        }
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return {
            "status": "error",
            "error": str(e),
            "documents": [],
            "total_documents": 0,
            "total_sections": 0
        }

def delete_document(doc_id: str) -> Dict[str, Any]:
    """Delete a document and its index entries"""
    try:
        index = get_index()
        
        # Find document metadata
        doc_meta = [m for m in index.meta if m.doc_id == doc_id]
        if not doc_meta:
            return {
                "status": "error",
                "error": "Document not found"
            }
        
        filename = doc_meta[0].doc_name
        
        # Remove from index
        index.meta = [m for m in index.meta if m.doc_id != doc_id]
        
        # Rebuild index without the deleted document
        index.clear()
        index.scan_and_ingest(UPLOAD_DIR)
        
        # Try to remove file
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Deleted file: {filename}")
        
        logger.info(f"✅ Deleted document: {filename} (ID: {doc_id})")
        
        return {
            "status": "success",
            "message": f"Document {filename} deleted successfully",
            "deleted_sections": len(doc_meta)
        }
        
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_index_status() -> Dict[str, Any]:
    """Get comprehensive index status"""
    try:
        index = get_index()
        stats = index.get_stats()
        
        # Get file system info
        upload_files = []
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                if f.lower().endswith('.pdf'):
                    file_path = os.path.join(UPLOAD_DIR, f)
                    upload_files.append({
                        "filename": f,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path)
                    })
        
        return {
            "status": "success",
            "index_stats": stats,
            "upload_directory": UPLOAD_DIR,
            "uploaded_files": upload_files,
            "total_uploaded": len(upload_files),
            "index_healthy": stats.get("total_sections", 0) > 0
        }
        
    except Exception as e:
        logger.error(f"Error getting index status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def cleanup_orphaned_files() -> Dict[str, Any]:
    """Remove PDF files that are not indexed"""
    try:
        index = get_index()
        indexed_files = {m.doc_name for m in index.meta}
        
        orphaned = []
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                if f.lower().endswith('.pdf') and f not in indexed_files:
                    file_path = os.path.join(UPLOAD_DIR, f)
                    os.remove(file_path)
                    orphaned.append(f)
                    logger.info(f"🗑️ Cleaned up orphaned file: {f}")
        
        return {
            "status": "success",
            "cleaned_files": orphaned,
            "total_cleaned": len(orphaned)
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up orphaned files: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
