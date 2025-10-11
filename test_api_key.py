#!/usr/bin/env python
"""
Test script to check API key configuration
"""
import os
import sys

# Add the project directory to path
sys.path.append('.')

print("🔍 HealthBot API Key Configuration Test")
print("=" * 50)

# Test 1: Check if .env file exists
env_file_exists = os.path.exists('.env')
print(f"📁 .env file exists: {env_file_exists}")

if env_file_exists:
    with open('.env', 'r') as f:
        env_content = f.read()
    print(f"📄 .env file content preview:\n{env_content[:200]}...")

# Test 2: Try to load with python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded successfully")
except ImportError:
    print("❌ python-dotenv not available")

# Test 3: Check environment variable
api_key = os.getenv('GEMINI_API_KEY')
print(f"\n🔑 API Key Status:")
print(f"   Raw value: {repr(api_key)}")
print(f"   Length: {len(api_key) if api_key else 0}")
print(f"   Starts with 'AIzaSy': {api_key.startswith('AIzaSy') if api_key else False}")
print(f"   Is placeholder: {api_key == 'your_gemini_api_key_here' if api_key else False}")
print(f"   Is example key: {'EXAMPLEKEY' in api_key if api_key else False}")

# Test 4: Try to import Google Generative AI
try:
    import google.generativeai as genai
    print("✅ google-generativeai package available")
    
    # Test 5: Try to configure (only if it looks like a real key)
    if api_key and api_key != 'your_gemini_api_key_here' and 'EXAMPLEKEY' not in api_key:
        try:
            genai.configure(api_key=api_key)
            print("✅ Gemini AI configured successfully")
            
            # Test 6: Try a simple API call
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Hello, this is a test.")
                print("✅ Gemini API call successful")
                print(f"   Response preview: {response.text[:100]}...")
            except Exception as e:
                print(f"❌ Gemini API call failed: {e}")
                
        except Exception as e:
            print(f"❌ Gemini configuration failed: {e}")
    else:
        print("⚠️ API key appears to be placeholder/example - skipping API test")
        
except ImportError:
    print("❌ google-generativeai package not available")

print("\n📋 Summary:")
if api_key and 'EXAMPLEKEY' not in api_key and api_key != 'your_gemini_api_key_here':
    print("🟢 API key appears to be real - should work with Gemini")
else:
    print("🟡 API key appears to be placeholder/example - using demo mode")

print("\n💡 Next steps:")
if not api_key or 'EXAMPLEKEY' in api_key:
    print("1. Get real API key from: https://makersuite.google.com/app/apikey")
    print("2. Replace the GEMINI_API_KEY value in .env file")
    print("3. Restart the Django server")
else:
    print("1. API key looks valid - check server logs for any errors")
    print("2. Make sure Django server is restarted after .env changes")