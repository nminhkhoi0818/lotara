"""Simple client example for Lotara Travel Agent API."""

import requests
import json
from typing import Dict, Any


class LotaraClient:
    """Client for interacting with Lotara Travel Agent API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client with base URL."""
        self.base_url = base_url
        self.timeout = 180  # 3 minutes
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def generate_itinerary(
        self,
        user_id: str,
        duration: str = "medium",
        companions: str = "solo",
        budget: str = "midrange",
        travel_style: str = "cultural",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a travel itinerary.
        
        Args:
            user_id: User identifier
            duration: Trip duration (short|medium|long|extended)
            companions: Traveler type (solo|couple|family_kids|family_adults|friends)
            budget: Budget level (budget|midrange|comfortable|luxury)
            travel_style: Travel style (adventure|cultural|nature|food|wellness|photography)
            **kwargs: Additional optional parameters
        
        Returns:
            Itinerary response dictionary
        """
        payload = {
            "userId": user_id,
            "duration": duration,
            "companions": companions,
            "budget": budget,
            "travelStyle": travel_style,
            "pace": kwargs.get("pace", "balanced"),
            "activity": kwargs.get("activity", "medium"),
            "crowds": kwargs.get("crowds", "mixed"),
            "accommodation": kwargs.get("accommodation", "standard"),
            "remote": kwargs.get("remote", False),
            "timing": kwargs.get("timing", "flexible"),
        }
        
        print(f"🚀 Generating itinerary for user {user_id}...")
        print(f"   Duration: {duration}")
        print(f"   Style: {travel_style}")
        print(f"   Budget: {budget}")
        print(f"\n⏳ This may take 30-120 seconds...\n")
        
        response = requests.post(
            f"{self.base_url}/api/itinerary/generate",
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            print("✅ Itinerary generated successfully!")
            return response.json()
        else:
            print(f"❌ Request failed with status {response.status_code}")
            response.raise_for_status()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = LotaraClient()
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"✅ API Status: {health['status']}")
    print(f"   Model: {health['model']}")
    print(f"   Version: {health['version']}\n")
    
    # Generate itinerary
    try:
        result = client.generate_itinerary(
            user_id="demo-user",
            duration="short",
            companions="solo",
            budget="budget",
            travel_style="cultural",
            pace="balanced",
            activity="medium"
        )
        
        # Display results
        itinerary = result.get("itinerary", {})
        print(f"\n📋 Itinerary Summary:")
        print(f"   Trip: {itinerary.get('trip_name', 'N/A')}")
        print(f"   Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}")
        print(f"   Duration: {itinerary.get('total_days')} days")
        print(f"   Session: {result['session_id']}")
        
        # Save to file
        with open("example_itinerary.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full itinerary saved to: example_itinerary.json")
        
    except requests.Timeout:
        print("⏰ Request timed out. The API might be overloaded.")
    except requests.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response.status_code == 503:
            print("   The AI service is temporarily overloaded. Try again in a few minutes.")
        elif e.response.status_code == 429:
            print("   Rate limit exceeded. Wait a moment and try again.")
    except Exception as e:
        print(f"❌ Error: {e}")
