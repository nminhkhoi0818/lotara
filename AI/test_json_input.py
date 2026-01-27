"""Test the agent with backend JSON input."""

import asyncio
import json
from src.travel_lotara.main import run_agent
from src.travel_lotara.tracking import flush_traces


async def test_backend_input():
    # Backend JSON input
    backend_json = {
        "userId": "test-user-123",
        "duration": "medium",
        "companions": "solo",
        "budget": "midrange",
        "pace": "balanced",
        "travelStyle": "cultural",
        "activity": "medium",
        "crowds": "mixed",
        "accommodation": "standard",
        "remote": False,
        "timing": "flexible"
    }

    backend_json_test = {
        "userId": "test-user-123",
        "duration": "long",
        "companions": "solo",
        "budget": "luxury",
        "pace": "fast",
        "travelStyle": "cultural",
        "activity": "high",
        "crowds": "mixed",
        "accommodation": "premium",
        "remote": False,
        "timing": "flexible",
    }

    ###################################################
    # Testing more detailed input
    backend_json_input_1 = {
        "userId": "test-user-456",
        "duration": "long",
        "companions": "family",
        "budget": "luxury",
        "pace": "relaxed",
        "travelStyle": "adventure",
        "activity": "high",
        "crowds": "low",
        "accommodation": "premium",
        "remote": True,
        "timing": "fixed",
        "origin": "Los Angeles, USA",
        "destination": "New Zealand",
        "startDate": "2024-12-15",
        "endDate": "2025-01-05",
        "interests": ["hiking", "wildlife", "scenic drives"],
        "specialRequirements": ["wheelchair accessible accommodation"]
    }

    ###############################################
    # Testing less detailed input
    backend_json_input_2 = {
        "userId": "test-user-789",
        "destination": "New Zealand",
        "startDate": "2024-12-15",
        "endDate": "2025-01-05",
        "interests": ["hiking", "wildlife", "scenic drives"],
        "specialRequirements": ["wheelchair accessible accommodation"]
    }

    ###############################################
    # Testing no destination
    backend_json_input_3 = {
        "userId": "test-user-789",
        "duration": "short",
        "companions": "couple",
        "travelStyle": "budget",
        "budget": "low",
        "interests": ["food", "culture"],
        "pace": "relaxed"
    }

    ###############################################
    # Testing no destination
    backend_json_input_4 = {
        "userId": "test-user-789123",
        "duration": "medium",
        "companions": "family",
        "travelStyle": "balanced",
        "budget": "medium",
        "interests": ["nature", "adventure", "family-friendly"],
        "pace": "moderate",
        "specialRequirements": "kid-friendly activities"
    }

    ###############################################
    #  Luxury Solo Travel (Extended Trip)
    backend_json_input_5 = {
        "userId": "test-user-789123",
        "duration": "long",
        "companions": "solo",
        "travelStyle": "luxury",
        "budget": "high",
        "interests": ["wellness", "culture", "shopping"],
        "pace": "relaxed",
        "specialRequirements": "spa and fine dining"
    }

    ###############################################
    #  Adventure Group Trip
    backend_json_input_6 = {
        "userId": "test-user-789123",
        "duration": "medium",
        "companions": "group",
        "travelStyle": "adventure",
        "budget": "medium",
        "interests": ["adventure", "nature", "nightlife"],
        "pace": "fast",
        "specialRequirements": "outdoor activities, hiking"
    }

    ###############################################
    #  Minimal Test (Edge Case)
    backend_json_input_7 = {
        "userId": "test-user-789123",
        "duration": "short",
        "companions": "solo",
        "travelStyle": "budget",
        "budget": "low"
    }


    ###############################################
    #  Foodie Tour
    backend_json_input_8 = {
        "userId": "test-user-789123",
        "duration": "short",
        "companions": "couple",
        "travelStyle": "balanced",
        "budget": "medium",
        "interests": ["food", "culture", "cooking"],
        "pace": "relaxed",
        "specialRequirements": "cooking classes, food tours, local markets"
    }



    ############################################
    #  Business + Leisure
    backend_json_input_9 = {
        "userId": "test-user-789123",
        "duration": "short",
        "companions": "solo",
        "travelStyle": "balanced",
        "budget": "medium",
        "interests": ["culture", "food", "shopping"],
        "pace": "fast",
        "specialRequirements": "business-friendly hotels, good wifi"
    }

    ############################################
    #  Romantic Honeymoon
    backend_json_input_10 = {
        "userId": "test-user-789123",
        "duration": "medium",
        "companions": "couple",
        "travelStyle": "luxury",
        "budget": "high",
        "interests": ["romance", "beaches", "wellness"],
        "pace": "relaxed",
        "specialRequirements": "romantic dinners, private tours"
    }

    backend_json = backend_json_input_7  # Change this to test different inputs
    
    print("\nLotara Travel Assistant - Backend JSON Test")
    print(f"Backend Input: {json.dumps(backend_json, indent=2)}\n")
    
    try:
        response = await run_agent(
            user_input="",
            user_id=backend_json.get("userId"),
            backend_json=backend_json,
        )
        print("\nResponse:\n")
        print(response)
        print("\n" + "="*80)
        
    except Exception as e:
        import traceback
        print(f"\n[ERROR] {e}")
        traceback.print_exc()
    finally:
        flush_traces()


if __name__ == "__main__":
    asyncio.run(test_backend_input())


    # uv run test_json_input.py
