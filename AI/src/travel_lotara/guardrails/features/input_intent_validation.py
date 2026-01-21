
# (before_model_callback)

# ================ Purpose:
#### + Reject non-travel queries
#### + Prevent prompt injection
#### + Keep root agent in scope
#### + Where it runs

# ✔ Before any model call
# ✔ Applies to root agent and sub-agents


# guardrails/features/input_intent_validation.py
from google.adk.callbacks import CallbackContext, LlmRequest, LlmResponse

TRAVEL_KEYWORDS = {
    "travel", "trip", "itinerary", "flight", "hotel",
    "visa", "transport", "plan", "destination"
}

def input_intent_guard(
    ctx: CallbackContext,
    request: LlmRequest
) -> LlmResponse | None:
    user_text = request.contents[-1].text.lower()

    if not any(k in user_text for k in TRAVEL_KEYWORDS):
        return LlmResponse(
            contents=[
                "I can only help with travel planning and trip preparation."
            ]
        )

    return None
