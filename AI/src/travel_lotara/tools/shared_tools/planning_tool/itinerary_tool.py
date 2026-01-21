# travel_lotara/tools/shared_tools/planning_tool/itinerary_tool.py

from google.adk.tools import ToolContext, FunctionTool
from src.travel_lotara.database.repositories.itinerary_repo import ItineraryRepository

repo = ItineraryRepository()

def itinerary_builder_tool(tool_context: ToolContext):
    state = tool_context.state

    user_id = state["user_id"]
    destination = state["selected_destination"]
    days = state["trip_length"]

    itinerary = []
    for day in range(1, days + 1):
        itinerary.append({
            "day": day,
            "city": destination,
            "activities": ["Explore", "Local food"],
        })

    repo.save_itinerary(
        user_id=user_id,
        itinerary=itinerary,
    )

    state["itinerary"] = itinerary
    return {"itinerary": itinerary}


itinerary_tool = FunctionTool(
    # display_name="itinerary_tool",
    func=itinerary_builder_tool,
    # description="Builds an itinerary for the trip.",
)