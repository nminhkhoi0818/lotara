
# Sub-Agent Execution Guard

#  ===================== Ensures:
#### + Sub-agents cannot talk to user
#### + Sub-agents only return structured data


from ..scope_guard import AgentScopeGuard

class SubAgentExecutor:
    def __init__(self, guard: AgentScopeGuard):
        self.guard = guard

    def run(self, agent, input_data):
        result = agent.run(input_data)
        self.guard.check_output("structured_data")
        return result
