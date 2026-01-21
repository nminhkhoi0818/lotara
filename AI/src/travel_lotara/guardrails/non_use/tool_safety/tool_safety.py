# Tool Guard (Runtime Tool Safety)

# Every tool call must be:
# Authorized
# Input-validated
# Timeout-safe
# Auditable


from ..scope_guard import AgentScopeGuard

class BaseTool:
    name: str

    def validate_input(self, **kwargs):
        raise NotImplementedError

    def execute(self, **kwargs):
        raise NotImplementedError


class ToolGuard:
    def __init__(self, scope_guard: AgentScopeGuard):
        self.scope_guard = scope_guard

    def run(self, tool: BaseTool, **kwargs):
        self.scope_guard.check_tool_access(tool.name)
        tool.validate_input(**kwargs)
        return tool.execute(**kwargs)



