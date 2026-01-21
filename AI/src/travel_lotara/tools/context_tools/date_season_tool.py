# travel_lotara/tools/context_tools/date_season_tool.py
from datetime import datetime
from ..base_tool import BaseTool
from google.adk.tools import ToolContext, FunctionTool

class DateSeasonTool(BaseTool):
    """Derives season and travel context from dates."""

    @staticmethod
    def run(tool_context: ToolContext):
        state = tool_context.state

        start_date = datetime.fromisoformat(state["trip_start_date"])
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


date_season_tool = FunctionTool(
    # display_name="date_season_tool",
    func=DateSeasonTool.run,
    # description="Derives travel season and context from trip start date.",
)