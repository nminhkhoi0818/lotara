"""
Opik Tracking Integration for Travel Lotara.

Official Opik ADK Integration using track_adk_agent_recursive.
See: https://www.comet.com/docs/opik/integrations/adk

Usage:
    # Agent Tracing
    from travel_lotara.tracking import get_tracer, flush_traces
    
    tracer = get_tracer()
    tracer.instrument_agent(root_agent)
    
    # Tool Tracing with Decorators
    from travel_lotara.tracking import trace_tool, trace_async_tool
    
    @trace_tool(name="user_lookup", tags=["context", "user"])
    def get_user_profile(user_id: str) -> dict:
        return {"user_id": user_id}
    
    @trace_async_tool(name="api_call", tags=["external"])
    async def fetch_data(url: str):
        # async implementation
        pass
    
    # Flush traces before exit
    flush_traces()
"""

from .opik_tracer import (
    OpikTracer,
    get_tracer,
    flush_traces,
    trace_tool,
    trace_async_tool,
)
from .progress_tracker import (
    ProgressTracker,
    ProgressEventType,
    ProgressEvent,
    track_agent_start,
    track_tool_call,
    track_tool_result,
    track_model_call,
    track_thinking,
)

__all__ = [
    "OpikTracer",
    "get_tracer",
    "flush_traces",
    "trace_tool",
    "trace_async_tool",
    "ProgressTracker",
    "ProgressEventType",
    "ProgressEvent",
    "track_agent_start",
    "track_tool_call",
    "track_tool_result",
    "track_model_call",
    "track_thinking",
]
