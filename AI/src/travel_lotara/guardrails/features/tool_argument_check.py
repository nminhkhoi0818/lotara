# (before_tool_callback)

# ============ Purpose:

#### + Validate tool inputs
#### + Prevent tool misuse

#### + Block expensive / dangerous calls

#### + Where it runs
# ✔ Before every tool execution
# ✔ Centralized logic


# guardrails/features/tool_argument_check.py
from google.adk.tools import ToolContext, BaseTool


def tool_argument_guard(
    tool: BaseTool,
    args: dict,
    ctx: ToolContext
) -> dict | None:
    """
    Runs before EVERY tool execution.
    Prevents misuse and invalid parameters.
    """

    # Example: transport search
    if tool.name == "transport_search":
        budget = args.get("budget")
        if budget is not None and budget <= 0:
            return {
                "error": "INVALID_ARGUMENT",
                "message": "Budget must be a positive number."
            }

    # Example: calendar tool
    if tool.name == "calendar_tool":
        if "date" not in args:
            return {
                "error": "MISSING_ARGUMENT",
                "message": "Missing required 'date' parameter."
            }

    return None
