
# (before_model_callback)

# ================ Purpose:
#### + Reject non-travel queries
#### + Prevent prompt injection
#### + Keep root agent in scope
#### + Where it runs

# ✔ Before any model call
# ✔ Applies to root agent and sub-agents


# guardrails/features/input_intent_validation.py
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

TRAVEL_KEYWORDS = {
    "travel", "trip", "itinerary", "flight", "hotel",
    "transport", "plan", "destination", "visa"
}


def input_intent_guard(
    ctx: CallbackContext,
    request: LlmRequest
) -> LlmResponse | None:
    """
    Runs before ANY model call.
    Blocks non-travel or malicious prompts.
    """

    if not request.contents:
        return None

    user_text = request.contents[-1].text.lower()

    if not any(keyword in user_text for keyword in TRAVEL_KEYWORDS):
        return LlmResponse(
            contents=[
                "I can only assist with travel planning and trip preparation."
            ]
        )

    # Simple prompt injection defense
    forbidden = ["ignore instructions", "system prompt", "developer message"]
    if any(f in user_text for f in forbidden):
        return LlmResponse(
            contents=["Your request violates usage policies."]
        )

    return None
