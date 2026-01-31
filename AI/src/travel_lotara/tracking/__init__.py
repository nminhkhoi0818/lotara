"""
Opik Tracking Integration for Travel Lotara.

Official Opik ADK Integration using track_adk_agent_recursive.
See: https://www.comet.com/docs/opik/integrations/adk

Usage:
    from travel_lotara.tracking import get_tracer, flush_traces
    
    # Get tracer instance
    tracer = get_tracer()
    
    # Instrument agent (automatically instruments all sub-agents)
    tracer.instrument_agent(root_agent)
    
    # Run agent - tracing happens automatically!
    result = agent.run()
    
    # Flush traces before exit
    flush_traces()
"""

from .opik_tracer import (
    OpikTracer,
    get_tracer,
    flush_traces,
)

__all__ = [
    "OpikTracer",
    "get_tracer",
    "flush_traces",
]
