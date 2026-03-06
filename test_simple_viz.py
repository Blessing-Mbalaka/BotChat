#!/usr/bin/env python
"""Simple test to check visualization endpoint"""

import requests
import json
import time

time.sleep(1)  # Wait for server to start

url = 'http://127.0.0.1:8000/chat/'

test_queries = [
    "visualize top 5 mba schools",
    "show covid symptoms",
    "what is fever",
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    try:
        response = requests.post(
            url,
            json={"message": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message', '')[:100]}...")
        print(f"Visualizations: {len(data.get('visualizations', []))}")
        
        if data.get('visualizations'):
            for viz in data['visualizations']:
                print(f"  - {viz.get('type')}: {viz.get('title')}")
                print(f"    Data rows: {len(viz.get('data', {}).get('rows', []))}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

print("\n" + "="*60)
print("Test complete")
