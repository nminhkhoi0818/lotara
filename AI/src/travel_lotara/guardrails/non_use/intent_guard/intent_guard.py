# A. Intent Guard (Input Safety + Routing)

# ====================  Purpose:
#### + Validate user intent
#### + Prevent unsupported or dangerous requests
#### + Decide which agent tree is allowed

# ==================== Example responsibilities
#### + Reject non-travel queries
#### + Block booking/payment attempts
#### + Normalize intent



from enum import Enum

class UserIntent(Enum):
    PRE_TRIP = "pre_trip"
    IN_TRIP = "in_trip"
    POST_TRIP = "post_trip"
    UNKNOWN = "unknown"


class IntentGuard:
    def classify(self, user_query: str) -> UserIntent:
        q = user_query.lower()

        if any(k in q for k in ["plan", "itinerary", "travel", "trip"]):
            return UserIntent.PRE_TRIP

        return UserIntent.UNKNOWN

    def validate(self, intent: UserIntent):
        if intent == UserIntent.UNKNOWN:
            raise ValueError("Unsupported intent")
