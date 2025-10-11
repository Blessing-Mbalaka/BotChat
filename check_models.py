#!/usr/bin/env python
"""
Check available Gemini models
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    
    print("🤖 Available Gemini Models:")
    print("=" * 40)
    
    try:
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description}")
                print()
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        
    # Test specific model names
    test_models = [
        'gemini-1.5-flash',
        'gemini-2.5-flash', 
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-2.5-flash'
    ]
    
    print("\n🧪 Testing Model Names:")
    print("=" * 40)
    
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"✅ {model_name} - Works!")
        except Exception as e:
            print(f"❌ {model_name} - Error: {str(e)[:100]}...")
            
else:
    print("❌ No API key found")