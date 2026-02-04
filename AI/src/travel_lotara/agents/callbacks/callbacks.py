import asyncio
import time
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext, BaseTool
from google.adk.agents.callback_context import CallbackContext
from src.travel_lotara.config.logging_config import get_logger
from src.travel_lotara.tools.shared_tools.adk_memory import _load_precreated_itinerary
from src.travel_lotara.guardrails.features import (
    tool_argument_guard,
    input_intent_guard
)

from src.travel_lotara.guardrails.output_enforcer import (
    enforce_final_json_output
)

from src.travel_lotara.agents.shared_libraries import OutputMessage

# Import progress tracking
from src.travel_lotara.tracking import (
    track_agent_start,
    track_tool_call,
    track_tool_result,
    track_model_call,
    track_thinking,
    ProgressTracker,
)

# Logger
logger = get_logger(__name__)

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
        time.sleep(delay)
    
    _last_agent_call_time = time.time()
    
    # Track agent start for progress streaming
    session_id = ctx.session.id if hasattr(ctx, 'session') and ctx.session else None
    if session_id:
        agent_name = ctx.agent.name if hasattr(ctx, 'agent') and hasattr(ctx.agent, 'name') else "Agent"
        # Estimate progress based on agent type
        progress = 10  # Default start
        if "inspiration" in agent_name.lower():
            progress = 20
            track_agent_start(session_id, "Inspiration Agent", progress)
        elif "planning" in agent_name.lower() or "plan" in agent_name.lower():
            progress = 50
            track_agent_start(session_id, "Planning Agent", progress)
        elif "detail" in agent_name.lower():
            progress = 75
            track_agent_start(session_id, "Detailing Agent", progress)
        else:
            track_agent_start(session_id, agent_name, progress)

    _load_precreated_itinerary(ctx)

    # ✅ ADD THIS
    if "high_level_itinerary" not in ctx.state:
        itinerary = ctx.state.get("itinerary", {})
        ctx.state["itinerary"] = {
            "destination": itinerary.get("destination"),
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
    
    # Track model call for progress streaming
    session_id = callback_context.session.id if hasattr(callback_context, 'session') and callback_context.session else None
    if session_id:
        # Determine purpose from request context
        agent_name = callback_context.agent.name if hasattr(callback_context, 'agent') and hasattr(callback_context.agent, 'name') else "Agent"
        model_name = "Gemini 2.5 Flash"
        
        if "inspiration" in agent_name.lower():
            purpose = "Generating trip themes and inspiration"
        elif "planning" in agent_name.lower():
            purpose = "Creating day-by-day itinerary"
        elif "detail" in agent_name.lower():
            purpose = "Adding location details"
        else:
            purpose = f"Processing with {agent_name}"
        
        track_model_call(session_id, model_name, purpose)

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
    
    # Track tool call for progress streaming
    session_id = tool_context.session.id if hasattr(tool_context, 'session') and tool_context.session else None
    if session_id:
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        track_tool_call(session_id, tool_name, args)
    
    guard_output = tool_argument_guard(tool, args, tool_context)
    if guard_output:
        return guard_output

    return None



def after_agent_callback(*, callback_context: CallbackContext) -> OutputMessage | dict | None:
    """
    Post-process agent output after completion.
    
    Handles:
    1. Context reduction after RAG retrieval (limit to top 5 for speed)
    2. Itinerary validation and structure enforcement
    
    Args:
        callback_context: The callback context containing the agent and session information.
    Returns:
        None to pass through the agent's natural output.
    """
    state = callback_context.state
    agent_name = callback_context.agent.name if hasattr(callback_context, 'agent') else "unknown"
    
    # CONTEXT REDUCTION: Limit RAG results to top 5 per category for faster planning
    # This reduces planning agent context from ~50K tokens to ~10K tokens (80% reduction)
    if agent_name == "rag_retrieval_parallel_agent":
        for key in ["rag_attractions", "rag_hotels", "rag_activities"]:
            if key in state and isinstance(state[key], dict):
                # Extract locations list
                locations = state[key].get("locations", [])
                if len(locations) > 5:
                    state[key]["locations"] = locations[:5]  # Keep top 5 only
                    state[key]["count"] = 5
    
    # ITINERARY VALIDATION
    # State object doesn't have .keys(), access directly
    itinerary = state.get("itinerary", {})
    logger.debug(f"Itinerary type: {type(itinerary)}, empty: {not itinerary}")
    
    if itinerary and isinstance(itinerary, dict):
        logger.info("Itinerary found in state, validating structure...")
        
        # Ensure all required top-level fields exist
        required_fields = {
            "trip_name": itinerary.get("trip_name", "Untitled Trip"),
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
            logger.warning(f"Missing fields in itinerary: {missing_fields}")
            logger.info("Filling missing fields from state or defaults...")
            
            # Update the itinerary with missing fields
            for field, default_value in required_fields.items():
                if field not in itinerary or itinerary[field] is None:
                    itinerary[field] = default_value
            
            # Update state with corrected itinerary
            state["itinerary"] = itinerary
        
        # Validate trip_overview structure
        trip_overview = itinerary.get("trip_overview", [])
        if not trip_overview:
            logger.warning("trip_overview is empty")
        elif isinstance(trip_overview, list):
            # Check each trip has required fields
            for idx, trip in enumerate(trip_overview):
                if not isinstance(trip, dict):
                    logger.error(f"trip_overview[{idx}] is not a dict")
                    continue
                
                required_trip_fields = ["trip_number", "summary", "events"]
                missing_trip_fields = [f for f in required_trip_fields if f not in trip]
                if missing_trip_fields:
                    logger.warning(f"Trip {idx} missing fields: {missing_trip_fields}")
                
                # Validate events
                events = trip.get("events", [])
                if not events:
                    logger.warning(f"Trip {idx} has no events")
                elif isinstance(events, list):
                    for event_idx, event in enumerate(events):
                        if not isinstance(event, dict):
                            logger.error(f"Trip {idx}, event {event_idx} is not a dict")
                            continue
                        if "event_type" not in event:
                            logger.warning(f"Trip {idx}, event {event_idx} missing event_type")
                        if "description" not in event:
                            logger.warning(f"Trip {idx}, event {event_idx} missing description")
        
        logger.info("Itinerary validation complete")
    else:
        logger.warning("No valid itinerary found in state")

