#!/usr/bin/env python
"""
Ollama Service Test
Demonstrates offline mode using local Ollama LLM
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.ollama_service import OllamaService, DEFAULT_OLLAMA_MODEL


def main():
    """Test Ollama service"""
    
    print("=" * 70)
    print("OLLAMA OFFLINE MODE TEST")
    print("=" * 70)
    
    # Check if Ollama is available
    print("\n🔍 Checking for Ollama service...")
    
    if not OllamaService.is_ollama_available():
        print("""
❌ Ollama is not running!

To use this offline mode, you need to:

1. INSTALL OLLAMA:
   - Download from: https://ollama.ai
   - Or: https://ollama.com
   
2. START OLLAMA:
   - On Windows: Run the Ollama application
   - On Mac: brew install ollama && ollama serve
   - On Linux: curl https://ollama.ai/install.sh | sh
   
3. PULL A MODEL (in a new terminal):
   ollama pull {DEFAULT_OLLAMA_MODEL}

4. VERIFY IT'S RUNNING:
   curl http://localhost:11434/api/tags
   
Then run this test again!
""")
        return
    
    print("✅ Ollama is available!")
    
    # Check available models
    models = OllamaService.get_available_models()
    print(f"\n📦 Available models: {', '.join(models) if models else 'None'}")
    
    if not models:
        print("""
⚠️ No models found in Ollama

Install a model by running:
   ollama pull {DEFAULT_OLLAMA_MODEL}
   
Or try these models:
   ollama pull neural-chat
   ollama pull llama2
   ollama pull openchat
""")
        return
    
    # Test with the configured default local model
    print("\n" + "=" * 70)
    print("Testing Ollama Service")
    print("=" * 70)
    
    service = OllamaService()
    
    test_queries = [
        "What are the top 5 MBA schools?",
        "Show me COVID-19 symptoms",
        "List common medications"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 70)
        
        response = service.generate_response(query)
        
        message = response.get('message', '')
        visualizations = response.get('visualizations', [])
        
        # Show first 150 chars of message
        msg_preview = message[:150] + "..." if len(message) > 150 else message
        print(f"Response: {msg_preview}")
        print(f"Visualizations: {len(visualizations)}")
        
        if visualizations:
            for viz in visualizations:
                print(f"  - {viz.get('type')}: {viz.get('title')}")
    
    print("\n" + "=" * 70)
    print("✅ Ollama offline mode is working!")
    print("=" * 70)


if __name__ == '__main__':
    main()
