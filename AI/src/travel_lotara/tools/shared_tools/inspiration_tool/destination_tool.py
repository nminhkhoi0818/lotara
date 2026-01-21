# travel_lotara/tools/shared_tools/inspiration_tool/destination_tool.py

from google.adk.tools import ToolContext, FunctionTool
from src.travel_lotara.database.repositories.destination_repo import DestinationRepository

repo = DestinationRepository()

def destination_discovery_tool(tool_context: ToolContext):
    state = tool_context.state

    interests = state.get("interests", [])
    budget = state.get("budget", "medium")
    season = state.get("season", "any")

    results = repo.search_by_interests(
        interests=interests,
        budget=budget,
        season=season,
    )

    # Store canonical memory
    state["destination_candidates"] = results

    return {
        "destination_candidates": [
            {
                "id": d["id"],
                "name": d["name"],
                "country": d["country"],
                "why": d["tags"],
            }
            for d in results
        ]
    }

destination_tool = FunctionTool(
    # display_name="destination_tool",
    func=destination_discovery_tool,
    # description="Discover travel destinations based on user interests, budget, and season.",
)