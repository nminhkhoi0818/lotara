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
    
    Since conversational agents don't enforce strict output schemas,
    this callback currently passes through the output unchanged.
    Task-specific sub-agents still enforce their own output_schema.

    Args:
        callback_context: The callback context containing the agent and session information.
    Returns:
        None to pass through the agent's natural output.
    """
    # Let conversational agents respond naturally
    # Sub-agents with output_schema will still enforce structured output

    print("✅ after_agent_callback triggered")
    print(f" [INFROMATION] Tool calls will define structured outputs where needed.")
    
    # Note: Output enforcement is handled by individual agents' output_schema
    # No need to enforce here as the planning agent already returns structured output
    
    # Optionally log the state for debugging
    state = callback_context.state
    itinerary_context = state.get("itinerary", {})
    if itinerary_context:
        print(f" [INFO] Itinerary context found in state")
    
    return None



