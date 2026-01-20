"""
Travel Data Fixtures - Mock but Realistic Data

Provides realistic mock data for flights, hotels, and activities
to enable end-to-end testing without real API integrations.
"""

from datetime import datetime, timedelta
from typing import Any


def get_flight_fixtures(origin: str, destination: str) -> list[dict[str, Any]]:
    """Get mock flight data for common routes."""
    
    # Normalize city codes
    origin = origin.upper()[:3]
    destination = destination.upper()[:3]
    
    routes = {
        ("JFK", "HND"): [  # NYC to Tokyo
            {
                "airline": "JAL",
                "flight_number": "JAL5",
                "route": "JFK → HND (nonstop)",
                "departure": "18:00",
                "arrival": "21:30+1",
                "duration_hours": 14.5,
                "price_usd": 947,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "2x23kg",
                "stops": 0,
                "booking_url": "https://jal.com/booking/xyz",
                "amenities": ["WiFi", "Entertainment", "Meals"],
                "confidence": 0.92,
            },
            {
                "airline": "ANA",
                "flight_number": "NH9",
                "route": "JFK → HND (nonstop)",
                "departure": "13:15",
                "arrival": "16:45+1",
                "duration_hours": 14.5,
                "price_usd": 989,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "2x23kg",
                "stops": 0,
                "booking_url": "https://ana.com/booking/abc",
                "amenities": ["WiFi", "Entertainment", "Meals", "Power"],
                "confidence": 0.90,
            },
            {
                "airline": "United",
                "flight_number": "UA79",
                "route": "JFK → NRT (nonstop)",
                "departure": "16:30",
                "arrival": "19:50+1",
                "duration_hours": 14.3,
                "price_usd": 867,
                "cabin_class": "Economy",
                "baggage_included": False,
                "baggage_allowance": "1x23kg (+$60)",
                "stops": 0,
                "booking_url": "https://united.com/booking/def",
                "amenities": ["WiFi", "Entertainment"],
                "confidence": 0.88,
            },
            {
                "airline": "Delta",
                "flight_number": "DL152",
                "route": "JFK → HND (1 stop SEA)",
                "departure": "09:00",
                "arrival": "15:30+1",
                "duration_hours": 17.5,
                "price_usd": 723,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "1x23kg",
                "stops": 1,
                "layover": "3h 15m in Seattle",
                "booking_url": "https://delta.com/booking/ghi",
                "amenities": ["WiFi", "Entertainment"],
                "confidence": 0.85,
            },
        ],
        ("JFK", "CDG"): [  # NYC to Paris
            {
                "airline": "Air France",
                "flight_number": "AF22",
                "route": "JFK → CDG (nonstop)",
                "departure": "19:00",
                "arrival": "08:50+1",
                "duration_hours": 7.8,
                "price_usd": 547,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "1x23kg",
                "stops": 0,
                "booking_url": "https://airfrance.com/booking/xyz",
                "amenities": ["WiFi", "Entertainment", "Meals"],
                "confidence": 0.93,
            },
            {
                "airline": "Delta",
                "flight_number": "DL264",
                "route": "JFK → CDG (nonstop)",
                "departure": "22:30",
                "arrival": "12:15+1",
                "duration_hours": 7.8,
                "price_usd": 589,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "1x23kg",
                "stops": 0,
                "booking_url": "https://delta.com/booking/abc",
                "amenities": ["WiFi", "Entertainment", "Meals"],
                "confidence": 0.91,
            },
        ],
        ("SFO", "CDG"): [  # SF to Paris
            {
                "airline": "Air France",
                "flight_number": "AF83",
                "route": "SFO → CDG (nonstop)",
                "departure": "17:50",
                "arrival": "13:30+1",
                "duration_hours": 10.7,
                "price_usd": 1247,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "1x23kg",
                "stops": 0,
                "booking_url": "https://airfrance.com/booking/sfo",
                "amenities": ["WiFi", "Entertainment", "Meals", "Premium"],
                "confidence": 0.90,
            },
        ],
        ("LAX", "DPS"): [  # LA to Bali
            {
                "airline": "Garuda Indonesia",
                "flight_number": "GA88",
                "route": "LAX → DPS (1 stop CGK)",
                "departure": "23:55",
                "arrival": "10:30+2",
                "duration_hours": 21.6,
                "price_usd": 876,
                "cabin_class": "Economy",
                "baggage_included": True,
                "baggage_allowance": "2x23kg",
                "stops": 1,
                "layover": "2h 45m in Jakarta",
                "booking_url": "https://garuda-indonesia.com/booking/xyz",
                "amenities": ["Entertainment", "Meals"],
                "confidence": 0.87,
            },
        ],
    }
    
    # Find matching route
    key = (origin, destination)
    if key in routes:
        return routes[key]
    
    # Generate generic options if no fixture
    return [
        {
            "airline": "Generic Airlines",
            "flight_number": "GA100",
            "route": f"{origin} → {destination}",
            "departure": "10:00",
            "arrival": "18:00",
            "duration_hours": 8.0,
            "price_usd": 650,
            "cabin_class": "Economy",
            "baggage_included": True,
            "stops": 0,
            "confidence": 0.70,
        }
    ]


def get_hotel_fixtures(destination: str) -> list[dict[str, Any]]:
    """Get mock hotel data for popular destinations."""
    
    destination = destination.upper()[:3]
    
    hotels = {
        "HND": [  # Tokyo
            {
                "name": "Shinjuku Business Hotel",
                "location": "Shinjuku, Tokyo",
                "stars": 4,
                "price_per_night_usd": 120,
                "amenities": ["WiFi", "Breakfast", "Gym", "Restaurant"],
                "distance_to_center_km": 0.5,
                "rating": 4.3,
                "reviews_count": 2847,
                "booking_url": "https://booking.com/hotel/shinjuku",
                "address": "1-2-3 Shinjuku, Tokyo",
                "highlights": ["5 min walk to station", "Excellent breakfast", "Central location"],
                "confidence": 0.91,
            },
            {
                "name": "Asakusa Boutique Inn",
                "location": "Asakusa, Tokyo",
                "stars": 3,
                "price_per_night_usd": 95,
                "amenities": ["WiFi", "Traditional Bath", "Tea Room"],
                "distance_to_center_km": 2.1,
                "rating": 4.6,
                "reviews_count": 1523,
                "booking_url": "https://booking.com/hotel/asakusa",
                "address": "4-5-6 Asakusa, Tokyo",
                "highlights": ["Traditional Japanese style", "Near Senso-ji temple", "Quiet area"],
                "confidence": 0.89,
            },
            {
                "name": "Tokyo Grand Palace Hotel",
                "location": "Marunouchi, Tokyo",
                "stars": 5,
                "price_per_night_usd": 285,
                "amenities": ["WiFi", "Spa", "Pool", "Michelin Restaurant", "Concierge"],
                "distance_to_center_km": 0.3,
                "rating": 4.8,
                "reviews_count": 4521,
                "booking_url": "https://booking.com/hotel/palace",
                "address": "1-1-1 Marunouchi, Tokyo",
                "highlights": ["Luxury amenities", "Imperial Palace view", "Best location"],
                "confidence": 0.94,
            },
        ],
        "CDG": [  # Paris
            {
                "name": "Hotel de Seine",
                "location": "Saint-Germain-des-Prés, Paris",
                "stars": 4,
                "price_per_night_usd": 165,
                "amenities": ["WiFi", "Breakfast", "Bar", "Concierge"],
                "distance_to_center_km": 1.2,
                "rating": 4.4,
                "reviews_count": 1876,
                "booking_url": "https://booking.com/hotel/seine",
                "address": "52 Rue de Seine, 75006 Paris",
                "highlights": ["Charming boutique", "Left Bank location", "Walking to Louvre"],
                "confidence": 0.90,
            },
            {
                "name": "Le Bristol Paris",
                "location": "Champs-Élysées, Paris",
                "stars": 5,
                "price_per_night_usd": 795,
                "amenities": ["WiFi", "Spa", "Pool", "3 Michelin Stars", "Garden"],
                "distance_to_center_km": 0.8,
                "rating": 4.9,
                "reviews_count": 3241,
                "booking_url": "https://booking.com/hotel/bristol",
                "address": "112 Rue du Faubourg Saint-Honoré, 75008 Paris",
                "highlights": ["Palace hotel", "Legendary service", "Rooftop pool"],
                "confidence": 0.95,
            },
        ],
        "DPS": [  # Bali
            {
                "name": "Ubud Jungle Retreat",
                "location": "Ubud, Bali",
                "stars": 4,
                "price_per_night_usd": 87,
                "amenities": ["WiFi", "Pool", "Yoga", "Restaurant", "Spa"],
                "distance_to_center_km": 3.5,
                "rating": 4.7,
                "reviews_count": 982,
                "booking_url": "https://booking.com/hotel/ubud",
                "address": "Jl. Raya Ubud, Bali",
                "highlights": ["Rice terrace view", "Infinity pool", "Peaceful setting"],
                "confidence": 0.88,
            },
        ],
    }
    
    if destination in hotels:
        return hotels[destination]
    
    # Generic hotel
    return [
        {
            "name": "Central Hotel",
            "location": f"{destination} City Center",
            "stars": 3,
            "price_per_night_usd": 100,
            "amenities": ["WiFi", "Breakfast"],
            "rating": 4.0,
            "confidence": 0.70,
        }
    ]


def get_activity_fixtures(destination: str) -> list[dict[str, Any]]:
    """Get mock activity/attraction data."""
    
    destination = destination.upper()[:3]
    
    activities = {
        "HND": [  # Tokyo
            {
                "name": "Tsukiji Outer Market Food Tour",
                "category": "Food & Drink",
                "duration_hours": 3.0,
                "price_usd": 85,
                "rating": 4.8,
                "description": "Explore Tokyo's famous fish market with a local guide. Sample fresh sushi, street food, and learn about Japanese culinary culture.",
                "best_time": "Morning (6am-9am)",
                "booking_required": True,
                "booking_url": "https://viator.com/tsukiji-tour",
                "confidence": 0.92,
            },
            {
                "name": "Senso-ji Temple & Asakusa Walking Tour",
                "category": "Culture & History",
                "duration_hours": 2.5,
                "price_usd": 0,  # Free
                "rating": 4.7,
                "description": "Visit Tokyo's oldest temple, stroll through Nakamise shopping street, and experience traditional Tokyo.",
                "best_time": "Morning or late afternoon",
                "booking_required": False,
                "confidence": 0.95,
            },
            {
                "name": "Ramen Making Class",
                "category": "Food & Drink",
                "duration_hours": 2.0,
                "price_usd": 75,
                "rating": 4.9,
                "description": "Learn to make authentic Japanese ramen from scratch. Includes noodle-making, broth preparation, and eating your creation.",
                "best_time": "Afternoon",
                "booking_required": True,
                "booking_url": "https://cookingclass.jp/ramen",
                "confidence": 0.90,
            },
            {
                "name": "Meiji Shrine & Yoyogi Park",
                "category": "Nature & Culture",
                "duration_hours": 2.0,
                "price_usd": 0,
                "rating": 4.6,
                "description": "Peaceful Shinto shrine in forested grounds. Perfect for morning meditation or afternoon stroll.",
                "best_time": "Early morning",
                "booking_required": False,
                "confidence": 0.93,
            },
            {
                "name": "Shibuya & Harajuku Walking Tour",
                "category": "Urban Exploration",
                "duration_hours": 3.0,
                "price_usd": 0,
                "rating": 4.5,
                "description": "Experience Tokyo's youth culture: Shibuya Crossing, Harajuku fashion streets, and quirky shops.",
                "best_time": "Afternoon/evening",
                "booking_required": False,
                "confidence": 0.91,
            },
        ],
        "CDG": [  # Paris
            {
                "name": "Louvre Museum Priority Access",
                "category": "Art & Culture",
                "duration_hours": 3.0,
                "price_usd": 45,
                "rating": 4.7,
                "description": "Skip-the-line access to world's largest art museum. See Mona Lisa, Venus de Milo, and more.",
                "best_time": "Morning",
                "booking_required": True,
                "booking_url": "https://louvre.fr/tickets",
                "confidence": 0.94,
            },
            {
                "name": "Eiffel Tower Sunset Visit",
                "category": "Landmarks",
                "duration_hours": 2.0,
                "price_usd": 35,
                "rating": 4.9,
                "description": "Visit iconic Eiffel Tower at sunset for stunning city views.",
                "best_time": "Sunset (7pm-9pm)",
                "booking_required": True,
                "booking_url": "https://toureiffel.paris/tickets",
                "confidence": 0.96,
            },
        ],
        "DPS": [  # Bali
            {
                "name": "Uluwatu Temple & Kecak Dance",
                "category": "Culture & Performance",
                "duration_hours": 4.0,
                "price_usd": 25,
                "rating": 4.8,
                "description": "Clifftop temple with sunset views, followed by traditional Kecak fire dance performance.",
                "best_time": "Late afternoon/sunset",
                "booking_required": True,
                "booking_url": "https://bali-tours.com/uluwatu",
                "confidence": 0.91,
            },
            {
                "name": "Ubud Rice Terrace Trek",
                "category": "Nature & Adventure",
                "duration_hours": 3.0,
                "price_usd": 15,
                "rating": 4.7,
                "description": "Guided walk through iconic Tegallalang rice terraces. Includes village visit and coffee tasting.",
                "best_time": "Morning",
                "booking_required": False,
                "confidence": 0.89,
            },
        ],
    }
    
    if destination in activities:
        return activities[destination]
    
    return []


def get_destination_info(destination: str) -> dict[str, Any]:
    """Get general destination information."""
    
    destination = destination.upper()[:3]
    
    info = {
        "HND": {
            "city": "Tokyo",
            "country": "Japan",
            "timezone": "Asia/Tokyo",
            "currency": "JPY",
            "language": "Japanese",
            "best_months": ["March", "April", "October", "November"],
            "avg_daily_budget_usd": {
                "budget": 80,
                "mid_range": 150,
                "luxury": 400,
            },
            "local_tips": [
                "Get a Suica card for public transport",
                "Cherry blossoms peak late March - early April",
                "Many restaurants don't accept credit cards",
                "Tipping is not customary",
            ],
            "safety_rating": 9.5,
        },
        "CDG": {
            "city": "Paris",
            "country": "France",
            "timezone": "Europe/Paris",
            "currency": "EUR",
            "language": "French",
            "best_months": ["April", "May", "September", "October"],
            "avg_daily_budget_usd": {
                "budget": 90,
                "mid_range": 180,
                "luxury": 500,
            },
            "local_tips": [
                "Buy Paris Museum Pass for major attractions",
                "Avoid August (many locals on vacation)",
                "Metro is efficient but pickpockets common",
                "Learn basic French phrases",
            ],
            "safety_rating": 7.5,
        },
        "DPS": {
            "city": "Bali",
            "country": "Indonesia",
            "timezone": "Asia/Makassar",
            "currency": "IDR",
            "language": "Indonesian",
            "best_months": ["April", "May", "June", "September"],
            "avg_daily_budget_usd": {
                "budget": 40,
                "mid_range": 100,
                "luxury": 300,
            },
            "local_tips": [
                "Rent a scooter for flexibility",
                "Rainy season Nov-March",
                "Bargain at markets",
                "Dress modestly at temples",
            ],
            "safety_rating": 8.0,
        },
    }
    
    return info.get(destination, {
        "city": destination,
        "avg_daily_budget_usd": {"mid_range": 120},
    })
