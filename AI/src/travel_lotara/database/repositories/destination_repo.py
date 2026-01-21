# travel_lotara/db/repositories/destination_repo.py

from ..client import SupabaseClient

class DestinationRepository:
    def __init__(self):
        self.db = SupabaseClient.get_client()

    def search_by_interests(
        self,
        interests: list[str],
        budget: str,
        season: str,
    ):
        query = (
            self.db
            .table("destinations")
            .select("*")
            .contains("tags", interests)
            .eq("budget_level", budget)
        )

        if season != "any":
            query = query.contains("best_seasons", [season])

        return query.execute().data
