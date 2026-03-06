#!/usr/bin/env python
"""Direct test of visualization function"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
sys.path.insert(0, 'e:\\Healthcare_Bot')

django.setup()

from health_app.views import generate_ai_response_content

# Test
try:
    result = generate_ai_response_content("visualize top 5 mba schools")
    print("✅ Function succeeded")
    print(f"Message: {result.get('message', '')[:100]}")
    print(f"Visualizations: {len(result.get('visualizations', []))}")
    
    if result.get('visualizations'):
        print(f"First viz: {result['visualizations'][0]}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
