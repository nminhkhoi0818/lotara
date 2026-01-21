# travel_lotara/tools/shared_tools/pretrip_tool/visa_tool.py

from google.adk.tools import ToolContext, FunctionTool
from src.travel_lotara.database.repositories.pretrip_repo import PreTripRepository

repo = PreTripRepository()

def visa_requirements_tool(tool_context: ToolContext):
    state = tool_context.state

    nationality = state.get("passport_nationality", "US")
    destination = state["destination_country"]

    # 1️⃣ Try cache first
    visa_info = repo.get_visa(nationality, destination)
    if visa_info:
        state["visa_info"] = visa_info
        return {"visa_info": visa_info}

    # 2️⃣ Fallback logic (replace later with real API)
    visa_info = {
        "visa_required": nationality != "Vietnam",
        "stay_days": 90,
        "entry_type": "Tourist",
        "notes": "E-visa recommended"
    }

    # 3️⃣ Save cache
    repo.save_visa(nationality, destination, visa_info)

    state["visa_info"] = visa_info
    return {"visa_info": visa_info}


visa_tool = FunctionTool(
    # display_name="visa_tool",
    func=visa_requirements_tool,
    # description="Checks visa requirements for a destination.",
)