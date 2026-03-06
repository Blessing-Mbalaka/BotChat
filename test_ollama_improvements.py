#!/usr/bin/env python
"""
Quick test of Ollama service improvements
Tests timeout handling and error messages
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock requests to avoid import errors
import unittest.mock as mock

print("=" * 60)
print("OLLAMA SERVICE IMPROVEMENTS TEST")
print("=" * 60)

# Test 1: Quick availability check
print("\n[TEST 1] Ollama Availability Check")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    # Simulate Ollama running
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [
        {'name': 'mistral:latest'},
        {'name': 'phi3:mini'},
        {'name': 'tinyllama:latest'},
        {'name': 'gemma3:33b'}  # Slow model - should skip
    ]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        # Change import AFTER mocking
        from health_app.services.ollama_service import OllamaService
        
        service = OllamaService()
        print(f"✅ Ollama Available: {service.available}")
        print(f"✅ Selected Model: {service.model}")
        assert service.available == True, "Should be available"
        assert service.model in ['mistral:latest', 'phi3:mini'], f"Should select fast model, got {service.model}"
        print("✅ TEST 1 PASSED: Fast model selected correctly")

# Test 2: Timeout error handling
print("\n[TEST 2] Timeout Error Handling")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [{'name': 'mistral:latest'}]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("60 second timeout")
        
        from health_app.services.ollama_service import OllamaService
        service = OllamaService()
        result = service.generate_response("Tell me about health")
        
        print(f"Message returned: {result['message'][:50]}...")
        assert "slowly" in result['message'].lower() or "timeout" in result['message'].lower(), \
            "Should mention timeout in error message"
        assert result['visualizations'] == [], "Should have no visualizations"
        print("✅ TEST 2 PASSED: Timeout handled with user-friendly message")

# Test 3: Connection error handling
print("\n[TEST 3] Connection Error Handling")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [{'name': 'mistral:latest'}]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")
        
        from health_app.services.ollama_service import OllamaService
        service = OllamaService()
        result = service.generate_response("test")
        
        print(f"Message returned: {result['message']}")
        assert "Cannot connect" in result['message'] or "running" in result['message'], \
            "Should explain connection error"
        print("✅ TEST 3 PASSED: Connection error handled properly")

# Test 4: 404 Model not found
print("\n[TEST 4] Model Not Found (404) Handling")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [{'name': 'test-model'}]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        mock_response_post = mock.Mock()
        mock_response_post.status_code = 404
        mock_post.return_value = mock_response_post
        
        from health_app.services.ollama_service import OllamaService
        service = OllamaService()
        result = service.generate_response("test")
        
        print(f"Message returned: {result['message']}")
        assert "not found" in result['message'] or "pull" in result['message'].lower(), \
            "Should mention pulling the model"
        print("✅ TEST 4 PASSED: Model not found error handled properly")

# Test 5: JSON response parsing
print("\n[TEST 5] JSON Response Parsing")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [{'name': 'mistral:latest'}]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        mock_response_post = mock.Mock()
        mock_response_post.status_code = 200
        mock_response_post.json.return_value = {
            'response': '{"message": "Health tip: stay hydrated", "visualizations": []}'
        }
        mock_post.return_value = mock_response_post
        
        from health_app.services.ollama_service import OllamaService
        service = OllamaService()
        result = service.generate_response("test")
        
        print(f"Message: {result['message'][:50]}...")
        assert "hydrated" in result['message'], "Should parse JSON response correctly"
        assert "Medical Disclaimer" in result['message'], "Should add disclaimer"
        print("✅ TEST 5 PASSED: JSON response parsed correctly")

# Test 6: Plain text fallback
print("\n[TEST 6] Plain Text Fallback (Non-JSON Response)")
print("-" * 60)

with mock.patch('requests.get') as mock_get:
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'models': [{'name': 'mistral:latest'}]}
    mock_get.return_value = mock_response
    
    with mock.patch('requests.post') as mock_post:
        mock_response_post = mock.Mock()
        mock_response_post.status_code = 200
        mock_response_post.json.return_value = {
            'response': 'This is plain text, not JSON'
        }
        mock_post.return_value = mock_response_post
        
        from health_app.services.ollama_service import OllamaService
        service = OllamaService()
        result = service.generate_response("test")
        
        print(f"Message: {result['message'][:50]}...")
        assert "plain text" in result['message'], "Should handle plain text responses"
        assert "Medical Disclaimer" in result['message'], "Should still add disclaimer"
        print("✅ TEST 6 PASSED: Plain text fallback works")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nKey Improvements:")
print("  • Timeout reduced from 120s to 60s for faster feedback")
print("  • Better model selection: excludes slow models (gemma3:33b, llama2:70b)")
print("  • Specific error messages for 404, timeout, connection errors")
print("  • Handles both JSON and plain text responses")
print("  • Better logging for debugging")
