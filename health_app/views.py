from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
import json
import os
import logging
import random
import tempfile

from .services.extractors import extract_from_excel, extract_from_docx, extract_from_pdf
from .services.extractors.html_table_extractor import extract_from_html
from .services.extractors.normalizer import derive_basic_charts
from .services.extraction_store import add_artifacts, get_tables
from .services.visualization_service import VisualizationService
from .services.ollama_service import OllamaService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
try:
    from .services.south_africa_medical import south_africa_medical_service
except ImportError:
    south_africa_medical_service = None
    logger.warning("South Africa medical service not available")

try:
    from .services.web_search_service import WebSearchService
    web_search_service = WebSearchService()
except ImportError:
    web_search_service = None
    logger.warning("Web search service not available")

# Lazy load CourseService to avoid import errors on models/migrations
course_service = None

def get_course_service():
    global course_service
    if course_service is None:
        try:
            from .services.course_service import CourseService
            course_service = CourseService()
        except (ImportError, Exception) as e:
            logger.warning(f"Course service not available: {e}")
    return course_service

try:
    from .services.kpi_service import KPIService
    kpi_service = KPIService()
except ImportError:
    kpi_service = None
    logger.warning("KPI service not available")

try:
    from .services.business_school_kpi import (
        BusinessSchoolResearcher,
        BusinessSchoolKPIService,
        BusinessSchoolVisualizationService
    )
    business_school_researcher = BusinessSchoolResearcher()
    business_school_kpi_service = BusinessSchoolKPIService()
    business_school_viz_service = BusinessSchoolVisualizationService()
except ImportError:
    business_school_researcher = None
    business_school_kpi_service = None
    business_school_viz_service = None
    logger.warning("Business school KPI services not available")

# Try to import and configure Gemini AI
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    from .services.bot_config import BotConfigManager
    
    # Load from .env file explicitly
    try:
        from dotenv import load_dotenv
        # Load from .env in project root
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)
        logger.info(f"📁 Loading .env from: {env_path}")
    except ImportError:
        pass  # dotenv not available, fallback to os.getenv
    
    # Get API key from environment (after .env is loaded)
    api_key = os.getenv('GEMINI_API_KEY')
    logger.info(f"🔍 Debug: API key loaded: {api_key[:10] + '...' if api_key and len(api_key) > 10 else api_key}")
    
    if api_key and api_key != 'your_gemini_api_key_here' and 'EXAMPLEKEY' not in api_key:
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
        logger.info("✅ Gemini AI configured successfully")
    else:
        logger.info("⚠️ Using demo responses - API key appears to be placeholder")
        
except ImportError as e:
    logger.info(f"ℹ️ Google Generative AI not available: {e}")
except Exception as e:
    logger.error(f"❌ Error configuring Gemini AI: {e}")
    logger.info("ℹ️ Falling back to demo responses")

def chatbot_view(request):
    """Render the main chatbot interface"""
    return render(request, 'health_app/chatbot.html')

@csrf_exempt
@require_http_methods(["POST"])
def extract_api(request):
    """Upload endpoint to extract tables and basic chart descriptors from files or HTML."""
    if 'file' not in request.FILES and 'html' not in request.POST:
        return HttpResponseBadRequest('file or html required')

    artifacts = []
    warnings = []
    tmp_path = None

    try:
        if 'html' in request.POST and request.POST.get('html'):
            html = request.POST.get('html')
            artifacts.extend(extract_from_html(html, source_name=request.POST.get('source', 'web')))

        if 'file' in request.FILES:
            f = request.FILES['file']
            name = f.name.lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix='_'+f.name) as tmp:
                for chunk in f.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            if name.endswith('.xlsx') or name.endswith('.xls') or name.endswith('.csv'):
                try:
                    artifacts.extend(extract_from_excel(tmp_path))
                except Exception as e:
                    warnings.append(str(e))
            elif name.endswith('.docx'):
                try:
                    artifacts.extend(extract_from_docx(tmp_path))
                except Exception as e:
                    warnings.append(str(e))
            elif name.endswith('.pdf'):
                try:
                    artifacts.extend(extract_from_pdf(tmp_path))
                except Exception as e:
                    warnings.append(str(e))
            else:
                warnings.append('Unsupported file type')

        enriched_artifacts = list(artifacts)
        for table in [a for a in artifacts if a.get('type') == 'table']:
            enriched_artifacts.extend(derive_basic_charts(table))

        if not request.session.session_key:
            request.session.save()
        session_id = request.session.session_key
        add_artifacts(session_id, [a for a in enriched_artifacts if a.get('id')])

        return JsonResponse({"success": True, "artifacts": enriched_artifacts, "warnings": warnings})
    except Exception as e:
        logger.error(f"extract_api error: {e}")
        return JsonResponse({"success": False, "error": "Extraction failed"})
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


@csrf_exempt
@require_http_methods(["POST"])
def kpi_api(request):
    if not kpi_service:
        return JsonResponse({"success": False, "error": "KPI service unavailable"}, status=503)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)

    try:
        result = kpi_service.run(payload)
        if not result:
            return JsonResponse({"success": False, "error": "No matching data found"})
        return JsonResponse({"success": True, **result})
    except ValueError as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)
    except Exception as exc:
        logger.error(f"kpi_api error: {exc}")
        return JsonResponse({"success": False, "error": "Unable to compute KPI"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """Handle chat API requests with visualization support"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Use Gemini AI if available, otherwise use demo responses
        if GEMINI_AVAILABLE:
            response_data = generate_ai_response(user_message)
        else:
            # Demo mode: just text, no visualizations
            response_text = generate_demo_response(user_message)
            response_data = {
                'message': response_text,
                'visualizations': []
            }
        
        # Debug: Log the response structure
        logger.info(f"📝 Response structure: message length={len(response_data.get('message', ''))}, visualizations={len(response_data.get('visualizations', []))}")
        
        return JsonResponse({
            'success': True,
            'message': response_data.get('message', ''),
            'visualizations': response_data.get('visualizations', []),
            'conversation_id': conversation_id or generate_conversation_id(),
            'ai_powered': GEMINI_AVAILABLE
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'I apologize, but I encountered an error. Please try again.'
        })

def generate_ai_response(user_message, extracted_tables=None):
    """Generate response using Gemini AI with visualization and web search integration"""
    try:
        user_message_lower = user_message.lower()
        
        # Get table context for LLM
        table_context = VisualizationService.get_context_for_llm()
        
        # Generate base AI response with visualization support
        response_data = generate_ai_response_content(user_message, table_context)
        base_message = response_data.get('message', '')
        visualizations = response_data.get('visualizations', [])
        
        # Process and validate visualizations
        processed_visualizations = []
        for viz in visualizations:
            processed_viz = _process_visualization_request(viz)
            if processed_viz:
                processed_visualizations.append(processed_viz)
        
        final_message = base_message
        
        # Check if user is asking for South African medical resources
        sa_medical_keywords = [
            'south africa', 'sa doctor', 'doctor in south africa', 'south african',
            'find doctor', 'medical doctor', 'specialist', 'hospital', 'clinic',
            'emergency', 'ambulance', 'medical help', 'healthcare provider'
        ]
        
        # Check if user wants online sources/articles
        web_search_keywords = [
            'articles', 'research', 'studies', 'online sources', 'links', 'websites',
            'read more', 'more information', 'sources', 'evidence', 'clinical trials'
        ]
        
        needs_sa_resources = any(keyword in user_message_lower for keyword in sa_medical_keywords)
        needs_web_search = any(keyword in user_message_lower for keyword in web_search_keywords) or 'link' in user_message_lower
        
        # Add South African resources if requested
        if needs_sa_resources and south_africa_medical_service:
            resources = south_africa_medical_service.search_medical_resources(user_message)
            sa_response = south_africa_medical_service.format_medical_links_response(resources)
            final_message += f"\n\n---\n\n{sa_response}"
        
        # Add web search results if requested or for medical topics
        elif needs_web_search or any(word in user_message_lower for word in ['symptom', 'disease', 'condition', 'treatment', 'medicine', 'health']):
            if web_search_service:
                search_results = web_search_service.search_medical_sites(user_message)
                if search_results:
                    web_response = web_search_service.format_search_results(search_results, user_message)
                    final_message += f"\n\n---\n\n{web_response}"
        
        return {
            'message': final_message,
            'visualizations': processed_visualizations
        }
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return {
            'message': "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
            'visualizations': []
        }


def _process_visualization_request(viz_config):
    """
    Process and validate a visualization request from the LLM.
    Enriches it with actual data if needed.
    
    Args:
        viz_config: Visualization configuration dict from LLM
    
    Returns:
        Processed visualization dict or None if invalid
    """
    try:
        # Basic validation
        if not isinstance(viz_config, dict):
            logger.warning(f"Not a dict: {type(viz_config)}")
            return None
        
        chart_type = viz_config.get('type', '').lower()
        if chart_type not in VisualizationService.CHART_TYPES:
            logger.warning(f"Invalid chart type: {chart_type}")
            return None
        
        if not viz_config.get('title'):
            logger.warning("Missing title")
            return None
        
        source = viz_config.get('source', 'web').lower()
        
        # Get data based on source
        if source == 'extracted':
            # Load from extracted table
            table_id = viz_config.get('table_id')
            if not table_id:
                logger.warning("Extracted viz missing table_id")
                return None
            
            config = viz_config.get('config', {})
            data = VisualizationService.get_chart_data_from_table(table_id, config)
            if not data:
                logger.warning(f"Could not load table {table_id}")
                return None
            
            viz_config['data'] = data
        
        elif source == 'web':
            # Fetch real data from web sources (no synthetic fallback)
            context = f"{viz_config.get('title', '')} {viz_config.get('description', '')}"
            limit = viz_config.get('config', {}).get('limit', 10)
            
            logger.info(f"Fetching real web data for: {context}")
            data = VisualizationService.search_web_for_data(context, num_items=limit)
            
            if not data:
                logger.warning(f"No real data found for visualization. Returning None instead of synthetic fallback.")
                return None
            
            viz_config['data'] = data
        
        elif source == 'synthetic':
            # Synthetic data is no longer allowed
            logger.warning(f"Synthetic data requested but not allowed per configuration")
            return None
        
        # Validate final config
        if not VisualizationService.validate_chart_config(viz_config):
            logger.warning(f"Final validation failed")
            return None
        
        return viz_config
    
    except Exception as e:
        logger.error(f"Error processing viz: {str(e)}")
        return None

def generate_ai_response_content(user_message, table_context=""):
    """Generate AI response content using Gemini with visualization support"""
    try:
        # Create the model (using Gemini 2.5 Flash)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Get system prompt from active configuration
        system_prompt = BotConfigManager.get_gemini_prompt()

        # Build the full prompt
        data_context = f"\n\nAVAILABLE EXTRACTED DATA:\n{table_context}" if table_context else ""
        full_prompt = f"{system_prompt}{data_context}\n\nUser request: {user_message}\n\nJSON Output:"
        
        logger.info(f"📤 Sending to Gemini...")
        
        # Generate response with strict timeout
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )
        response_text = response.text.strip()
        
        logger.info(f"📥 Received response ({len(response_text)} chars)")
        
        # Try to parse as JSON
        try:
            # Clean up markdown code blocks if present
            cleaned = response_text
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json\n"):
                    cleaned = cleaned[5:]
                elif cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            
            cleaned = cleaned.strip()
            parsed = json.loads(cleaned)
            logger.info("✅ JSON parsed successfully")
            
            # Get message and visualizations
            message = parsed.get('message', '').strip()
            visualizations = parsed.get('visualizations', []) or []
            
            # Ensure visualizations is a list
            if not isinstance(visualizations, list):
                visualizations = []
            
            # Add disclaimer
            if message:
                message += "\n\n💡 **Medical Disclaimer**: For professional medical advice, consult a healthcare provider."
            
            return {
                'message': message or "I'm here to help with health questions.",
                'visualizations': visualizations
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {str(e)}")
            logger.debug(f"Response: {response_text[:200]}")
            
            # Return response as message only, no visualizations
            return {
                'message': response_text + "\n\n💡 **Medical Disclaimer**: For professional medical advice, consult a healthcare provider.",
                'visualizations': []
            }
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a quota/rate limit error
        if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            logger.warning(f"⚠️ API quota limit exceeded. Trying Ollama fallback...")
            
            # Try Ollama as fallback
            ollama_service = OllamaService()
            if ollama_service.available:
                logger.info("🔄 Using Ollama for offline response")
                return ollama_service.generate_response(user_message)
            else:
                logger.info("Ollama not available, returning temporary capacity message")
                return {
                    'message': _temporary_capacity_message(),
                    'visualizations': []
                }
        
        logger.error(f"Error: {str(e)}", exc_info=True)
        
        # Try Ollama as general fallback for any other errors
        ollama_service = OllamaService()
        if ollama_service.available:
            logger.info("🔄 Using Ollama due to Gemini error")
            return ollama_service.generate_response(user_message)
        
        return {
            'message': "The server is overloaded right now. Please try again a little later.",
            'visualizations': []
        }


def _temporary_capacity_message():
    """Generic user-facing message for temporary hosted model capacity issues."""
    return (
        "The server is overloaded right now. Please reconvene in a few hours and try again."
    )


def _generate_demo_response_with_viz(user_message):
    """Generate demo response with visualization when API quota is exceeded"""
    user_lower = user_message.lower()
    
    # Check if visualization is requested
    viz_keywords = ['visualize', 'visualise', 'chart', 'graph', 'show', 'display', 'top ', 'ranking']
    
    if any(keyword in user_lower for keyword in viz_keywords):
        # Determine what kind of visualization to create
        if 'mba' in user_lower or 'school' in user_lower:
            return {
                'message': "Here are the top MBA schools. MBA programs prepare future business leaders with advanced management skills.",
                'visualizations': [{
                    'type': 'bar',
                    'title': 'Top MBA Programs',
                    'description': 'Leading MBA schools worldwide',
                    'source': 'synthetic',
                    'config': {'limit': 10},
                    'data': {
                        'labels': ['Harvard', 'Stanford', 'INSEAD', 'MIT Sloan', 'Wharton', 'Kellogg', 'Duke Fuqua', 'Yale', 'Columbia', 'Northwestern'],
                        'rows': [
                            ['Harvard Business School', 1],
                            ['Stanford Graduate School of Business', 2],
                            ['INSEAD', 3],
                            ['MIT Sloan School of Management', 4],
                            ['Wharton School of Business', 5],
                            ['Kellogg School of Management', 6],
                            ['Duke Fuqua School of Business', 7],
                            ['Yale School of Management', 8],
                            ['Columbia Business School', 9],
                            ['Northwestern Kellogg School', 10]
                        ],
                        'series': [
                            {'label': 'Rank', 'data': list(range(1, 11))}
                        ]
                    }
                }]
            }
        
        elif 'universit' in user_lower or 'rank' in user_lower:
            return {
                'message': "Here are the top universities by academic ranking. These institutions are recognized globally for research and teaching excellence.",
                'visualizations': [{
                    'type': 'table',
                    'title': 'Top Universities Worldwide',
                    'description': 'Leading universities by academic ranking',
                    'source': 'synthetic',
                    'config': {'limit': 10},
                    'data': {
                        'labels': ['University', 'Country', 'Ranking'],
                        'rows': [
                            ['Harvard University', 'USA', 1],
                            ['Stanford University', 'USA', 2],
                            ['MIT', 'USA', 3],
                            ['Oxford University', 'UK', 4],
                            ['Cambridge University', 'UK', 5],
                            ['Caltech', 'USA', 6],
                            ['Yale University', 'USA', 7],
                            ['Princeton University', 'USA', 8],
                            ['UC Berkeley', 'USA', 9],
                            ['University of Chicago', 'USA', 10]
                        ],
                        'series': []
                    }
                }]
            }
        
        elif 'symptom' in user_lower or 'covid' in user_lower:
            return {
                'message': "COVID-19 commonly presents with respiratory and systemic symptoms. If you experience severe symptoms, seek immediate medical attention.",
                'visualizations': [{
                    'type': 'bar',
                    'title': 'COVID-19 Symptoms Frequency',
                    'description': 'Common symptoms and their prevalence',
                    'source': 'synthetic',
                    'config': {'limit': 10},
                    'data': {
                        'labels': ['Fever', 'Cough', 'Fatigue', 'Breathing', 'Headache', 'Loss of Taste', 'Sore Throat', 'Muscle Pain', 'Diarrhea', 'Chills'],
                        'rows': [
                            ['Fever', 88],
                            ['Cough', 76],
                            ['Fatigue', 61],
                            ['Difficulty Breathing', 35],
                            ['Headache', 34],
                            ['Loss of Taste/Smell', 30],
                            ['Sore Throat', 26],
                            ['Muscle Pain', 24],
                            ['Diarrhea', 20],
                            ['Chills', 18]
                        ],
                        'series': [
                            {'label': 'Frequency %', 'data': [88, 76, 61, 35, 34, 30, 26, 24, 20, 18]}
                        ]
                    }
                }]
            }
        
        elif 'medicine' in user_lower or 'medication' in user_lower or 'drug' in user_lower:
            return {
                'message': "Common medications treating various conditions. Always follow medical professional guidance for proper usage and dosage.",
                'visualizations': [{
                    'type': 'table',
                    'title': 'Common Medications',
                    'description': 'Frequently prescribed medications',
                    'source': 'synthetic',
                    'config': {'limit': 10},
                    'data': {
                        'labels': ['Medication Name', 'Type', 'Common Use'],
                        'rows': [
                            ['Aspirin', 'Analgesic', 'Pain & Fever'],
                            ['Ibuprofen', 'Anti-inflammatory', 'Pain & Inflammation'],
                            ['Acetaminophen', 'Analgesic', 'Pain & Fever'],
                            ['Amoxicillin', 'Antibiotic', 'Bacterial Infections'],
                            ['Lisinopril', 'Antihypertensive', 'High Blood Pressure'],
                            ['Metformin', 'Antidiabetic', 'Type 2 Diabetes'],
                            ['Atorvastatin', 'Statin', 'High Cholesterol'],
                            ['Levothyroxine', 'Thyroid', 'Hypothyroidism'],
                            ['Omeprazole', 'Proton Pump Inhibitor', 'GERD'],
                            ['Sertraline', 'SSRI', 'Depression/Anxiety']
                        ],
                        'series': []
                    }
                }]
            }
        
        # Generic visualization for other queries
        return {
            'message': "Here's some data related to your query.",
            'visualizations': [{
                'type': 'table',
                'title': f'Data for: {user_message[:30]}',
                'description': 'Information related to your request',
                'source': 'synthetic',
                'config': {'limit': 5},
                'data': {
                    'labels': ['Item', 'Value'],
                    'rows': [
                        ['Information 1', 100],
                        ['Information 2', 80],
                        ['Information 3', 60],
                        ['Information 4', 40],
                        ['Information 5', 20]
                    ],
                    'series': []
                }
            }]
        }
    
    # Non-visualization request - return text only
    if 'fever' in user_lower:
        return {
            'message': "**Fever** is your body's way of fighting infection. Normal temperature is 98.6°F (37°C). Seek immediate care if fever exceeds 103°F or is accompanied by severe symptoms.",
            'visualizations': []
        }
    
    if 'headache' in user_lower:
        return {
            'message': "**Headaches** can be tension, migraine, or sinus-related. Common relief includes rest, hydration, and pain relievers. Seek emergency care for sudden severe headaches.",
            'visualizations': []
        }
    
    if 'cough' in user_lower:
        return {
            'message': "**Coughs** help clear airways and can be dry or productive. Most resolve on their own, but see a doctor if lasting more than 3 weeks or with other concerning symptoms.",
            'visualizations': []
        }
    
    # Default response
    return {
        'message': "I'm currently using offline mode. How can I help with your health questions?",
        'visualizations': []
    }

def generate_demo_response(user_message):
    """Generate demo health response (when Gemini AI is not available)"""
    
    user_message_lower = user_message.lower()
    
    # Check if user is asking for South African medical resources
    sa_medical_keywords = [
        'south africa', 'sa doctor', 'doctor in south africa', 'south african',
        'find doctor', 'medical doctor', 'specialist', 'hospital', 'clinic',
        'emergency', 'ambulance', 'medical help', 'healthcare provider'
    ]
    
    # Check if user wants web search
    web_search_keywords = [
        'articles', 'research', 'studies', 'online sources', 'links', 'websites',
        'read more', 'more information', 'sources', 'evidence'
    ]
    
    needs_sa_resources = any(keyword in user_message_lower for keyword in sa_medical_keywords)
    needs_web_search = any(keyword in user_message_lower for keyword in web_search_keywords) or 'link' in user_message_lower
    
    if needs_sa_resources and south_africa_medical_service:
        # Get South African medical resources
        resources = south_africa_medical_service.search_medical_resources(user_message)
        response_text = south_africa_medical_service.format_medical_links_response(resources)
        return response_text
    
    # Check if web search is requested
    if needs_web_search and web_search_service:
        search_results = web_search_service.search_medical_sites(user_message)
        if search_results:
            response_text = web_search_service.format_search_results(search_results, user_message)
            return response_text
    
    # Simple keyword-based responses for demonstration
    responses = {
        'fever': """
        **Fever** is your body fighting infection. Normal is 98.6°F (37°C).
        
        **Seek care if:** Above 103°F, lasting 3+ days, or with severe symptoms.
        **Home care:** Rest, hydrate, use fever reducers as directed.
        """,
        
        'headache': """
        **Headaches** are usually not serious. Common types: tension, migraine, sinus.
        
        **Emergency care if:** Sudden severe headache, with fever/stiff neck, after injury, or vision changes.
        **Treatment:** Rest in dark room, compress, hydrate, OTC pain relievers.
        """,
        
        'cough': """
        **Coughs** help clear airways. Can be dry or productive (with mucus).
        
        **See doctor if:** Lasting 3+ weeks, blood, breathing issues, or chest pain.
        **Home care:** Stay hydrated, humidifier, honey, throat lozenges.
        """,
        
        'pain': """
        **Pain** signals something needs attention.
        
        **Common relief:** Acetaminophen, ibuprofen, or aspirin as directed.
        **Seek care if:** Severe, worsening, after injury, or chronic.
        **Natural options:** Rest, hot/cold therapy, relaxation.
        """
    }
    
    # Check for keywords in user message
    message_lower = user_message.lower()
    
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response + "\n\n💡 **Important**: This information is for educational purposes only. Always consult with healthcare professionals for personalized medical advice."
    
    # Default health response
    default_responses = [
        """
        Hello! I'm HealthBot AI. I can help with symptoms, medications, wellness tips, and when to seek care.
        
        What's your health question?
        
        💡 **Remember**: Always consult healthcare professionals for medical advice.
        """,
        
        """
        I'm here to provide general health information. For serious symptoms, contact your healthcare provider. For emergencies, call 911.
        
        What would you like to know about?
        
        💡 **Disclaimer**: Educational information only, not medical advice.
        """
    ]
    
    return random.choice(default_responses)

def generate_conversation_id():
    """Generate a unique conversation ID"""
    import uuid
    return str(uuid.uuid4())

def api_status(request):
    """Check API configuration status"""
    try:
        # Load current environment
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Debug information
        debug_info = {
            'api_key_raw': api_key,
            'api_key_length': len(api_key) if api_key else 0,
            'api_key_starts_correctly': api_key.startswith('AIzaSy') if api_key else False,
            'is_placeholder': api_key == 'your_gemini_api_key_here' if api_key else False,
            'api_key_preview': f"{api_key[:10]}..." if api_key and len(api_key) > 10 else api_key
        }
        
        status = {
            'gemini_configured': GEMINI_AVAILABLE,
            'api_key_present': bool(api_key and api_key != 'your_gemini_api_key_here'),
            'demo_mode': not GEMINI_AVAILABLE,
            'debug': debug_info
        }
        
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'gemini_configured': False,
            'demo_mode': True
        })

# Course-related views
def course_view(request):
    """Render the course chatbot interface"""
    return render(request, 'health_app/course.html')

@csrf_exempt
@require_http_methods(["POST"])
def course_chat_api(request):
    """Handle course chat API requests with visualization support"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        request_external = data.get('request_external', False)
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        course_service = get_course_service()
        if not course_service:
            return JsonResponse({
                'success': False,
                'error': 'Course service not available'
            })
        
        # Try to get response with visualizations
        visualizations = []
        if GEMINI_AVAILABLE:
            try:
                # Get table context for visualization support
                table_context = VisualizationService.get_context_for_llm()
                
                # Generate AI response with visualization support
                response_data = generate_ai_response_content(user_message, table_context)
                base_message = response_data.get('message', '')
                visualizations = response_data.get('visualizations', [])
                
                # Process and validate visualizations
                processed_visualizations = []
                for viz in visualizations:
                    processed_viz = _process_visualization_request(viz)
                    if processed_viz:
                        processed_visualizations.append(processed_viz)
                
                visualizations = processed_visualizations
                response_text = base_message
            except Exception as viz_error:
                logger.warning(f"Visualization generation failed in course chat: {str(viz_error)}, falling back to course service")
                # Fall back to course service if visualization generation fails
                course_service = get_course_service()
                response_data = course_service.get_response(user_message, request_external)
                response_text = response_data['response']
        else:
            # Use course service directly when Gemini is not available
            response_data = course_service.get_response(user_message, request_external)
            response_text = response_data['response']
        
        # Debug: Log the response structure
        logger.info(f"📝 Course response: message length={len(response_text)}, visualizations={len(visualizations)}")
        
        return JsonResponse({
            'success': True,
            'response': response_text,
            'message': response_text,  # Include 'message' field for compatibility
            'visualizations': visualizations,
            'conversation_id': conversation_id or generate_conversation_id(),
            'ai_powered': GEMINI_AVAILABLE
        })
        
    except Exception as e:
        logger.error(f"Error in course chat API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'I encountered an error processing your educational query. Please try again.'
        })

@csrf_exempt
@require_http_methods(["POST"])
def upload_pdf(request):
    """Handle PDF file uploads for course materials"""
    try:
        course_service = get_course_service()
        if not course_service:
            return JsonResponse({
                'success': False,
                'error': 'Course service not available'
            })
        
        pdf_file = request.FILES.get('pdf_file')
        course_name = request.POST.get('course_name', 'General Course')
        
        if not pdf_file:
            return JsonResponse({
                'success': False,
                'error': 'No PDF file provided'
            })
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'error': 'Please upload a PDF file'
            })
        
        # Ingest the PDF
        success = course_service.ingest_pdf(pdf_file, course_name)
        
        if success:
            stats = course_service.get_corpus_stats()
            return JsonResponse({
                'success': True,
                'message': f'PDF successfully uploaded and processed for {course_name}',
                'corpus_stats': stats
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to process PDF file'
            })
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error processing PDF upload'
        })

@csrf_exempt
@require_http_methods(["GET"])
def course_stats(request):
    """Get course corpus statistics"""
    try:
        course_service = get_course_service()
        if not course_service:
            return JsonResponse({
                'success': False,
                'error': 'Course service not available'
            })
        
        stats = course_service.get_corpus_stats()
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting course stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error retrieving course statistics'
        })


# ==================== BUSINESS SCHOOL KPI ENDPOINTS ====================

@csrf_exempt
@require_http_methods(["POST"])
def business_school_kpis_api(request):
    """Get KPI data for business schools with filtering and stratification"""
    if not business_school_kpi_service:
        return JsonResponse({
            'success': False,
            'error': 'Business school KPI service unavailable'
        }, status=503)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    
    try:
        school_name = payload.get('school_name')
        schools_list = payload.get('schools')
        filters = payload.get('filters', {})
        query_type = payload.get('query_type', 'single')  # 'single', 'aggregate', 'filtered'
        
        logger.info(f"🏫 Business school KPI query: type={query_type}, school={school_name}")
        
        if query_type == 'single' and school_name:
            # Get KPIs for a single school
            result = business_school_kpi_service.get_school_kpis(school_name, filters)
            return JsonResponse({'success': result.get('success', False), **result})
        
        elif query_type == 'aggregate' and schools_list:
            # Aggregate KPIs across multiple schools
            result = business_school_kpi_service.aggregate_kpis(schools_list, filters)
            return JsonResponse({'success': result.get('success', False), **result})
        
        elif query_type == 'filtered':
            # Get KPIs filtered by criteria
            result = business_school_kpi_service.get_kpis_by_filter(filters)
            return JsonResponse({'success': result.get('success', False), **result})
        
        else:
            # Default: get all schools
            result = business_school_kpi_service.aggregate_kpis()
            return JsonResponse({'success': result.get('success', False), **result})
        
    except Exception as e:
        logger.error(f"business_school_kpis_api error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to compute business school KPIs'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def business_school_research_api(request):
    """Trigger research for business schools and get detailed data"""
    if not business_school_researcher:
        return JsonResponse({
            'success': False,
            'error': 'Business school researcher unavailable'
        }, status=503)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    
    try:
        query = payload.get('query', '')
        region = payload.get('region')
        school_name = payload.get('school_name')
        
        logger.info(f"🔍 Business school research: query='{query}', region={region}")
        
        if school_name:
            # Get details for specific school
            school = business_school_researcher.extract_school_details(school_name)
            if school:
                return JsonResponse({
                    'success': True,
                    'school': school,
                    'source': school.get('source'),
                    'data_quality': school.get('data_quality')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'School not found: {school_name}'
                }, status=404)
        
        else:
            # Research schools by query/region
            schools = business_school_researcher.research_schools(query, region)
            return JsonResponse({
                'success': len(schools) > 0,
                'schools': schools,
                'count': len(schools),
                'query': query,
                'region': region
            })
        
    except Exception as e:
        logger.error(f"business_school_research_api error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to complete business school research'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def business_school_visualizations_api(request):
    """Get stratified visualizations for business school KPIs"""
    if not business_school_viz_service:
        return JsonResponse({
            'success': False,
            'error': 'Business school visualization service unavailable'
        }, status=503)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    
    try:
        schools = payload.get('schools')
        viz_types = payload.get('viz_types', 'all')  # 'all' or list like ['chart', 'table', 'filters']
        filters = payload.get('filters', {})
        
        logger.info(f"📊 Business school visualization request: types={viz_types}")
        
        visualizations = []
        
        if viz_types == 'all' or 'chart' in viz_types:
            visualizations.append(business_school_viz_service.render_kpi_overview_chart(schools))
        
        if viz_types == 'all' or 'table' in viz_types:
            visualizations.append(business_school_viz_service.render_expandable_detail_table(schools))
        
        if viz_types == 'all' or 'filters' in viz_types:
            visualizations.append(business_school_viz_service.render_filter_controls())
        
        if viz_types == 'all' or 'cascading' in viz_types:
            visualizations.append(business_school_viz_service.render_cascading_selection())
        
        if viz_types == 'all' or 'stats' in viz_types:
            visualizations.append(business_school_viz_service.render_stats_cards(schools))
        
        return JsonResponse({
            'success': True,
            'visualizations': visualizations,
            'count': len(visualizations)
        })
        
    except Exception as e:
        logger.error(f"business_school_visualizations_api error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to generate visualizations'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def search_course_history(request):
    """Search conversation history for quick retrieval"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        course_service = get_course_service()
        if not course_service:
            return JsonResponse({
                'success': False,
                'error': 'Course service not available'
            })
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Search query cannot be empty'
            })
        
        # Search conversation history
        history_results = course_service.search_conversation_history(query)
        
        return JsonResponse({
            'success': True,
            'results': history_results
        })
        
    except Exception as e:
        logger.error(f"Error searching course history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error searching conversation history'
        })
