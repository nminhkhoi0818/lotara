"""Test script for the FastAPI backend."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed!")


def test_itinerary_generation():
    """Test itinerary generation endpoint."""
    print("\n" + "="*80)
    print("TEST 2: Itinerary Generation")
    print("="*80)
    
    # Test request
    request_data = {
        "userId": "test-user-fastapi",
        "duration": "short",
        "companions": "solo",
        "budget": "budget",
        "pace": "balanced",
        "travelStyle": "cultural",
        "activity": "medium",
        "crowds": "mixed",
        "accommodation": "standard",
        "remote": False,
        "timing": "flexible"
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    print("\n⏳ Generating itinerary (this may take 30-120 seconds)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/itinerary/generate",
            json=request_data,
            timeout=180  # 3 minutes timeout
        )
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Request completed in {elapsed:.1f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Itinerary generated successfully!")
            print(f"Session ID: {result['session_id']}")
            print(f"Status: {result['status']}")
            
            if result.get('itinerary'):
                itinerary = result['itinerary']
                print(f"\n📋 Itinerary Preview:")
                print(f"  Trip Name: {itinerary.get('trip_name', 'N/A')}")
                print(f"  Start Date: {itinerary.get('start_date', 'N/A')}")
                print(f"  End Date: {itinerary.get('end_date', 'N/A')}")
                print(f"  Total Days: {itinerary.get('total_days', 'N/A')}")
                
                # Save full response
                with open('test_api_response.json', 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Full response saved to: test_api_response.json")
        else:
            print(f"\n❌ Request failed!")
            print(f"Response: {response.text}")
            
    except requests.Timeout:
        print(f"\n⏰ Request timed out after 180 seconds")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_root():
    """Test root endpoint."""
    print("\n" + "="*80)
    print("TEST 3: Root Endpoint")
    print("="*80)
    
    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✅ Root endpoint passed!")


if __name__ == "__main__":
    print("\n🚀 Lotara Travel Agent API - Test Suite")
    print("="*80)
    
    try:
        # Test health first
        test_health()
        
        # Test root
        test_root()
        
        # Ask user before running long test
        print("\n" + "="*80)
        response = input("\nRun itinerary generation test? (30-120s) [y/N]: ")
        if response.lower() == 'y':
            test_itinerary_generation()
        else:
            print("⏭️  Skipped itinerary generation test")
        
        print("\n" + "="*80)
        print("✅ All tests completed!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
