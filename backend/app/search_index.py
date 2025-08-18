import logging
import re
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Try to import FAISS and sentence-transformers
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
    logger.info("🚀 FAISS and sentence-transformers available - using semantic search")
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("⚠️ FAISS or sentence-transformers not available - falling back to keyword search")

class SearchIndex:
    """Advanced search index with FAISS vector embeddings for semantic search"""
    
    def __init__(self):
        self.documents = {}  # doc_id -> document info
        self.text_index = {}  # word -> list of doc_ids (fallback)
        
        # FAISS components
        if FAISS_AVAILABLE:
            try:
                # Use a lightweight but effective model
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.dimension = self.embedding_model.get_sentence_embedding_dimension()
                
                # Initialize FAISS index
                self.faiss_index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                self.document_embeddings = []  # List of (doc_id, embedding) tuples
                self.embedding_to_doc_id = []  # Mapping from FAISS index to doc_id
                
                # New for semantic chunking
                self.chunk_embeddings = {}
                self.chunk_metadata = {}
                
                logger.info(f"🔍 FAISS index initialized with dimension {self.dimension}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize FAISS: {e}")
                # Don't change FAISS_AVAILABLE here, just disable for this instance
                self.embedding_model = None
                self.faiss_index = None
        else:
            self.embedding_model = None
            self.faiss_index = None
        
        logger.info("🔍 Search index initialized")
    
    def add_document(self, doc_id: str, filename: str, text_content: str):
        """Add a document to the search index with improved chunking"""
        try:
            logger.info(f"Indexing document: {filename} (ID: {doc_id})")
            
            # Improved chunking strategy: split by paragraphs and meaningful sections
            chunks = self._create_semantic_chunks(text_content)
            
            # Store document metadata
            self.documents[doc_id] = {
                "filename": filename,
                "text": text_content,
                "length": len(text_content),
                "chunks": chunks,
                "uploaded_at": datetime.now().isoformat()
            }
            
            # Add chunks to search index
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_text = chunk["text"]
                
                # Generate embedding for the chunk
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode([chunk_text])[0]
                        self.chunk_embeddings[chunk_id] = embedding
                        self.chunk_metadata[chunk_id] = {
                            "doc_id": doc_id,
                            "filename": filename,
                            "chunk_index": i,
                            "text": chunk_text,
                            "section": chunk.get("section", "Unknown"),
                            "page": chunk.get("page", "Unknown")
                        }
                    except Exception as e:
                        logger.warning(f"Failed to generate embedding for chunk {i}: {e}")
                        # Store chunk without embedding for fallback search
                        self.chunk_metadata[chunk_id] = {
                            "doc_id": doc_id,
                            "filename": filename,
                            "chunk_index": i,
                            "text": chunk_text,
                            "section": chunk.get("section", "Unknown"),
                            "page": chunk.get("page", "Unknown")
                        }
                else:
                    # Fallback: store chunk metadata without embedding
                    self.chunk_metadata[chunk_id] = {
                        "doc_id": doc_id,
                        "filename": filename,
                        "chunk_index": i,
                        "text": chunk_text,
                        "section": chunk.get("section", "Unknown"),
                        "page": chunk.get("page", "Unknown")
                    }
            
            logger.info(f"✅ Document indexed successfully: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing document {filename}: {e}")
            raise
    
    def _create_semantic_chunks(self, text_content: str) -> List[Dict[str, Any]]:
        """Create semantic chunks from text content"""
        try:
            # Split text into paragraphs
            paragraphs = text_content.split('\n\n')
            chunks = []
            current_chunk = ""
            current_section = "Introduction"
            
            for paragraph in paragraphs:
                paragraph = self._clean_paragraph(paragraph)
                if not paragraph:
                    continue
                
                # Check if this paragraph is a section header
                if self._is_section_header(paragraph):
                    current_section = self._extract_section_name(paragraph)
                    # Start a new chunk for section headers
                    if current_chunk.strip():
                        chunks.append({
                            "text": current_chunk.strip(),
                            "section": current_section,
                            "page": "Unknown"
                        })
                        current_chunk = ""
                
                # Add paragraph to current chunk
                current_chunk += paragraph + "\n\n"
                
                # If chunk is getting too long, save it and start new one
                if len(current_chunk) > 1000:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "section": current_section,
                        "page": "Unknown"
                    })
                    current_chunk = ""
            
            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "section": current_section,
                    "page": "Unknown"
                })
            
            logger.info(f"Created {len(chunks)} semantic chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating semantic chunks: {e}")
            # Fallback: return the entire text as one chunk
            return [{"text": text_content, "section": "Unknown", "page": "Unknown"}]
    
    def _clean_paragraph(self, paragraph: str) -> str:
        """Clean individual paragraph text"""
        try:
            # Remove leading/trailing whitespace
            paragraph = paragraph.strip()
            
            # Skip very short paragraphs (likely noise)
            if len(paragraph) < 20:
                return ""
            
            # Remove paragraph if it's mostly numbers or special characters
            if len(re.findall(r'[a-zA-Z]', paragraph)) < len(paragraph) * 0.3:
                return ""
            
            # Fix broken sentences
            paragraph = re.sub(r'\s+([a-z])', r' \1', paragraph)  # Fix spacing before lowercase
            
            # Normalize spacing
            paragraph = re.sub(r'\s+', ' ', paragraph)
            
            return paragraph
            
        except Exception as e:
            logger.warning(f"Error cleaning paragraph: {e}")
            return paragraph
    
    def _extract_section_name(self, header_text: str) -> str:
        """Extract clean section name from header text"""
        try:
            # Remove numbering and clean up
            clean_header = re.sub(r'^\d+\.?\s*', '', header_text.strip())
            clean_header = re.sub(r'^[A-Z\s]+$', lambda m: m.group(0).title(), clean_header)
            
            # Limit length
            if len(clean_header) > 100:
                clean_header = clean_header[:97] + "..."
            
            return clean_header or "Unknown Section"
            
        except Exception as e:
            logger.warning(f"Error extracting section name: {e}")
            return "Unknown Section"
    
    def _is_section_header(self, text: str) -> bool:
        """Check if text looks like a section header"""
        # Common patterns for section headers
        header_patterns = [
            r'^\d+\.\s+[A-Z]',  # 1. Title
            r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS TITLE
            r'^[A-Z][a-z\s]{3,}$',  # Title Case Title
            r'^Chapter\s+\d+',  # Chapter X
            r'^Section\s+\d+',  # Section X
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks using improved semantic similarity and query processing"""
        try:
            logger.info(f"🔍 Searching for: {query[:100]}...")
            
            if not self.chunk_metadata:
                logger.warning("No chunks available for search")
                return []
            
            # Clean and preprocess the query
            cleaned_query = self._clean_query(query)
            logger.info(f"Cleaned query: {cleaned_query[:100]}...")
            
            # Generate query embedding if model is available
            query_embedding = None
            if self.embedding_model:
                try:
                    query_embedding = self.embedding_model.encode([cleaned_query])[0]
                    logger.info("✅ Query embedding generated")
                except Exception as e:
                    logger.warning(f"Failed to generate query embedding: {e}")
            
            # Score chunks based on multiple criteria
            scored_chunks = []
            
            for chunk_id, metadata in self.chunk_metadata.items():
                score = 0.0
                scoring_details = {}
                
                # 1. Semantic similarity (if embeddings available)
                if query_embedding is not None and chunk_id in self.chunk_embeddings:
                    chunk_embedding = self.chunk_embeddings[chunk_id]
                    semantic_score = self._cosine_similarity(query_embedding, chunk_embedding)
                    score += semantic_score * 0.6  # Weight: 60%
                    scoring_details["semantic"] = semantic_score
                    logger.debug(f"Semantic score for {chunk_id}: {semantic_score:.4f}")
                
                # 2. Keyword matching
                keyword_score = self._keyword_similarity(cleaned_query, metadata["text"])
                score += keyword_score * 0.3  # Weight: 30%
                scoring_details["keyword"] = keyword_score
                
                # 3. Section header relevance boost
                if any(term.lower() in metadata["section"].lower() for term in cleaned_query.split()):
                    section_boost = 0.2
                    score += section_boost
                    scoring_details["section_boost"] = section_boost
                    logger.debug(f"Section header boost for {chunk_id}")
                
                # 4. Content quality boost (longer, more meaningful chunks get slight boost)
                if metadata.get("word_count", 0) > 100:
                    quality_boost = min(0.1, metadata.get("word_count", 0) / 1000)
                    score += quality_boost
                    scoring_details["quality_boost"] = quality_boost
                
                # 5. Penalize very short or noisy chunks
                if metadata.get("word_count", 0) < 50:
                    score *= 0.5
                    scoring_details["length_penalty"] = 0.5
                
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "metadata": metadata,
                    "score": score,
                    "scoring_details": scoring_details
                })
            
            # Sort by score (highest first)
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            
            # Apply diversity filtering and deduplication
            unique_results = self._diversify_and_deduplicate_chunks(scored_chunks, max_results)
            
            # Format results with better information
            results = []
            for chunk_data in unique_results:
                metadata = chunk_data["metadata"]
                results.append({
                    "id": chunk_data["chunk_id"],
                    "filename": metadata["filename"],
                    "content_preview": self._create_content_preview(metadata["text"], cleaned_query),
                    "section": metadata["section"],
                    "chunk_index": metadata["chunk_index"],
                    "score": chunk_data["score"],
                    "full_text": metadata["text"],
                    "word_count": metadata.get("word_count", 0),
                    "relevance_reason": self._explain_relevance(cleaned_query, metadata, chunk_data["scoring_details"])
                })
            
            logger.info(f"✅ Search completed: {len(results)} results found")
            return results
        
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def _clean_query(self, query: str) -> str:
        """Clean and preprocess the search query"""
        try:
            # Remove extra whitespace and normalize
            cleaned = re.sub(r'\s+', ' ', query.strip())
            
            # Remove common stop words that don't add meaning
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = cleaned.split()
            meaningful_words = [word for word in words if word.lower() not in stop_words or len(word) > 2]
            
            cleaned_query = ' '.join(meaningful_words)
            
            # If query is too short after cleaning, use original
            if len(cleaned_query.split()) < 2:
                cleaned_query = query.strip()
            
            return cleaned_query
            
        except Exception as e:
            logger.warning(f"Error cleaning query: {e}")
            return query.strip()
    
    def _create_content_preview(self, text: str, query: str) -> str:
        """Create a smart content preview that highlights relevant parts"""
        try:
            # Find the most relevant part of the text
            query_terms = query.lower().split()
            sentences = text.split('. ')
            
            # Score each sentence based on query term presence
            scored_sentences = []
            for sentence in sentences:
                score = sum(1 for term in query_terms if term.lower() in sentence.lower())
                if score > 0:
                    scored_sentences.append((sentence, score))
            
            # Sort by relevance score
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            
            if scored_sentences:
                # Use the most relevant sentence as preview
                best_sentence = scored_sentences[0][0]
                if len(best_sentence) > 300:
                    best_sentence = best_sentence[:297] + "..."
                return best_sentence
            else:
                # Fallback to first part of text
                return text[:300] + "..." if len(text) > 300 else text
                
        except Exception as e:
            logger.warning(f"Error creating content preview: {e}")
            return text[:300] + "..." if len(text) > 300 else text
    
    def _explain_relevance(self, query: str, metadata: Dict, scoring_details: Dict) -> str:
        """Explain why this chunk is relevant to the query"""
        try:
            reasons = []
            
            if "semantic" in scoring_details:
                semantic_score = scoring_details["semantic"]
                if semantic_score > 0.7:
                    reasons.append("High semantic similarity")
                elif semantic_score > 0.5:
                    reasons.append("Good semantic match")
                else:
                    reasons.append("Some semantic relevance")
            
            if "keyword" in scoring_details:
                keyword_score = scoring_details["keyword"]
                if keyword_score > 0.5:
                    reasons.append("Strong keyword match")
                elif keyword_score > 0.2:
                    reasons.append("Keyword overlap")
            
            if "section_boost" in scoring_details:
                reasons.append("Relevant section header")
            
            if metadata.get("word_count", 0) > 100:
                reasons.append("Substantial content")
            
            return "; ".join(reasons) if reasons else "General relevance"
            
        except Exception as e:
            logger.warning(f"Error explaining relevance: {e}")
            return "Relevant content"
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.warning(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _keyword_similarity(self, query: str, text: str) -> float:
        """Calculate keyword-based similarity between query and text"""
        try:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            
            if not query_words:
                return 0.0
            
            intersection = query_words.intersection(text_words)
            union = query_words.union(text_words)
            
            if not union:
                return 0.0
            
            return len(intersection) / len(union)
        except Exception as e:
            logger.warning(f"Error calculating keyword similarity: {e}")
            return 0.0
    
    def _diversify_and_deduplicate_chunks(self, scored_chunks: List[Dict], max_results: int) -> List[Dict]:
        """Apply diversity filtering and deduplication to search results"""
        try:
            if not scored_chunks:
                return []
            
            # Remove exact duplicates based on text content
            seen_texts = set()
            unique_chunks = []
            
            for chunk in scored_chunks:
                text_hash = hash(chunk["metadata"]["text"][:100])  # Use first 100 chars as hash
                if text_hash not in seen_texts:
                    seen_texts.add(text_hash)
                    unique_chunks.append(chunk)
            
            # Apply diversity filtering (ensure different documents are represented)
            diverse_results = []
            seen_docs = set()
            
            for chunk in unique_chunks[:max_results * 2]:  # Look at more candidates for diversity
                doc_id = chunk["metadata"]["doc_id"]
                
                # Allow up to 2 chunks per document for diversity
                if doc_id not in seen_docs or len([r for r in diverse_results if r["metadata"]["doc_id"] == doc_id]) < 2:
                    diverse_results.append(chunk)
                    seen_docs.add(doc_id)
                
                if len(diverse_results) >= max_results:
                    break
            
            return diverse_results[:max_results]
            
        except Exception as e:
            logger.warning(f"Error in diversity filtering: {e}")
            return scored_chunks[:max_results]
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all indexed documents"""
        try:
            return [
                {
                    "id": doc_id,
                    "filename": doc_data["filename"],
                    "length": doc_data["length"],
                    "uploaded_at": doc_data["uploaded_at"],
                    "chunk_count": len(doc_data["chunks"])
                }
                for doc_id, doc_data in self.documents.items()
            ]
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document and all its chunks from the index"""
        try:
            if doc_id in self.documents:
                # Remove from documents dict
                removed_doc = self.documents.pop(doc_id)
                logger.info(f"✅ Removed document from index: {removed_doc['filename']}")
                
                # Also remove related chunks
                chunks_to_remove = []
                for chunk_id in list(self.chunk_metadata.keys()):
                    if self.chunk_metadata[chunk_id]["doc_id"] == doc_id:
                        chunks_to_remove.append(chunk_id)
                
                for chunk_id in chunks_to_remove:
                    if chunk_id in self.chunk_metadata:
                        del self.chunk_metadata[chunk_id]
                    if chunk_id in self.chunk_embeddings:
                        del self.chunk_embeddings[chunk_id]
                
                logger.info(f"🗑️ Removed {len(chunks_to_remove)} related chunks")
                
                return True
            else:
                logger.warning(f"⚠️ Document ID not found in index: {doc_id}")
                logger.warning(f"📚 Available documents: {list(self.documents.keys())}")
                return False
        except Exception as e:
            logger.error(f"❌ Error removing document {doc_id}: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        return self.documents.get(doc_id, {})
    
    def stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        stats = {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunk_metadata),
            "index_size": len(self.documents)
        }
        
        if FAISS_AVAILABLE and hasattr(self, 'faiss_index') and self.faiss_index is not None:
            stats["faiss_available"] = True
            stats["embedding_dimension"] = getattr(self, 'dimension', 'N/A')
            stats["faiss_index_size"] = self.faiss_index.ntotal if hasattr(self.faiss_index, 'ntotal') else 0
        else:
            stats["faiss_available"] = False
        
        return stats

    def clear_index(self):
        """Clear all indexed data and start fresh"""
        try:
            logger.info("🧹 Clearing search index...")
            
            # Clear all data structures
            self.documents.clear()
            self.chunk_embeddings.clear()
            self.chunk_metadata.clear()
            
            # Reset FAISS index if available
            if hasattr(self, 'faiss_index') and self.faiss_index is not None:
                self.faiss_index.reset()
                logger.info("✅ FAISS index cleared")
            
            logger.info("✅ Search index cleared successfully")
        
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
    
    def reindex_documents(self):
        """Re-index all existing documents with the new chunk-based system"""
        try:
            logger.info("🔄 Re-indexing all documents with new chunk-based system...")
            
            # Store current documents temporarily
            temp_docs = self.documents.copy()
            
            # Clear the index
            self.clear_index()
            
            # Re-index each document
            for doc_id, doc_data in temp_docs.items():
                try:
                    # Extract text content (handle both old and new formats)
                    text_content = doc_data.get('text', doc_data.get('content', ''))
                    if text_content:
                        self.add_document(doc_id, doc_data['filename'], text_content)
                        logger.info(f"✅ Re-indexed: {doc_data['filename']}")
                    else:
                        logger.warning(f"⚠️ No text content found for: {doc_data['filename']}")
                except Exception as e:
                    logger.error(f"❌ Failed to re-index {doc_data['filename']}: {e}")
            
            logger.info(f"✅ Re-indexing completed: {len(temp_docs)} documents processed")
            
        except Exception as e:
            logger.error(f"Error during re-indexing: {e}")
            raise
