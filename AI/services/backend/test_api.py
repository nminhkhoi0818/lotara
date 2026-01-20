"""
Test script for the Travel Lotara API.

Run locally:
    pip install requests
    python test_api.py

Or with Vercel dev:
    vercel dev &
    python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"  # Change to your Vercel URL after deploy


def test_health():
    """Test health endpoint."""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test root endpoint."""
    print("\nTesting /...")
    response = requests.get(f"{BASE_URL}/")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_plan():
    """Test planning endpoint."""
    print("\nTesting /v1/plan...")
    payload = {
        "user_id": "test-user-123",
        "query": "Plan a 5-day trip to Tokyo with a budget of $3000",
        "constraints": {
            "budget_usd": 3000,
            "duration_days": 5,
            "destination": "Tokyo",
            "interests": ["food", "culture", "technology"]
        }
    }
    response = requests.post(f"{BASE_URL}/v1/plan", json=payload)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_plan_sync():
    """Test synchronous planning endpoint."""
    print("\nTesting /v1/plan/sync...")
    payload = {
        "user_id": "test-user-123",
        "query": "Plan a weekend trip to Paris",
        "constraints": {
            "budget_usd": 1500,
            "duration_days": 3,
            "destination": "Paris",
            "interests": ["art", "food", "romance"]
        }
    }
    response = requests.post(f"{BASE_URL}/v1/plan/sync", json=payload)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_suggest():
    """Test suggestion endpoint."""
    print("\nTesting /v1/suggest...")
    payload = {
        "user_id": "test-user-123",
        "trigger_type": "price_alert",
        "trigger_data": {
            "destination": "Bali",
            "discount_percent": 30,
            "original_price": 1200,
            "sale_price": 840
        }
    }
    response = requests.post(f"{BASE_URL}/v1/suggest", json=payload)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_preferences():
    """Test preferences endpoints."""
    user_id = "test-user-123"
    
    print(f"\nTesting GET /v1/preferences/{user_id}...")
    response = requests.get(f"{BASE_URL}/v1/preferences/{user_id}")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    print(f"\nTesting PUT /v1/preferences/{user_id}...")
    preferences = {
        "travel_style": "adventure",
        "budget_range": {"min": 1000, "max": 5000},
        "preferred_destinations": ["Japan", "Iceland", "New Zealand"]
    }
    response = requests.put(
        f"{BASE_URL}/v1/preferences/{user_id}",
        json=preferences
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 60)
    print("Travel Lotara API Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Plan Trip", test_plan),
        ("Plan Trip (Sync)", test_plan_sync),
        ("Suggest Trip", test_suggest),
        ("User Preferences", test_preferences),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, "PASS" if passed else "FAIL"))
        except Exception as e:
            print(f"  Error: {e}")
            results.append((name, "ERROR"))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, status in results:
        emoji = "✅" if status == "PASS" else "❌"
        print(f"  {emoji} {name}: {status}")


if __name__ == "__main__":
    main()
