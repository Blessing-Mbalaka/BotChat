"""
Test script to demonstrate the concise responses from the health chatbot
"""

import requests
import json

def test_concise_responses():
    """Test various queries to show concise response format"""
    
    chat_url = "http://127.0.0.1:8000/chat/"
    
    test_questions = [
        "I have a fever, what should I do?",
        "Find me a doctor in South Africa",
        "What helps with headaches?",
        "Tell me about cough treatment",
        "I have chest pain"
    ]
    
    print("🧪 Testing Concise Health Chatbot Responses")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 40)
        
        try:
            response = requests.post(chat_url, 
                json={'message': question},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    bot_response = result['response']
                    word_count = len(bot_response.split())
                    print(f"✅ Response ({word_count} words):")
                    print(bot_response)
                    
                    # Check if response includes South African resources
                    if "south africa" in question.lower() and ("🏥" in bot_response or "doctor" in bot_response.lower()):
                        print("🌍 Includes South African medical resources!")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")
    
    print(f"\n{'=' * 50}")
    print("✅ Test completed! Notice how responses are now much more concise.")
    print("🌍 Try asking about doctors in South Africa to see medical resources!")
    print(f"🌐 Visit: http://127.0.0.1:8000/ to test interactively")

if __name__ == "__main__":
    test_concise_responses()