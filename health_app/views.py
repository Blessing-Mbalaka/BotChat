from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
import json
import os
import logging
import random

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

# Try to import and configure Gemini AI
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    
    # Try to load from dotenv, fallback to os.getenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available, but os.getenv should still work
    
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
def chat_api(request):
    """Handle chat API requests"""
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
            response = generate_ai_response(user_message)
        else:
            response = generate_demo_response(user_message)
        
        # Debug: Log the response to see if HTML is being escaped
        logger.info(f"📝 Response being sent: {response[:200]}...")
        
        return JsonResponse({
            'success': True,
            'response': response,
            'conversation_id': conversation_id or generate_conversation_id(),
            'ai_powered': GEMINI_AVAILABLE
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'I apologize, but I encountered an error. Please try again.'
        })

def generate_ai_response(user_message):
    """Generate response using Gemini AI with web search integration"""
    try:
        user_message_lower = user_message.lower()
        
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
        
        # Generate base AI response
        ai_response = generate_ai_response_content(user_message)
        
        # Add South African resources if requested
        if needs_sa_resources and south_africa_medical_service:
            resources = south_africa_medical_service.search_medical_resources(user_message)
            sa_response = south_africa_medical_service.format_medical_links_response(resources)
            ai_response += f"\n\n---\n\n{sa_response}"
        
        # Add web search results if requested or for medical topics
        elif needs_web_search or any(word in user_message_lower for word in ['symptom', 'disease', 'condition', 'treatment', 'medicine', 'health']):
            if web_search_service:
                search_results = web_search_service.search_medical_sites(user_message)
                if search_results:
                    web_response = web_search_service.format_search_results(search_results, user_message)
                    ai_response += f"\n\n---\n\n{web_response}"
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

def generate_ai_response_content(user_message):
    """Generate AI response content using Gemini"""
    try:
        # Create the model (using Gemini 2.5 Flash)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Health-focused system prompt
        system_prompt = """You are HealthBot AI, a knowledgeable and empathetic health assistant.

IMPORTANT GUIDELINES:
- Provide general health information only
- Always remind users to consult healthcare professionals for medical advice
- Be empathetic and supportive in your responses
- Use clear, easy-to-understand language
- If discussing symptoms, suggest when to seek immediate medical attention
- Never provide specific medical diagnoses
- Encourage healthy lifestyle choices

RESPONSE STYLE - KEEP IT CONCISE:
- Keep responses SHORT and focused (2-4 sentences maximum)
- Use 1-3 bullet points only when absolutely necessary
- Be direct and to-the-point while remaining caring
- Avoid lengthy explanations - give key information only
- Don't repeat the same information multiple times
- If the user needs more detail, they can ask follow-up questions"""

        # Construct the full prompt
        full_prompt = f"{system_prompt}\n\nUser question: {user_message}\n\nProvide a helpful, accurate, and empathetic response. IMPORTANT: Keep your response under 100 words and avoid long paragraphs:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Add medical disclaimer
        ai_response = response.text + "\n\n💡 **Medical Disclaimer**: This information is for educational purposes only. Always consult with healthcare professionals for personalized medical advice."
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating AI response content: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

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
        return south_africa_medical_service.format_medical_links_response(resources)
    
    # Check if web search is requested
    if needs_web_search and web_search_service:
        search_results = web_search_service.search_medical_sites(user_message)
        if search_results:
            return web_search_service.format_search_results(search_results, user_message)
    
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
