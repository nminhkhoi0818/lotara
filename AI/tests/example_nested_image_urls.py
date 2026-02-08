"""
Example: Using Nested Image URLs from Milvus
============================================
This script demonstrates how to access and use the new image_url fields
in places, cuisines, and hotels from Milvus retrieval results.

Usage:
    python tests/example_nested_image_urls.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.travel_lotara.tools.shared_tools.milvus_engine import search_locations
from src.travel_lotara.config.logging_config import get_logger

logger = get_logger(__name__)


def display_location_with_images(location):
    """Display a location with all its image URLs."""
    print("\n" + "=" * 80)
    print(f"📍 {location.get('Location name', 'Unknown')} ({location.get('Location', 'Unknown')})")
    print("=" * 80)
    
    # Main location image
    main_image = location.get('Image', '')
    if main_image:
        print(f"\n🖼️  Main Attraction Image:")
        print(f"   {main_image}")
    
    # Destinations (Places and Cuisines)
    destinations = location.get('Destinations', [])
    if destinations:
        print(f"\n📌 Destinations ({len(destinations)} items):")
        for i, dest in enumerate(destinations, 1):
            print(f"\n   Destination {i}:")
            
            # Place with image
            place = dest.get('place', {})
            if place:
                place_name = place.get('name', 'N/A')
                place_image = place.get('image_url', '')
                print(f"   🏛️  Place: {place_name}")
                if place_image:
                    print(f"      Image: {place_image}")
                else:
                    print(f"      Image: (not available)")
                print(f"      Budget: {place.get('budget', 'N/A')}")
                print(f"      Duration: {place.get('average_timespan', 'N/A')}")
            
            # Cuisine with image
            cuisine = dest.get('cuisine', {})
            if cuisine:
                cuisine_name = cuisine.get('name', 'N/A')
                cuisine_image = cuisine.get('image_url', '')
                print(f"   🍽️  Cuisine: {cuisine_name}")
                if cuisine_image:
                    print(f"      Image: {cuisine_image}")
                else:
                    print(f"      Image: (not available)")
                print(f"      Budget: {cuisine.get('budget', 'N/A')}")
                print(f"      Duration: {cuisine.get('average_timespan', 'N/A')}")
    
    # Hotels
    hotels = location.get('Hotels', [])
    if hotels:
        print(f"\n🏨 Hotels ({len(hotels)} options):")
        for i, hotel in enumerate(hotels, 1):
            hotel_name = hotel.get('name', 'N/A')
            hotel_image = hotel.get('image_url', '')
            hotel_cost = hotel.get('cost', 'N/A')
            hotel_reviews = hotel.get('reviews', 'N/A')
            
            print(f"\n   Hotel {i}: {hotel_name}")
            if hotel_image:
                print(f"   Image: {hotel_image}")
            else:
                print(f"   Image: (not available)")
            print(f"   Cost: {hotel_cost} | Reviews: {hotel_reviews}")
    
    # Activities
    activities = location.get('Activities', [])
    if activities:
        print(f"\n🎯 Activities ({len(activities)} items):")
        for activity in activities[:5]:  # Show first 5
            print(f"   • {activity}")
        if len(activities) > 5:
            print(f"   ... and {len(activities) - 5} more")


def build_itinerary_event_with_images(location, event_type='visit'):
    """
    Example: How to build an itinerary event with appropriate image URLs.
    
    This demonstrates the logic that the planning agent should use.
    """
    print(f"\n🔧 Building {event_type} event from RAG data...")
    
    event = {
        "type": event_type,
        "location_name": "",
        "image_url": None,
        "description": "",
        "budget_usd": 0
    }
    
    if event_type == "visit":
        # For visit events, use main location image
        event["location_name"] = location.get('Location name', '')
        event["image_url"] = location.get('Image', None)
        event["description"] = location.get('Description', '')[:100] + "..."
        
        # Could also use a specific place image from Destinations
        destinations = location.get('Destinations', [])
        if destinations and destinations[0].get('place'):
            place = destinations[0]['place']
            place_image = place.get('image_url', '')
            if place_image:
                print(f"   Note: Specific place image also available: {place_image[:50]}...")
    
    elif event_type == "meal":
        # For meal events, use cuisine image from Destinations
        destinations = location.get('Destinations', [])
        if destinations and destinations[0].get('cuisine'):
            cuisine = destinations[0]['cuisine']
            event["location_name"] = cuisine.get('name', 'Restaurant')
            event["image_url"] = cuisine.get('image_url', None) or None
            event["budget_usd"] = 15  # Example conversion from budget tier
            event["description"] = f"Dining at {cuisine.get('name', 'local restaurant')}"
    
    elif event_type == "hotel_checkin":
        # For hotel events, use hotel image
        hotels = location.get('Hotels', [])
        if hotels:
            hotel = hotels[0]  # Take first hotel as example
            event["location_name"] = hotel.get('name', 'Hotel')
            event["image_url"] = hotel.get('image_url', None) or None
            event["budget_usd"] = 80  # Example conversion from cost tier
            event["description"] = f"Check-in at {hotel.get('name', 'hotel')}"
    
    print(f"   ✅ Event created:")
    print(f"      Location: {event['location_name']}")
    print(f"      Image: {event['image_url'][:50] if event['image_url'] else 'None'}...")
    print(f"      Description: {event['description']}")
    
    return event


def main():
    """Main demonstration."""
    logger.info("=" * 80)
    logger.info("DEMONSTRATION: Using Nested Image URLs from Milvus")
    logger.info("=" * 80)
    
    # Search for cultural locations
    logger.info("\n🔍 Searching for cultural attractions in Ninh Binh...")
    results = search_locations("cultural attractions temples in Ninh Binh", top_k=2)
    
    if not results:
        logger.error("No results found! Make sure Milvus is set up.")
        logger.info("\nRun this first:")
        logger.info("  python -m src.travel_lotara.tools.shared_tools.setup_milvus")
        return
    
    # Display first result with all images
    display_location_with_images(results[0])
    
    # Demonstrate building itinerary events
    print("\n" + "=" * 80)
    print("🛠️  DEMONSTRATION: Building Itinerary Events")
    print("=" * 80)
    
    location = results[0]
    
    # Build different event types
    visit_event = build_itinerary_event_with_images(location, 'visit')
    meal_event = build_itinerary_event_with_images(location, 'meal')
    hotel_event = build_itinerary_event_with_images(location, 'hotel_checkin')
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ SUMMARY")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. Main attraction images: location['Image']")
    print("2. Specific place images: location['Destinations'][n]['place']['image_url']")
    print("3. Restaurant images: location['Destinations'][n]['cuisine']['image_url']")
    print("4. Hotel images: location['Hotels'][n]['image_url']")
    print("\nThese fields are now available in all Milvus retrieval results!")
    print("Use them to create visually rich itineraries with specific images for each venue.")
    print("=" * 80)


if __name__ == "__main__":
    main()

    # uv run tests/example_nested_image_urls.py
