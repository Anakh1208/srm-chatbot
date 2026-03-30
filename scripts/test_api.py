#!/usr/bin/env python3
"""
API Test Client
--------------
Test the SRM Chatbot API endpoints.

Usage:
    python scripts/test_api.py
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"🧪 {title}")
    print("=" * 70)


def print_response(response: requests.Response):
    """Print formatted response."""
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
    print("\n📄 Response Body:")
    print(json.dumps(response.json(), indent=2))


def test_health():
    """Test the health endpoint."""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
        
        if response.status_code == 200:
            print("\n✅ Health check passed!")
        else:
            print("\n❌ Health check failed!")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("   Make sure the server is running:")
        print("   python scripts/start_api.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True


def test_root():
    """Test the root endpoint."""
    print_section("TEST 2: API Information")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        
        if response.status_code == 200:
            print("\n✅ Root endpoint works!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_stats():
    """Test the stats endpoint."""
    print_section("TEST 3: System Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print_response(response)
        
        if response.status_code == 200:
            print("\n✅ Stats endpoint works!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_chat(query: str):
    """
    Test the chat endpoint.
    
    Args:
        query: Question to ask
    """
    print_section(f"TEST 4: Chat - '{query}'")
    
    try:
        payload = {
            "query": query,
            "conversation_id": "test_conversation_123"
        }
        
        print("\n📤 Request:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 70)
            print("💬 ANSWER:")
            print("=" * 70)
            print(data['answer'])
            
            if data['sources']:
                print("\n📚 SOURCES:")
                for i, source in enumerate(data['sources'], 1):
                    print(f"\n{i}. {source['title']}")
                    print(f"   URL: {source['url']}")
                    print(f"   Score: {source['relevance_score']:.4f}")
            
            print(f"\n📊 Confidence: {data['confidence']}")
            print(f"🔍 Has Context: {data['has_context']}")
            
            print("\n✅ Chat endpoint works!")
        else:
            print("\n❌ Chat request failed!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_invalid_request():
    """Test error handling with invalid request."""
    print_section("TEST 5: Error Handling - Invalid Request")
    
    try:
        # Send invalid data (query is number instead of string)
        payload = {"query": 123}
        
        print("\n📤 Request (invalid):")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print_response(response)
        
        if response.status_code == 422:
            print("\n✅ Error handling works correctly!")
        else:
            print("\n⚠️  Expected status 422, got", response.status_code)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_cors():
    """Test CORS headers."""
    print_section("TEST 6: CORS Headers")
    
    try:
        response = requests.options(
            f"{BASE_URL}/chat",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print("\n📄 CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"   {header}: {value}")
        
        if "access-control-allow-origin" in response.headers:
            print("\n✅ CORS is enabled!")
        else:
            print("\n⚠️  CORS headers not found")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 SRM CHATBOT API - TEST SUITE")
    print("=" * 70)
    print("\nTesting API endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    # Test health first (to check if server is running)
    if not test_health():
        print("\n❌ Server is not running. Exiting...")
        return
    
    # Test other endpoints
    test_root()
    test_stats()
    
    # Test chat with sample questions
    test_chat("What programs does SRM offer?")
    
    # Test error handling
    test_invalid_request()
    
    # Test CORS
    test_cors()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   - Visit http://localhost:8000/docs for interactive testing")
    print("   - Try more queries with the /chat endpoint")
    print("   - Check the logs in the terminal where the server is running")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()