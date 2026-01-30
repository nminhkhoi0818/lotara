# travel_lotara/tools/context_tools/calendar_tool.py

from abc import abstractmethod
from datetime import datetime, timedelta
from google.adk.tools import ToolContext, FunctionTool
from ..base_tool import BaseTool
from src.travel_lotara.tracking import trace_tool

class CalendarTool(BaseTool):
    """Expands trip dates into structured calendar days."""

    name = "calendar_tool"

    def run(self, tool_context: ToolContext):
        state = tool_context.state

        start_date_str = state.get("start_date")
        end_date_str = state.get("end_date")
        
        if not start_date_str or not end_date_str:
            return {
                "error": "Dates not set yet",
                "instruction": "Please use memorize() to set start_date and end_date first",
                "example": "memorize('start_date', '2026-03-15')",
                "total_days": 0,
                "calendar": []
            }
        
        start = datetime.fromisoformat(start_date_str)
        end = datetime.fromisoformat(end_date_str)

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


@trace_tool(name="trip_calendar", tags=["context", "calendar", "dates"])
def get_trip_calendar(tool_context: ToolContext):
    """Generate trip calendar from start and end dates."""
    return CalendarTool().run(tool_context)

calendar_tool = FunctionTool(
    func=get_trip_calendar,
)
