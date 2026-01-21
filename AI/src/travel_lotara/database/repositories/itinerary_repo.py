# travel_lotara/database/repositories/itinerary_repo.py

from ..client import SupabaseClient

class ItineraryRepository:
    def __init__(self):
        self.db = SupabaseClient.get_client()

    def save_itinerary(self, user_id: str, itinerary: list[dict]):
        self.db.table("itineraries").insert({
            "user_id": user_id,
            "content": itinerary,
            "status": "planned",
        }).execute()
