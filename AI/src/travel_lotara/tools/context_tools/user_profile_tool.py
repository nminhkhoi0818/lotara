# travel_lotara/tools/context_tools/user_profile_tool.py
from abc import abstractmethod
from typing import Dict, Any
from ..base_tool import BaseTool
from google.adk.tools import ToolContext, FunctionTool


class UserProfileTool(BaseTool):
    """Normalizes and enriches user profile data."""

    
    def run(self, tool_context: ToolContext):
        raw = tool_context.state["user_profile"]

        profile = {
            "travel_style": raw.get("travel_style"),
            "budget_range": raw.get("budget_range"),
            "group_type" : raw.get("group_type"),
            "preferences": raw.get("preferences"),
            "constraints": raw.get("constraints"),
            "home_location": raw.get("home_location"),
        }

        # Derived persona flags
        profile["is_family"] = "family" in profile["group_type"]
        profile["is_solo"] = profile["group_type"] == "solo"
        profile["is_fast_paced"] = profile["preferences"].get("pace") == "fast"

        tool_context.state["normalized_user_profile"] = profile
        return profile

def get_user_profile(tool_context: ToolContext):
    """Get and normalize user profile data."""
    return UserProfileTool().run(tool_context)

user_profile_tool = FunctionTool(
    func=get_user_profile,
)

