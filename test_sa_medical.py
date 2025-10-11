"""
Test script to demonstrate South African medical resources
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'health_app', 'services'))

from south_africa_medical import south_africa_medical_service

def test_south_african_resources():
    print("🏥 Testing South African Medical Resources Service\n")
    
    # Test queries
    test_queries = [
        "I need to find a doctor in South Africa",
        "Where can I find medical specialists?",
        "Emergency medical services",
        "Hospital information",
        "Medical articles and research"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("=" * 50)
        
        resources = south_africa_medical_service.search_medical_resources(query)
        response = south_africa_medical_service.format_medical_links_response(resources)
        
        print(response)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_south_african_resources()