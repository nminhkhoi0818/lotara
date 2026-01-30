import asyncio
import time
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext, BaseTool
from google.adk.agents.callback_context import CallbackContext
from src.travel_lotara.tools.shared_tools.adk_memory import _load_precreated_itinerary
from src.travel_lotara.guardrails.features import (
    tool_argument_guard,
    input_intent_guard
)

from src.travel_lotara.guardrails.output_enforcer import (
    enforce_final_json_output
)

from src.travel_lotara.agents.shared_libraries import OutputMessage

# Rate limiting: Track last agent call time
_last_agent_call_time = 0
_AGENT_CALL_DELAY_SECONDS = 5

def before_agent_callback(*, callback_context: CallbackContext):
    global _last_agent_call_time
    ctx = callback_context
    
    # Rate limiting: Enforce minimum delay between agent calls
    current_time = time.time()
    time_since_last_call = current_time - _last_agent_call_time
    if time_since_last_call < _AGENT_CALL_DELAY_SECONDS:
        delay = _AGENT_CALL_DELAY_SECONDS - time_since_last_call
        print(f"⏱️  Rate limiting: waiting {delay:.1f}s before agent call")
        time.sleep(delay)
    
    _last_agent_call_time = time.time()
    print("✅ before_agent_callback triggered")

    _load_precreated_itinerary(ctx)

    # ✅ ADD THIS
    if "high_level_itinerary" not in ctx.state:
        itinerary = ctx.state.get("itinerary", {})
        ctx.state["itinerary"] = {
            "destination": itinerary.get("destination"),
            "start_date": itinerary.get("start_date"),
            "end_date": itinerary.get("end_date"),
            "total_days": itinerary.get("total_days"),
            "status": itinerary.get("meta", {}).get("status") if itinerary.get("meta") else None,
        }
    
    # ✅ Ensure user_profile ALWAYS exists
    if "user_profile" not in ctx.state:
        ctx.state["user_profile"] = {
            "travel_style": None,
            "budget_range": None,
            "group_type": None,
            "preferences": {
                "food": [],
                "activities": [],
                "pace": None,
            },
            "constraints": {
                "mobility": None,
                "dietary": [],
                "time_limit_days": None,
            },
        }

    return None

def before_model_callback(
    *,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """
    Runs BEFORE every LLM call (root + sub-agents).
    Perfect place for input intent validation.
    """
    print("✅ before_model_callback triggered")

    guard_output = input_intent_guard(callback_context, llm_request)
    if guard_output:
        return guard_output

    return None


def before_tool_callback(
    *,
    tool: BaseTool,
    tool_context: ToolContext,
    args: dict,
):
    # print("[DEBUG] before_tool_callback triggered")
    guard_output = tool_argument_guard(tool, args, tool_context)
    if guard_output:
        return guard_output

    return None



def after_agent_callback(*, callback_context: CallbackContext) -> OutputMessage | dict | None:
    """
    Post-process agent output after completion.
    
    Ensures the itinerary in state matches the expected schema structure.
    This provides a safety net for validation before the API returns the response.

    Args:
        callback_context: The callback context containing the agent and session information.
    Returns:
        None to pass through the agent's natural output.
    """
    print("✅ after_agent_callback triggered")
    
    state = callback_context.state
    # State object doesn't have .keys(), access directly
    itinerary = state.get("itinerary", {})
    print(f" [DEBUG] Itinerary type: {type(itinerary)}, empty: {not itinerary}")
    
    if itinerary and isinstance(itinerary, dict):
        print(f" [INFO] Itinerary found in state, validating structure...")
        
        # Ensure all required top-level fields exist
        required_fields = {
            "trip_name": itinerary.get("trip_name", "Untitled Trip"),
            "start_date": itinerary.get("start_date", state.get("start_date", "2025-01-01")),
            "end_date": itinerary.get("end_date", state.get("end_date", "2025-01-01")),
            "origin": itinerary.get("origin", state.get("origin", "Unknown")),
            "destination": itinerary.get("destination", state.get("destination", "Unknown")),
            "total_days": str(itinerary.get("total_days", state.get("total_days", "0"))),
            "average_budget_spend_per_day": itinerary.get("average_budget_spend_per_day", state.get("average_budget_spend_per_day", "$50 USD")),
            "average_ratings": str(itinerary.get("average_ratings", "4.5")),
            "trip_overview": itinerary.get("trip_overview", [])
        }
        
        # Check if any required fields are missing
        missing_fields = [k for k, v in required_fields.items() if k not in itinerary]
        if missing_fields:
            print(f" [WARNING] Missing fields in itinerary: {missing_fields}")
            print(f" [INFO] Filling missing fields from state or defaults...")
            
            # Update the itinerary with missing fields
            for field, default_value in required_fields.items():
                if field not in itinerary or itinerary[field] is None:
                    itinerary[field] = default_value
            
            # Update state with corrected itinerary
            state["itinerary"] = itinerary
        
        # Validate trip_overview structure
        trip_overview = itinerary.get("trip_overview", [])
        if not trip_overview:
            print(f" [WARNING] trip_overview is empty")
        elif isinstance(trip_overview, list):
            # Check each trip has required fields
            for idx, trip in enumerate(trip_overview):
                if not isinstance(trip, dict):
                    print(f" [ERROR] trip_overview[{idx}] is not a dict")
                    continue
                
                required_trip_fields = ["trip_number", "start_date", "end_date", "summary", "events"]
                missing_trip_fields = [f for f in required_trip_fields if f not in trip]
                if missing_trip_fields:
                    print(f" [WARNING] Trip {idx} missing fields: {missing_trip_fields}")
                
                # Validate events
                events = trip.get("events", [])
                if not events:
                    print(f" [WARNING] Trip {idx} has no events")
                elif isinstance(events, list):
                    for event_idx, event in enumerate(events):
                        if not isinstance(event, dict):
                            print(f" [ERROR] Trip {idx}, event {event_idx} is not a dict")
                            continue
                        if "event_type" not in event:
                            print(f" [WARNING] Trip {idx}, event {event_idx} missing event_type")
                        if "description" not in event:
                            print(f" [WARNING] Trip {idx}, event {event_idx} missing description")
        
        print(f" [INFO] Itinerary validation complete")
    else:
        print(f" [WARNING] No valid itinerary found in state")

