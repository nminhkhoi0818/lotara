# travel_lotara/tools/shared_tools/planning_tool/itinerary_tool.py

from datetime import datetime
from typing import Any
from src.travel_lotara.agents.shared_libraries import constants

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import ToolContext, FunctionTool
from src.travel_lotara.database.repositories.itinerary_repo import ItineraryRepository


NEED_ITIN_INSTR = """
Cannot find an itinerary to work on.
Inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent` or the `root_agent`.
"""

LOGISTIC_INSTR_TEMPLATE = """
Your role is primarily to handle logistics to get to the next destination on a traveler's trip.

Current time is "{CURRENT_TIME}".
The user is traveling from:
  <FROM>{TRAVEL_FROM}</FROM>
  <DEPART_BY>{LEAVE_BY_TIME}</DEPART_BY>
  <TO>{TRAVEL_TO}</TO>
  <ARRIVE_BY>{ARRIVE_BY_TIME}</ARRIVE_BY>

Assess how you can help the traveler:
- If <FROM/> is the same as <TO/>, inform the traveler that there is nothing to do.
- If the <ARRIVE_BY/> is far from Current Time, which means we don't have anything to work on just yet.
- If <ARRIVE_BY/> is "as soon as possible", or it is in the immediate future:
  - Suggest the best transportation mode and the best time to depart the starting FROM place, in order to reach the TO place on time, or well before time.
  - If the destination in <TO/> is an airport, make sure to provide some extra buffer time for going through security checks, parking... etc.
  - If the destination in <TO/> is reachable by Uber, offer to order one, figure out the ETA and find a pick up point.
"""


def get_event_time_as_destination(
    destin_json: dict[str, Any], default_value: str
):
    """Returns an event time appropriate for the location type."""
    match destin_json["event_type"]:
        case "flight":
            return destin_json["departure_time"]
        case "hotel_checkin" | "hotel_checkout" | "visit":
            return destin_json["start_time"]
        case _:
            return default_value


def parse_as_origin(origin_json: dict[str, Any]):
    """Returns a tuple of strings (origin, depart_by) appropriate for the starting location."""
    match origin_json["event_type"]:
        case "flight":
            return (
                origin_json["arrival_time"],
            )
        case "hotel_checkin" | "hotel_checkout" | "visit":
            return (
                origin_json["description"]
                + " "
                + origin_json.get("location", "").get("address", ""),
                origin_json["end_time"],
            )
        case "home":
            return (
                origin_json.get("local_prefer_mode")
                + " from "
                + origin_json.get("location", "").get("address", ""),
                "any time",
            )
        case _:
            return "Local in the region", "any time"


def parse_as_destin(destin_json: dict[str, Any]):
    """Returns a tuple of strings (destination, arrive_by) appropriate for the destination."""
    match destin_json["event_type"]:
        case "flight":
            return (
                destin_json["description"]
                + " "
                "An hour before " + destin_json["departure_time"],
            )
        case "hotel_checkin" | "hotel_checkout" | "visit":
            return (
                destin_json["description"]
                + " "
                + destin_json.get("location", "").get("address", ""),
                destin_json["start_time"],
            )
        case "home":
            return (
                "Local in the region towards "
                + destin_json.get("location", "").get("address", ""),
                "any time",
            )
        case _:
            return "Local in the region", "as soon as possible"


def find_segment(
    profile: dict[str, Any], itinerary: dict[str, Any], current_datetime: str
):
    """
    Find the events to travel from A to B
    This follows the itinerary schema in types.Itinerary.

    Since return values will be used as part of the prompt,
    there are flexibilities in what the return values contains.

    Args:
        profile: A dictionary containing the user's profile.
        itinerary: A dictionary containing the user's itinerary.
        current_datetime: A string containing the current date and time.

    Returns:
      from - capture information about the origin of this segment.
      to   - capture information about the destination of this segment.
      arrive_by - an indication of the time we shall arrive at the destination.
    """
    # Expects current_datetime is in '2024-03-15 04:00:00' format
    datetime_object = datetime.fromisoformat(current_datetime)
    current_date = datetime_object.strftime("%Y-%m-%d")
    current_time = datetime_object.strftime("%H:%M")
    event_date = current_date
    event_time = current_time

    print("-----")
    print("MATCH DATE", current_date, current_time)
    print("-----")

    # defaults
    origin_json = profile["home"]
    destin_json = profile["home"]

    leave_by = "No movement required"
    arrive_by = "No movement required"

    # Go through the itinerary to find where we are base on the current date and time
    for day in itinerary.get("trip_overview", []):
        event_date = day["start_date"]
        for event in day["events"]:
            # for every event we update the origin and destination until
            # we find one we need to pay attention
            origin_json = destin_json
            destin_json = event
            event_time = get_event_time_as_destination(
                destin_json, current_time
            )
            # The moment we find an event that's in the immediate future we stop to handle it
            print(
                event["event_type"],
                event_date,
                current_date,
                event_time,
                current_time,
            )
            if event_date >= current_date and event_time >= current_time:
                break
        else:  # if inner loop not break, continue
            continue
        break  # else break too.

    #
    # Construct prompt descriptions for travel_from, travel_to, arrive_by
    #
    travel_from, leave_by = parse_as_origin(origin_json)
    travel_to, arrive_by = parse_as_destin(destin_json)

    return (travel_from, travel_to, leave_by, arrive_by)


def _inspect_itinerary(state: dict[str:Any]):
    """Identifies and returns the itinerary, profile and current datetime from the session state."""

    itinerary = state[constants.ITIN_KEY]
    profile = state[constants.PROF_KEY]
    print("itinerary", itinerary)
    current_datetime = itinerary["start_date"] + " 00:00"
    if state.get(constants.ITIN_DATETIME, ""):
        current_datetime = state[constants.ITIN_DATETIME]

    return itinerary, profile, current_datetime


def transit_coordination(readonly_context: ReadonlyContext):
    """Dynamically generates an instruction for the day_of agent."""

    state = readonly_context.state

    # Inspecting the itinerary
    if constants.ITIN_KEY not in state:
        return NEED_ITIN_INSTR

    itinerary, profile, current_datetime = _inspect_itinerary(state)
    travel_from, travel_to, leave_by, arrive_by = find_segment(
        profile, itinerary, current_datetime
    )

    print("-----")
    print(itinerary["trip_name"])
    print(current_datetime)
    print("-----")
    print("-----")
    print("TRIP EVENT")
    print("FROM", travel_from, leave_by)
    print("TO", travel_to, arrive_by)
    print("-----")

    return LOGISTIC_INSTR_TEMPLATE.format(
        CURRENT_TIME=current_datetime,
        TRAVEL_FROM=travel_from,
        LEAVE_BY_TIME=leave_by,
        TRAVEL_TO=travel_to,
        ARRIVE_BY_TIME=arrive_by,
    )

# ################## Initialize the itinerary repository


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