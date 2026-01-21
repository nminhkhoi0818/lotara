# travel_lotara/tools/context_tools/user_profile_tool.py
from typing import Dict, Any
from ..base_tool import BaseTool
from google.adk.tools import ToolContext, FunctionTool


class UserProfileTool(BaseTool):
    """Normalizes and enriches user profile data."""

    @staticmethod
    def run(tool_context: ToolContext):
        raw = tool_context.state["user_profile"]

        profile = {
            "budget_tier": raw.get("budget"),
            "pace": raw.get("pace"),
            "companions": raw.get("companions"),
            "activity_level": raw.get("activity"),
            "crowd_tolerance": raw.get("crowds"),
            "needs_wifi": raw.get("remote") == "yes",
            "travel_style": raw.get("travelStyle"),
        }

        # Derived persona flags
        profile["is_family"] = "family" in profile["companions"]
        profile["is_solo"] = profile["companions"] == "solo"
        profile["is_fast_paced"] = profile["pace"] == "fast"

        tool_context.state["normalized_user_profile"] = profile
        return profile

user_profile_tool = FunctionTool(
    # display_name="user_profile_tool",
    # description="Normalizes and enriches user profile data.",
    func=UserProfileTool.run,
)

