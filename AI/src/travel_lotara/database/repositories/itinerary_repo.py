# travel_lotara/database/repositories/itinerary_repo.py

from ..client import get_supabase_client

class ItineraryRepository:
    def __init__(self):
        self.db = get_supabase_client()

    def save_itinerary(self, user_id: str, itinerary: list[dict]):
        self.db.table("itineraries").insert({
            "user_id": user_id,
            "content": itinerary,
            "status": "planned",
        }).execute()
