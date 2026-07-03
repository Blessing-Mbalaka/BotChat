"""
Ollama Service - Local LLM for offline mode
Uses locally running Ollama instance for AI responses when Gemini API is unavailable
"""

import json
import logging
import requests
import shutil
import os
from typing import Dict, Any, Optional
from .bot_config import BotConfigManager

logger = logging.getLogger(__name__)
DEFAULT_OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'ministral-3:3b')


def get_system_resources() -> Dict[str, Any]:
    """
    Get current system resource information (RAM, disk space)
    Helps diagnose 500 errors caused by resource constraints
    """
    try:
        # Get memory info (cross-platform)
        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_info = {
                'total_gb': round(mem.total / (1024**3), 2),
                'available_gb': round(mem.available / (1024**3), 2),
                'percent_used': mem.percent
            }
        except ImportError:
            ram_info = {'note': 'psutil not installed'}
        
        # Get disk space
        try:
            disk = shutil.disk_usage('/')
            disk_info = {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent_used': round((disk.used / disk.total) * 100, 1)
            }
        except Exception as e:
            disk_info = {'error': str(e)}
        
        return {'ram': ram_info, 'disk': disk_info}
    except Exception as e:
        return {'error': str(e)}


class OllamaService:
    """Service to generate responses using local Ollama LLM"""
    
    def __init__(self, model: str = None, base_url: str = 'http://localhost:11434'):
        """
        Initialize Ollama service
        
        Args:
            model: Ollama model name (default: local configured model or auto-detect)
            base_url: Base URL of Ollama server (default: localhost:11434)
        """
        self.base_url = base_url
        self.available = self._check_availability()
        
        if self.available:
            # Auto-detect best model if not specified
            if not model:
                available_models = self.get_available_models(base_url)
                if available_models:
                    if DEFAULT_OLLAMA_MODEL in available_models:
                        model = DEFAULT_OLLAMA_MODEL
                    else:
                        model = self._select_best_model(available_models)
                else:
                    model = DEFAULT_OLLAMA_MODEL
            
            self.model = model
            logger.info(f"✅ Ollama service initialized with model: {model}")
        else:
            self.model = model or DEFAULT_OLLAMA_MODEL
            logger.warning(f"⚠️ Ollama not available at {base_url}")
    
    def _check_availability(self) -> bool:
        """Check if Ollama server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {str(e)}")
            return False
    
    def _select_best_model(self, available_models: list) -> str:
        """Select the best model from available list"""
        # Prefer fast, reliable models
        fast_models = [DEFAULT_OLLAMA_MODEL, 'phi3:mini', 'phi3:2.7b', 'mistral', 'neural-chat', 'tinyllama']
        slow_models = ['gemma3:33b', 'llama2:70b', 'neural-chat:13b']
        
        # Skip very slow models
        safe_models = [m for m in available_models 
                      if not any(skip in m.lower() for skip in slow_models)]
        
        # Prefer fast models
        for fast in fast_models:
            for model in safe_models:
                if fast.lower() in model.lower():
                    logger.info(f"Selected fast model: {model}")
                    return model
        
        # If no fast model found, use any safe model
        if safe_models:
            logger.info(f"Using model: {safe_models[0]}")
            return safe_models[0]
        
        # Last resort - use first available
        if available_models:
            logger.warning(f"Using available model: {available_models[0]}")
            return available_models[0]
        
        return DEFAULT_OLLAMA_MODEL
    
    def generate_response(self, user_message: str) -> Dict[str, Any]:
        """
        Generate AI response using Ollama with visualization support
        
        Args:
            user_message: User's input message
            
        Returns:
            Dictionary with 'message' and 'visualizations' keys
        """
        if not self.available:
            return {
                'message': "Ollama service is not running. Please start Ollama first.",
                'visualizations': []
            }
        
        try:
            # Get system prompt from active configuration
            system_prompt = BotConfigManager.get_ollama_prompt()

            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nJSON Response:"
            
            logger.info(f"📤 Calling Ollama ({self.model})...")
            
            # Try generate endpoint (most compatible)
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "top_p": 0.95,
                    },
                    timeout=60  # Reduced from 120 to 60 seconds
                )
                
                if response.status_code == 200:
                    response_text = response.json().get('response', '').strip()
                elif response.status_code == 404:
                    logger.error(f"Model '{self.model}' not found. Available: {self.get_available_models()}")
                    return {
                        'message': f"Model not found. Try: ollama pull {self.model}",
                        'visualizations': []
                    }
                elif response.status_code == 500:
                    # Internal server error - resource or model issue
                    logger.error(f"❌ Ollama 500 Internal Server Error")
                    logger.error(f"Model: {self.model}")
                    logger.error(f"Response: {response.text[:200]}")
                    resources = get_system_resources()
                    logger.error(f"System Resources: {resources}")
                    
                    # Check what might have caused the error
                    error_text = response.text.lower()
                    is_oom = 'out of memory' in error_text or 'oom' in error_text or 'cuda' in error_text
                    
                    # Get resource details
                    ram = resources.get('ram', {})
                    disk = resources.get('disk', {})
                    ram_pct = ram.get('percent_used', 0) if isinstance(ram, dict) else 0
                    disk_pct = disk.get('percent_used', 0) if isinstance(disk, dict) else 0
                    
                    # Build diagnostic message
                    msg = "Ollama crashed (Error 500)\n\n"
                    msg += "📊 System Status:\n"
                    
                    if isinstance(ram, dict) and 'percent_used' in ram:
                        msg += f"  RAM: {ram['percent_used']}% used ({ram.get('available_gb', '?')}GB available)\n"
                    if isinstance(disk, dict) and 'percent_used' in disk:
                        msg += f"  Disk: {disk['percent_used']}% used ({disk.get('free_gb', '?')}GB free)\n"
                    
                    msg += "\n🔧 Solutions:\n"
                    
                    if is_oom or ram_pct > 85:
                        msg += "  1️⃣ RAM Problem Detected!\n"
                        msg += "     • Close other applications\n"
                        msg += "     • Use smaller model: ollama pull phi3:mini\n"
                        msg += "     • Increase available RAM\n"
                    elif disk_pct > 90:
                        msg += "  1️⃣ Disk Space issue!\n"
                        msg += "     • Free up disk space\n"
                        msg += "     • Remove old Ollama models\n"
                    else:
                        msg += "  1️⃣ Model crashed (unknown reason)\n"
                        msg += "     • Try: ollama rm {self.model}\n"
                        msg += "     • Reinstall: ollama pull {self.model}\n"
                    
                    msg += "  2️⃣ Restart Ollama\n"
                    msg += "     • Stop Ollama\n"
                    msg += "     • Run: ollama serve\n"
                    msg += "  3️⃣ Try different model\n"
                    msg += "     • ollama pull phi3:mini (fastest)\n"
                    msg += "     • ollama pull mistral (balanced)\n"
                    
                    return {'message': msg, 'visualizations': []}
                else:
                    logger.error(f"❌ Ollama API error {response.status_code}")
                    logger.error(f"Response: {response.text[:200]}")
                    return {
                        'message': f"Ollama error {response.status_code}. Try restarting: ollama serve",
                        'visualizations': []
                    }
            
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Ollama timeout (60s) - model may be slow or system overloaded")
                return {
                    'message': "Ollama is responding slowly. This might be a Large model or system overload. Try again (may be faster on second attempt).",
                    'visualizations': []
                }
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to Ollama at {self.base_url}")
                return {
                    'message': f"Cannot connect to Ollama. Is it running at {self.base_url}?",
                    'visualizations': []
                }
            
            if not response_text:
                logger.warning("Empty response from Ollama")
                return {
                    'message': "Ollama returned empty response. Try again.",
                    'visualizations': []
                }
            
            logger.info(f"📥 Got response ({len(response_text)} chars)")
            
            # Try to parse as JSON
            try:
                # Clean up markdown code blocks if present
                cleaned = response_text
                if '```' in cleaned:
                    parts = cleaned.split('```')
                    if len(parts) >= 2:
                        cleaned = parts[1]
                        if cleaned.startswith('json'):
                            cleaned = cleaned[4:]
                
                cleaned = cleaned.strip()
                parsed = json.loads(cleaned)
                
                # Extract message and visualizations
                message = parsed.get('message', '').strip()
                visualizations = parsed.get('visualizations', [])
                
                if not isinstance(visualizations, list):
                    visualizations = []
                
                # Add disclaimer
                if message:
                    message += "\n\n💡 **Medical Disclaimer**: For professional medical advice, consult a healthcare provider."
                
                logger.info("✅ Successfully parsed Ollama response")
                return {
                    'message': message or "I'm here to help with health questions.",
                    'visualizations': visualizations
                }
            
            except json.JSONDecodeError:
                logger.warning(f"Response not valid JSON. Returning as text.")
                # Return response as plain text fallback
                return {
                    'message': response_text[:500] + "\n\n💡 **Medical Disclaimer**: For professional medical advice, consult a healthcare provider.",
                    'visualizations': []
                }
        
        except Exception as e:
            logger.error(f"Ollama service error: {str(e)}")
            return {
                'message': "Error using Ollama service. Please try again.",
                'visualizations': []
            }
    
    @staticmethod
    def is_ollama_available(base_url: str = 'http://localhost:11434') -> bool:
        """Check if Ollama is running (static method for quick checks)"""
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    def get_available_models(base_url: str = 'http://localhost:11434') -> list:
        """Get list of available models in Ollama"""
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                return [m.get('name', '') for m in models]
            return []
        except Exception as e:
            logger.debug(f"Could not get Ollama models: {str(e)}")
            return []


def create_ollama_service(model: str = DEFAULT_OLLAMA_MODEL) -> Optional[OllamaService]:
    """
    Factory function to create Ollama service if available
    
    Args:
        model: Ollama model to use
        
    Returns:
        OllamaService instance or None if Ollama is not available
    """
    service = OllamaService(model=model)
    if service.available:
        return service
    return None
