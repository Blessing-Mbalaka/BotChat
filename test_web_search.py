"""
Test script to demonstrate the enhanced web search functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'health_app', 'services'))

from health_app.services import WebSearchService

def test_web_search():
    print("🔍 Testing Enhanced Web Search Functionality\n")
    
    web_service = WebSearchService()
    
    # Test queries that should trigger web search
    test_queries = [
        "diabetes symptoms articles",
        "high blood pressure research",
        "heart disease treatment studies",
        "covid vaccination information links",
        "mental health resources online"
    ]
    
    for query in test_queries:
        print(f"🔍 Searching for: '{query}'")
        print("=" * 60)
        
        # Perform web search
        search_results = web_service.search_medical_sites(query)
        
        if search_results:
            formatted_response = web_service.format_search_results(search_results, query)
            print(formatted_response)
        else:
            print("No results found.")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_web_search()