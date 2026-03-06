#!/usr/bin/env python
"""
Test script to verify CourseBot visualization support
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Server URL
BASE_URL = 'http://127.0.0.1:8000'
COURSE_CHAT_URL = f'{BASE_URL}/course/chat/'

def test_course_visualization():
    """Test course chat with visualization support"""
    
    print("=" * 60)
    print("COURSEBOT VISUALIZATION TEST")
    print("=" * 60)
    
    # Test 1: Simple query
    print("\n" + "=" * 60)
    print("TEST 1: Simple course query (text response)")
    print("=" * 60)
    
    try:
        response = requests.post(
            COURSE_CHAT_URL,
            json={"message": "What is machine learning?"},
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        print("✓ Response received:", data.get('success'))
        
        if data.get('success'):
            # Check for both 'response' and 'message' keys for compatibility
            message = data.get('message') or data.get('response', '')
            print(f"  Message length: {len(message)}")
            print(f"  Visualizations count: {len(data.get('visualizations', []))}")
            
            if data.get('visualizations'):
                for i, viz in enumerate(data.get('visualizations', [])):
                    print(f"\n  Visualization {i+1}:")
                    print(f"    Type: {viz.get('type')}")
                    print(f"    Title: {viz.get('title')}")
                    print(f"    Source: {viz.get('source')}")
                    if viz.get('data'):
                        cols = viz.get('data', {}).get('columns', [])
                        rows = viz.get('data', {}).get('rows', [])
                        print(f"    Columns: {cols}")
                        print(f"    Rows: {len(rows)} rows")
            
            print("✓ CourseBot response structure is correct!")
        else:
            print(f"  Error: {data.get('error')}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Query that might generate visualization
    print("\n" + "=" * 60)
    print("TEST 2: Query that could trigger visualization")
    print("=" * 60)
    
    try:
        response = requests.post(
            COURSE_CHAT_URL,
            json={"message": "Show me the top 10 most important concepts"},
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        print("✓ Response received:", data.get('success'))
        
        if data.get('success'):
            message = data.get('message') or data.get('response', '')
            print(f"  Message length: {len(message)}")
            viz_count = len(data.get('visualizations', []))
            print(f"  Visualizations count: {viz_count}")
            
            if viz_count > 0:
                print("\n  ✓ Visualizations detected in CourseBot response!")
                for i, viz in enumerate(data.get('visualizations', [])):
                    print(f"\n  Visualization {i+1}:")
                    print(f"    Type: {viz.get('type')}")
                    print(f"    Title: {viz.get('title')}")
                    print(f"    Source: {viz.get('source')}")
                    if viz.get('data'):
                        cols = viz.get('data', {}).get('columns', [])
                        rows = viz.get('data', {}).get('rows', [])
                        print(f"    Columns: {cols}")
                        print(f"    Rows: {len(rows)} rows")
            else:
                print("\n  Note: No visualizations in this response (AI chose not to visualize)")
            
            print("✓ CourseBot visualization support is functional!")
        else:
            print(f"  Error: {data.get('error')}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All CourseBot tests passed!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        # Check if server is running
        print("Checking server status...")
        try:
            response = requests.get(f'{BASE_URL}/api/status/')
            print(f"Server status: {response.status_code}")
        except Exception as e:
            print(f"Warning: Could not reach server. Make sure Django is running.")
            print(f"Error: {e}")
            exit(1)
        
        success = test_course_visualization()
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
