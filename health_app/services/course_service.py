import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from django.conf import settings
from .bot_config import BotConfigManager
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
import io
import requests
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
import numpy as np
try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    cosine_similarity = None
import pickle
import hashlib

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self):
        """Initialize the Course Service with vector embeddings and conversation history"""
        self.model = None
        self.course_corpus = []
        self.course_embeddings = None
        self.conversation_history = []
        self.corpus_file = 'course_corpus.pkl'
        self.embeddings_file = 'course_embeddings.pkl'
        self.history_file = 'course_conversation_history.json'
        self.min_corpus_size = 5  # Minimum number of documents before external search
        self.embedding_available = False
        self.pdf_available = PyPDF2 is not None

        if SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_available = cosine_similarity is not None
            except Exception as e:
                logger.warning(f"Course embedding model unavailable: {e}")
        else:
            logger.warning("sentence_transformers not installed; using keyword search fallback")
        
        # Initialize Gemini AI
        try:
            # Use the same API key loading approach as views.py
            api_key = os.getenv('GEMINI_API_KEY')
            if genai and api_key and api_key != 'your_gemini_api_key_here' and 'EXAMPLEKEY' not in api_key:
                genai.configure(api_key=api_key)
                self.ai_model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Course AI service initialized successfully")
            else:
                logger.info("⚠️ Course AI using demo mode - API key appears to be placeholder")
                self.ai_model = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Course AI: {e}")
            self.ai_model = None
        
        # Load existing data
        self.load_corpus()
        self.load_conversation_history()
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from uploaded PDF file"""
        try:
            if PyPDF2 is None:
                logger.warning("PyPDF2 not installed; cannot extract PDF content")
                return ""
            if hasattr(pdf_file, 'read'):
                pdf_content = pdf_file.read()
            else:
                with open(pdf_file, 'rb') as file:
                    pdf_content = file.read()
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            logger.info(f"📄 Extracted {len(text_content)} characters from PDF")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ Error extracting PDF text: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context preservation"""
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
                    end = break_point + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        logger.info(f"📝 Created {len(chunks)} text chunks")
        return chunks
    
    def ingest_pdf(self, pdf_file, course_name: str = None) -> bool:
        """Ingest a PDF file into the course knowledge base"""
        try:
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_file)
            if not text_content.strip():
                logger.warning("⚠️ No text content extracted from PDF")
                return False
            
            # Create document metadata
            doc_id = hashlib.md5(text_content.encode()).hexdigest()[:8]
            document = {
                'id': doc_id,
                'course_name': course_name or 'Unknown Course',
                'content': text_content,
                'ingested_at': datetime.now().isoformat(),
                'chunk_count': 0
            }
            
            # Chunk the text
            chunks = self.chunk_text(text_content)
            document['chunk_count'] = len(chunks)
            
            # Add chunks to corpus
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'id': f"{doc_id}_chunk_{i}",
                    'parent_id': doc_id,
                    'course_name': course_name or 'Unknown Course',
                    'content': chunk,
                    'chunk_index': i,
                    'ingested_at': datetime.now().isoformat()
                }
                self.course_corpus.append(chunk_doc)
            
            # Generate embeddings for new chunks
            self.generate_embeddings()
            
            # Save updated corpus
            self.save_corpus()
            
            logger.info(f"✅ Successfully ingested PDF: {len(chunks)} chunks added")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ingesting PDF: {e}")
            return False
    
    def generate_embeddings(self):
        """Generate vector embeddings for all corpus documents"""
        try:
            if not self.embedding_available or self.model is None:
                logger.info("Embeddings unavailable; skipping vector generation")
                self.course_embeddings = np.array([])
                return
            if not self.course_corpus:
                self.course_embeddings = np.array([])
                return
            
            # Extract content for embedding
            contents = [doc['content'] for doc in self.course_corpus]
            
            # Generate embeddings
            logger.info("🔄 Generating embeddings...")
            self.course_embeddings = self.model.encode(contents)
            
            # Save embeddings
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.course_embeddings, f)
            
            logger.info(f"✅ Generated embeddings for {len(contents)} documents")
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            self.course_embeddings = np.array([])
    
    def search_course_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search course content using vector similarity"""
        try:
            if not self.embedding_available or self.model is None or not self.course_corpus or self.course_embeddings is None or len(self.course_embeddings) == 0:
                logger.info("📭 No course content available for search")
                return self._keyword_search_course_content(query, top_k)
            
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.course_embeddings)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Minimum similarity threshold
                    doc = self.course_corpus[idx].copy()
                    doc['similarity'] = float(similarities[idx])
                    results.append(doc)
            
            logger.info(f"🔍 Found {len(results)} relevant course documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching course content: {e}")
            return self._keyword_search_course_content(query, top_k)
    
    def should_search_external(self, query: str, local_results: List[Dict]) -> bool:
        """Determine if external search is needed based on corpus size and relevance"""
        # Check if corpus is too small
        if len(self.course_corpus) < self.min_corpus_size:
            return True
        
        # Check if local results are sufficient
        if not local_results:
            return True
        
        # Check relevance scores
        high_relevance_results = [r for r in local_results if r.get('similarity', 0) > 0.7]
        if len(high_relevance_results) < 2:
            return True
        
        return False

    def _keyword_search_course_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Fallback search when embedding dependencies are unavailable."""
        if not self.course_corpus:
            logger.info("No course content available for keyword search")
            return []

        query_words = [word for word in query.lower().split() if len(word) > 2]
        scored_results = []

        for doc in self.course_corpus:
            content = doc.get('content', '').lower()
            score = sum(content.count(word) for word in query_words)
            if score > 0:
                item = doc.copy()
                item['similarity'] = min(score / max(len(query_words), 1), 1.0)
                scored_results.append(item)

        scored_results.sort(key=lambda item: item.get('similarity', 0), reverse=True)
        logger.info(f"Keyword search found {len(scored_results[:top_k])} relevant course documents")
        return scored_results[:top_k]
    
    def get_response(self, query: str, request_external: bool = False) -> Dict[str, Any]:
        """Get course-focused response with option for external search"""
        try:
            # Search local course content
            local_results = self.search_course_content(query)
            
            # Check if external search is needed
            needs_external = self.should_search_external(query, local_results)
            
            # Build context from local results
            context_parts = []
            if local_results:
                context_parts.append("**Course Materials Context:**")
                for i, result in enumerate(local_results[:3], 1):
                    course_name = result.get('course_name', 'Course Material')
                    content_preview = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                    context_parts.append(f"{i}. **{course_name}**: {content_preview}")
                context_parts.append("")
            
            # Get system prompt from active configuration
            system_prompt = BotConfigManager.get_course_prompt()
            
            context = "\n".join(context_parts) if context_parts else "No specific course materials found for this query."
            
            user_prompt = f"""
            {context}
            
            **Student Question:** {query}
            
            Please provide a comprehensive educational response. If the course materials are insufficient, 
            indicate this and suggest that external educational resources might be helpful.
            """
            
            # Generate AI response
            if self.ai_model:
                response = self.ai_model.generate_content(user_prompt)
                ai_response = response.text
            else:
                ai_response = self._build_fallback_response(local_results, needs_external)
            
            # Build response object
            response_data = {
                'response': ai_response,
                'local_results_count': len(local_results),
                'needs_external_search': needs_external and not request_external,
                'external_search_requested': request_external,
                'course_materials_available': len(self.course_corpus),
                'sources': []
            }
            
            # Add source information
            if local_results:
                for result in local_results[:3]:
                    source_info = {
                        'course_name': result.get('course_name', 'Course Material'),
                        'similarity': result.get('similarity', 0),
                        'content_preview': result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                    }
                    response_data['sources'].append(source_info)
            
            # Record interaction in conversation history
            self.record_interaction(query, response_data)
            
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Error generating course response: {e}")
            return {
                'response': "I encountered an error while processing your educational query. Please try again.",
                'local_results_count': 0,
                'needs_external_search': False,
                'external_search_requested': False,
                'course_materials_available': len(self.course_corpus),
                'sources': []
            }
    
    def record_interaction(self, query: str, response_data: Dict):
        """Record conversation for quick retrieval"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response_data['response'],
            'sources_used': len(response_data['sources']),
            'local_results': response_data['local_results_count'],
            'needed_external': response_data.get('needs_external_search', False)
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only last 100 interactions
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        # Save history
        self.save_conversation_history()
    
    def search_conversation_history(self, query: str, limit: int = 5) -> List[Dict]:
        """Search previous conversations for quick retrieval"""
        if not self.conversation_history:
            return []
        
        # Simple keyword matching (could be enhanced with embeddings)
        query_words = query.lower().split()
        matches = []
        
        for interaction in reversed(self.conversation_history):  # Most recent first
            interaction_text = (interaction['query'] + " " + interaction['response']).lower()
            
            # Calculate simple relevance score
            score = sum(1 for word in query_words if word in interaction_text)
            
            if score > 0:
                matches.append({
                    'interaction': interaction,
                    'relevance_score': score
                })
        
        # Sort by relevance and return top results
        matches.sort(key=lambda x: x['relevance_score'], reverse=True)
        return [match['interaction'] for match in matches[:limit]]
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the course corpus"""
        courses = {}
        total_chunks = len(self.course_corpus)
        
        for doc in self.course_corpus:
            course_name = doc.get('course_name', 'Unknown Course')
            if course_name not in courses:
                courses[course_name] = 0
            courses[course_name] += 1
        
        return {
            'total_documents': total_chunks,
            'courses': courses,
            'conversation_history': len(self.conversation_history),
            'embeddings_available': self.course_embeddings is not None and len(self.course_embeddings) > 0,
            'embedding_backend_available': self.embedding_available,
            'pdf_support_available': self.pdf_available,
            'ai_available': self.ai_model is not None
        }

    def _build_fallback_response(self, local_results: List[Dict], needs_external: bool) -> str:
        """Build a useful non-AI response from local course content."""
        if local_results:
            snippets = []
            for result in local_results[:3]:
                course_name = result.get('course_name', 'Course Material')
                preview = result.get('content', '')[:220].strip()
                snippets.append(f"{course_name}: {preview}")

            response = "I couldn't use the AI course model, but I found relevant material in your local course content.\n\n"
            response += "\n\n".join(snippets)
            if needs_external:
                response += "\n\nYour local course corpus may be limited for this question, so external resources may still help."
            return response

        return (
            "The course service is running, but some AI or search dependencies are unavailable right now. "
            "I couldn't find matching local course material for this question."
        )
    
    def save_corpus(self):
        """Save course corpus to file"""
        try:
            with open(self.corpus_file, 'wb') as f:
                pickle.dump(self.course_corpus, f)
            logger.info("💾 Course corpus saved successfully")
        except Exception as e:
            logger.error(f"❌ Error saving corpus: {e}")
    
    def load_corpus(self):
        """Load course corpus from file"""
        try:
            if os.path.exists(self.corpus_file):
                with open(self.corpus_file, 'rb') as f:
                    self.course_corpus = pickle.load(f)
                logger.info(f"📁 Loaded {len(self.course_corpus)} course documents")
                
                # Load embeddings
                if os.path.exists(self.embeddings_file):
                    with open(self.embeddings_file, 'rb') as f:
                        self.course_embeddings = pickle.load(f)
                    logger.info("📁 Loaded course embeddings")
                else:
                    self.generate_embeddings()
            else:
                logger.info("📁 No existing course corpus found")
        except Exception as e:
            logger.error(f"❌ Error loading corpus: {e}")
            self.course_corpus = []
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving conversation history: {e}")
    
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.conversation_history = json.load(f)
                logger.info(f"📁 Loaded {len(self.conversation_history)} conversation records")
            else:
                logger.info("📁 No existing conversation history found")
        except Exception as e:
            logger.error(f"❌ Error loading conversation history: {e}")
            self.conversation_history = []
