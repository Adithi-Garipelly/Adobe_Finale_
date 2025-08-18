# backend/app/indexer.py
import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from .semantic import SemanticIndex, UPLOAD_DIR
import re
from datetime import datetime
import numpy as np
import faiss

logger = logging.getLogger(__name__)

# Global index instance
_index: Optional[SemanticIndex] = None

def get_index() -> SemanticIndex:
    """Get or create the global semantic index instance"""
    global _index
    if _index is None:
        try:
            _index = SemanticIndex()
            # Scan and ingest existing PDFs
            scan_result = _index.scan_and_ingest(UPLOAD_DIR)
            logger.info(f"Index initialized: {scan_result}")
        except Exception as e:
            logger.error(f"Failed to initialize index: {e}")
            raise
    return _index

async def save_pdf(file: UploadFile) -> str:
    """Save uploaded PDF file to upload directory"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF files allowed. Received: {file.filename}"
            )
        
        # Validate file size (max 50MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size: 50MB"
            )
        
        # Create safe filename
        safe_filename = _create_safe_filename(file.filename)
        dest_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"PDF saved: {safe_filename} ({file_size} bytes)")
        return dest_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving PDF {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

def _create_safe_filename(filename: str) -> str:
    """Create a safe filename by removing special characters"""
    
    # Remove special characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Add timestamp if filename already exists
    base_name, ext = os.path.splitext(safe_name)
    counter = 1
    final_name = safe_name
    
    while os.path.exists(os.path.join(UPLOAD_DIR, final_name)):
        final_name = f"{base_name}_{counter}{ext}"
        counter += 1
    
    return final_name

async def upload_and_index(files: List[UploadFile]) -> Dict[str, Any]:
    """Upload PDFs and index them"""
    try:
        saved_files = []
        indexing_results = []
        
        for file in files:
            # Save file
            file_path = await save_pdf(file)
            saved_files.append(os.path.basename(file_path))
            
            # Index the PDF
            index = get_index()
            result = index.ingest_pdf(file_path)
            indexing_results.append(result)
        
        # Get index statistics
        index = get_index()
        stats = index.get_stats()
        
        return {
            "status": "success",
            "uploaded": saved_files,
            "indexing_results": indexing_results,
            "index_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error in upload_and_index: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload and indexing failed: {str(e)}"
        )

def reindex() -> Dict[str, Any]:
    """Rebuild the entire index from uploaded PDFs"""
    try:
        index = get_index()
        
        # Clear existing index
        index.clear()
        
        # Rebuild from uploads
        result = index.scan_and_ingest(UPLOAD_DIR)
        
        # Get new stats
        stats = index.get_stats()
        
        logger.info(f"Reindex completed: {result}")
        
        return {
            "status": "success",
            "reindex_result": result,
            "index_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error during reindex: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_documents() -> List[Dict[str, Any]]:
    """Get list of all indexed documents"""
    try:
        index = get_index()
        
        # Group sections by document
        docs = {}
        for section in index.meta:
            doc_id = section.doc_id
            if doc_id not in docs:
                docs[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": section.doc_name,
                    "sections": [],
                    "total_sections": 0,
                    "total_words": 0
                }
            
            docs[doc_id]["sections"].append({
                "heading": section.heading,
                "word_count": section.word_count,
                "created_at": section.created_at
            })
            docs[doc_id]["total_sections"] += 1
            docs[doc_id]["total_words"] += section.word_count
        
        # Convert to list and sort by name
        doc_list = list(docs.values())
        doc_list.sort(key=lambda x: x["doc_name"])
        
        return doc_list
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return []

def delete_document(doc_name: str) -> Dict[str, Any]:
    """Delete a document and its sections from the index"""
    try:
        index = get_index()
        
        # Find sections to remove
        sections_to_remove = [i for i, section in enumerate(index.meta) 
                            if section.doc_name == doc_name]
        
        if not sections_to_remove:
            return {
                "status": "error",
                "error": f"Document '{doc_name}' not found in index"
            }
        
        # Remove sections (in reverse order to maintain indices)
        for i in reversed(sections_to_remove):
            del index.meta[i]
        
        # Rebuild FAISS index
        if index.meta:
            # Extract remaining embeddings
            remaining_embeddings = []
            for section in index.meta:
                try:
                    embedding = index.model.encode(section.content, normalize_embeddings=True)
                    remaining_embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Error encoding section {section.id}: {e}")
                    continue
            
            if remaining_embeddings:
                # Create new index with remaining embeddings
                new_embeddings = np.vstack(remaining_embeddings).astype("float32")
                index.index = faiss.IndexFlatIP(index.dim)
                index.index.add(new_embeddings)
            else:
                # No valid embeddings left
                index.index = faiss.IndexFlatIP(index.dim)
        else:
            # No sections left
            index.index = faiss.IndexFlatIP(index.dim)
        
        # Save updated index
        index._save()
        
        # Remove PDF file if it exists
        pdf_path = os.path.join(UPLOAD_DIR, doc_name)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"PDF file removed: {pdf_path}")
        
        logger.info(f"Document '{doc_name}' deleted successfully")
        
        return {
            "status": "success",
            "deleted_document": doc_name,
            "sections_removed": len(sections_to_remove),
            "remaining_sections": len(index.meta)
        }
        
    except Exception as e:
        logger.error(f"Error deleting document '{doc_name}': {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_index_status() -> Dict[str, Any]:
    """Get comprehensive index status"""
    try:
        index = get_index()
        stats = index.get_stats()
        docs = get_documents()
        
        return {
            "status": "healthy",
            "index_stats": stats,
            "documents": docs,
            "upload_directory": UPLOAD_DIR,
            "index_directory": index.index_dir,
            "model_info": {
                "name": index.model_name,
                "dimension": index.dim
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting index status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def cleanup_orphaned_files() -> Dict[str, Any]:
    """Remove PDF files that are no longer indexed"""
    try:
        index = get_index()
        
        # Get indexed document names
        indexed_docs = {section.doc_name for section in index.meta}
        
        # Get all PDF files in upload directory
        pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.pdf')]
        
        # Find orphaned files
        orphaned = [f for f in pdf_files if f not in indexed_docs]
        
        # Remove orphaned files
        removed_count = 0
        for orphan in orphaned:
            try:
                os.remove(os.path.join(UPLOAD_DIR, orphan))
                removed_count += 1
                logger.info(f"Removed orphaned file: {orphan}")
            except Exception as e:
                logger.error(f"Error removing orphaned file {orphan}: {e}")
        
        return {
            "status": "success",
            "orphaned_files_found": len(orphaned),
            "files_removed": removed_count,
            "remaining_files": len(pdf_files) - removed_count
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
