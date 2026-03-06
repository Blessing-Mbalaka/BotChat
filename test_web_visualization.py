#!/usr/bin/env python
"""
Test script to verify web-based visualization (real data retrieval)
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Server URLs
BASE_URL = 'http://127.0.0.1:8000'
COURSE_CHAT_URL = f'{BASE_URL}/course/chat/'
CHAT_URL = f'{BASE_URL}/chat/'

def test_web_visualization():
    """Test web-based visualization requests"""
    
    print("=" * 70)
    print("WEB-BASED VISUALIZATION TEST (Real Data via Web Search)")
    print("=" * 70)
    
    test_queries = [
        {
            "query": "visualise top 10 mba schools in south africa",
            "endpoint": COURSE_CHAT_URL,
            "name": "CourseBot - MBA Schools"
        },
        {
            "query": "show top 10 universities by ranking",
            "endpoint": COURSE_CHAT_URL,
            "name": "CourseBot - University Rankings"
        },
        {
            "query": "visualise most common symptoms of covid-19",
            "endpoint": CHAT_URL,
            "name": "HealthBot - COVID Symptoms"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'=' * 70}")
        print(f"Query: {test['query']}")
        
        try:
            response = requests.post(
                test['endpoint'],
                json={"message": test['query']},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            data = response.json()
            
            if not data.get('success'):
                print(f"✗ Error: {data.get('error')}")
                continue
            
            print(f"✓ Response received")
            
            message = data.get('message') or data.get('response', '')
            visualizations = data.get('visualizations', [])
            
            print(f"  Message: {message[:150]}...")
            print(f"  Visualizations: {len(visualizations)}")
            
            if visualizations:
                for j, viz in enumerate(visualizations, 1):
                    viz_type = viz.get('type')
                    title = viz.get('title')
                    source = viz.get('source')
                    rows = len(viz.get('data', {}).get('rows', []))
                    
                    print(f"\n  📊 Visualization {j}:")
                    print(f"     Type: {viz_type}")
                    print(f"     Title: {title}")
                    print(f"     Source: {source}")
                    print(f"     Data rows: {rows}")
                    
                    # Check if it's real data (not all generic values)
                    if viz.get('data', {}).get('rows'):
                        sample_rows = viz.get('data', {}).get('rows')[:3]
                        print(f"     Sample data:")
                        for row in sample_rows:
                            print(f"       - {row}")
                    
                    # Determine if web search was successful
                    is_web_data = source == 'extracted' and rows > 0
                    if is_web_data:
                        print(f"     ✓ Real/Web data detected!")
                    else:
                        print(f"     Note: Synthetic data (no web source match)")
            else:
                print("  No visualizations in response")
                
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout (30s) - server may be slow")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'=' * 70}")
    print("✓ Web visualization tests complete!")
    print("=" * 70)
    print("\nNOTE: Web search functionality:")
    print("- First attempts to fetch real data from web search")
    print("- Falls back to synthetic data if web search fails")
    print("- Check server logs for 'Web search' messages to see what's happening")

if __name__ == '__main__':
    try:
        # Check server status
        print("Checking server status...")
        try:
            response = requests.get(f'{BASE_URL}/api/status/', timeout=5)
            print(f"Server status: {response.status_code}\n")
        except Exception as e:
            print(f"Warning: Server may not be ready. Error: {e}\n")
        
        test_web_visualization()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
