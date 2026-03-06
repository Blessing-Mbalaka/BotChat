#!/usr/bin/env python
"""Check if the new API key is loaded"""

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {api_key[:30]}..." if api_key else "API Key not found")
print(f"Full key: {api_key}")
