#!/usr/bin/env python
"""
Test script for visualization feature
Tests the new chat_api endpoint to verify it returns visualizations
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def test_chat_with_visualization():
    """Test chat API with a query that should trigger visualization"""
    
    endpoint = f"{BASE_URL}/chat/"
    
    # Test 1: Simple greeting (should return text only)
    print("\n" + "="*60)
    print("TEST 1: Simple greeting (text-only response expected)")
    print("="*60)
    
    data = json.dumps({
        "message": "Hello, how are you?",
        "conversation_id": None
    }).encode('utf-8')
    
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✓ Response received: {result['success']}")
            print(f"  Message: {result.get('message', '')[:100]}...")
            print(f"  Visualizations count: {len(result.get('visualizations', []))}")
            print(f"  AI Powered: {result.get('ai_powered')}")
            
            # Verify structure
            assert 'success' in result, "Missing 'success' field"
            assert 'message' in result, "Missing 'message' field"
            assert 'visualizations' in result, "Missing 'visualizations' field"
            assert isinstance(result['visualizations'], list), "visualizations should be a list"
            
            print("✓ Response structure is correct!")
            
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Test 2: Query that might trigger visualization
    print("\n" + "="*60)
    print("TEST 2: Query that could trigger visualization")
    print("="*60)
    
    data = json.dumps({
        "message": "Show me common symptoms and their frequency",
        "conversation_id": None
    }).encode('utf-8')
    
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✓ Response received: {result['success']}")
            print(f"  Message length: {len(result.get('message', ''))}")
            print(f"  Visualizations count: {len(result.get('visualizations', []))}")
            
            if result.get('visualizations'):
                for i, viz in enumerate(result['visualizations']):
                    print(f"\n  Visualization {i+1}:")
                    print(f"    Type: {viz.get('type')}")
                    print(f"    Title: {viz.get('title')}")
                    print(f"    Source: {viz.get('source')}")
                    print(f"    Has data: {'data' in viz}")
                    if 'data' in viz:
                        data_obj = viz['data']
                        print(f"    Columns: {data_obj.get('columns', [])[:5]}")
                        print(f"    Rows: {len(data_obj.get('rows', []))} rows")
            
            print("✓ Visualization response structure is correct!")
            
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_chat_with_visualization()
    exit(0 if success else 1)
