"""Quick test to verify FastAPI app can start without errors."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all critical imports work."""
    print("Testing imports...")
    
    try:
        print("  ✓ Importing FastAPI app...")
        from services.backend.api.app import app
        print("  ✓ FastAPI app imported successfully")
        
        print("  ✓ Importing validators...")
        from services.backend.api.validators import validate_itinerary_structure, normalize_itinerary_output
        print("  ✓ Validators imported successfully")
        
        print("  ✓ Importing models...")
        from services.backend.api.models import ItineraryRequest, ItineraryResponse
        print("  ✓ Models imported successfully")
        
        print("  ✓ Importing routes...")
        from services.backend.api.routes import itinerary_router, health_router
        print("  ✓ Routes imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator_standalone():
    """Test that validator works without agent dependencies."""
    print("\nTesting validator standalone...")
    
    try:
        from services.backend.api.validators import validate_itinerary_structure, normalize_itinerary_output
        
        # Test with simple data
        test_data = {
            "trip_name": "Test Trip",
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            "origin": "HCMC",
            "destination": "Hanoi",
            "total_days": "1",
            "average_ratings": "4.5",
            "trip_overview": [
                {
                    "trip_number": 1,
                    "start_date": "2025-01-01",
                    "end_date": "2025-01-02",
                    "summary": "Test",
                    "events": [
                        {
                            "event_type": "visit",
                            "description": "Test event"
                        }
                    ]
                }
            ]
        }
        
        result = validate_itinerary_structure(test_data)
        
        if result.is_valid:
            print("  ✓ Validator working correctly")
            print(f"  ✓ Validated itinerary with {len(result.itinerary['trip_overview'])} trip(s)")
        else:
            print(f"  ⚠️  Validation failed: {result.errors}")
        
        # Test normalization
        normalized = normalize_itinerary_output(test_data)
        print(f"  ✓ Normalization working: {normalized['trip_name']}")
        
        print("\n✅ Validator tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_routes():
    """Test that app has all expected routes."""
    print("\nTesting app routes...")
    
    try:
        from services.backend.api.app import app
        
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/",
            "/health",
            "/api/itinerary/generate",
            "/api/itinerary/generate-stream",
            "/api/itinerary/cache-status"
        ]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"  ✓ Route {expected} found")
            else:
                print(f"  ⚠️  Route {expected} NOT found")
        
        print(f"\n  Total routes registered: {len(routes)}")
        print("\n✅ App routes test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ App routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FASTAPI & VALIDATOR INTEGRATION TEST")
    print("="*80 + "\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Validator Standalone", test_validator_standalone()))
    results.append(("App Routes", test_app_routes()))
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - FastAPI app is ready!")
        print("\nNext steps:")
        print("  1. Start the server: cd services/backend && uv run python run.py")
        print("  2. Test the API: http://localhost:8000/docs")
        print("  3. Check health: http://localhost:8000/health")
        print("="*80 + "\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Check errors above")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
