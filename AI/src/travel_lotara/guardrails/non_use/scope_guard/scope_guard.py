# Agent Scope Guard (Prevent Agent Overreach)

#### + Problem this solves
#### + PlanningAgent booking hotels
#### + InspirationAgent suggesting visas
#### + Tool abuse


class AgentCapability:
    def __init__(self, allowed_tools: list[str], allowed_outputs: list[str]):
        self.allowed_tools = allowed_tools
        self.allowed_outputs = allowed_outputs


class AgentScopeGuard:
    def __init__(self, capability: AgentCapability):
        self.capability = capability

    def check_tool_access(self, tool_name: str):
        if tool_name not in self.capability.allowed_tools:
            raise PermissionError(
                f"Tool '{tool_name}' not allowed for this agent"
            )

    def check_output(self, output_type: str):
        if output_type not in self.capability.allowed_outputs:
            raise ValueError(
                f"Output type '{output_type}' not allowed"
            )
