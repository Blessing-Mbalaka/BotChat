#!/usr/bin/env python
"""Quick test to check if views module imports correctly"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
sys.path.insert(0, 'e:\\Healthcare_Bot')
django.setup()

print("Testing imports...")

try:
    from health_app.views import generate_ai_response_content
    print("✓ Successfully imported generate_ai_response_content")
    
    # Try calling it
    result = generate_ai_response_content("What is a headache?", "")
    print(f"✓ Function executed")
    print(f"  Result has 'message': {'message' in result}")
    print(f"  Result has 'visualizations': {'visualizations' in result}")
    print(f"  Message: {result.get('message', '')[:100]}...")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
