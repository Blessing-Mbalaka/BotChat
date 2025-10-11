import os
import yaml
import PyPDF2
import docx
from pathlib import Path
import logging
import json
import re

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval-Augmented Generation service for health documents"""
    
    def __init__(self):
        self.config = self.load_config()
        self.documents = {}  # Simple in-memory storage
        self.load_documents()
    
    def load_config(self):
        """Load RAG configuration from YAML"""
        try:
            with open('medical_sources.yaml', 'r') as file:
                config = yaml.safe_load(file)
                return config.get('rag_settings', {})
        except Exception as e:
            logger.error(f"Error loading RAG config: {e}")
            return {
                'local_docs_path': './medical_docs',
                'chunk_size': 1000,
                'overlap': 200,
                'similarity_threshold': 0.7,
                'max_context_length': 4000
            }
    
    def load_documents(self):
        """Load all documents into memory"""
        docs_path = Path(self.config.get('local_docs_path', './medical_docs'))
        
        if not docs_path.exists():
            logger.warning(f"Medical docs path {docs_path} does not exist")
            return
        
        supported_extensions = {'.txt', '.pdf', '.docx', '.md'}
        
        for file_path in docs_path.rglob('*'):
            if file_path.suffix.lower() in supported_extensions:
                try:
                    content = self.extract_text(file_path)
                    if content:
                        self.documents[str(file_path)] = {
                            'content': content,
                            'chunks': self.chunk_text(content),
                            'filename': file_path.name
                        }
                        logger.info(f"Loaded: {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
    
    def extract_text(self, file_path):
        """Extract text from various file formats"""
        try:
            if file_path.suffix.lower() == '.pdf':
                return self.extract_pdf_text(file_path)
            elif file_path.suffix.lower() == '.docx':
                return self.extract_docx_text(file_path)
            elif file_path.suffix.lower() in {'.txt', '.md'}:
                return self.extract_plain_text(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def extract_pdf_text(self, file_path):
        """Extract text from PDF files"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def extract_docx_text(self, file_path):
        """Extract text from DOCX files"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    def extract_plain_text(self, file_path):
        """Extract text from plain text files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text):
        """Split text into chunks with overlap"""
        chunk_size = self.config.get('chunk_size', 1000)
        overlap = self.config.get('overlap', 200)
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk]
    
    def simple_similarity(self, query, text):
        """Simple keyword-based similarity scoring"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_relevant_context(self, query, max_results=3):
        """Get relevant context for a query using simple similarity"""
        try:
            if not self.documents:
                return ""
            
            threshold = self.config.get('similarity_threshold', 0.1)  # Lower threshold for simple similarity
            scored_chunks = []
            
            # Score all chunks from all documents
            for doc_path, doc_data in self.documents.items():
                for chunk in doc_data['chunks']:
                    score = self.simple_similarity(query, chunk)
                    if score >= threshold:
                        scored_chunks.append((score, chunk, doc_data['filename']))
            
            # Sort by score and get top results
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            relevant_chunks = [chunk for score, chunk, filename in scored_chunks[:max_results]]
            
            # Combine relevant chunks
            context = "\n\n".join(relevant_chunks)
            
            # Truncate if too long
            max_length = self.config.get('max_context_length', 4000)
            if len(context) > max_length:
                context = context[:max_length] + "..."
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""
    
    def add_document(self, file_path):
        """Add a single document to the collection"""
        try:
            content = self.extract_text(Path(file_path))
            if content:
                self.documents[str(file_path)] = {
                    'content': content,
                    'chunks': self.chunk_text(content),
                    'filename': Path(file_path).name
                }
                logger.info(f"Added document: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
        return False
    
    def get_collection_stats(self):
        """Get statistics about the document collection"""
        try:
            total_chunks = sum(len(doc['chunks']) for doc in self.documents.values())
            return {
                'total_documents': len(self.documents),
                'total_chunks': total_chunks,
                'status': 'healthy' if self.documents else 'empty'
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'total_documents': 0, 'total_chunks': 0, 'status': 'error'}