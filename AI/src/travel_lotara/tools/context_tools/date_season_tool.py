# travel_lotara/tools/context_tools/date_season_tool.py
from abc import abstractmethod
from datetime import datetime
from ..base_tool import BaseTool
from google.adk.tools import ToolContext, FunctionTool

class DateSeasonTool(BaseTool):
    """Derives season and travel context from dates."""

    def run(self, tool_context: ToolContext):
        state = tool_context.state

        start_date_str = state.get("start_date")
        if not start_date_str:
            return {
                "error": "start_date not found in state",
                "season": "unknown",
                "month": None,
                "is_peak_season": False,
                "monsoon_risk": False,
                "heat_risk": False,
            }
        
        start_date = datetime.fromisoformat(start_date_str)
        month = start_date.month

        # Vietnam-specific seasons
        if month in [12, 1, 2]:
            season = "cool_dry"
        elif month in [3, 4]:
            season = "hot_dry"
        elif month in [5, 6, 7, 8, 9]:
            season = "rainy"
        else:
            season = "transition"

        travel_context = {
            "season": season,
            "month": month,
            "is_peak_season": month in [12, 1, 6, 7],
            "monsoon_risk": season == "rainy",
            "heat_risk": season == "hot_dry",
        }

        state["date_season_context"] = travel_context
        return travel_context


def get_date_season_context(tool_context: ToolContext):
    """Derive season and travel context from trip dates."""
    return DateSeasonTool().run(tool_context)

date_season_tool = FunctionTool(
    func=get_date_season_context,
)