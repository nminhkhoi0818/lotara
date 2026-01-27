# travel_lotara/db/repositories/destination_repo.py

from ..client import get_supabase_client

class DestinationRepository:
    def __init__(self):
        self.db = get_supabase_client()

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
