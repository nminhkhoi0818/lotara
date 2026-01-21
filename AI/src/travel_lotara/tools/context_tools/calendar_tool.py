# travel_lotara/tools/context_tools/calendar_tool.py

from datetime import datetime, timedelta
from google.adk.tools import ToolContext, FunctionTool
from ..base_tool import BaseTool

class CalendarTool(BaseTool):
    """Expands trip dates into structured calendar days."""

    @staticmethod
    def run(tool_context: ToolContext):
        state = tool_context.state

        start = datetime.fromisoformat(state["trip_start_date"])
        end = datetime.fromisoformat(state["trip_end_date"])

        days = []
        current = start
        day_num = 1

        while current <= end:
            days.append({
                "day": day_num,
                "date": current.strftime("%Y-%m-%d"),
                "weekday": current.strftime("%A"),
                "is_travel_day": False,
            })
            current += timedelta(days=1)
            day_num += 1

        state["trip_calendar"] = days
        state["total_days"] = len(days)
        return {"total_days": len(days), "calendar": days}


calendar_tool = FunctionTool(
    # display_name="calendar_tool",
    func=CalendarTool.run,
    # description="Generates a detailed calendar for the trip based on start and end dates.",
)
