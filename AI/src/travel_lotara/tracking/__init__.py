"""
Opik Tracking Integration for Travel Lotara.

Tracing is handled automatically by the Opik ADK integration in agent.py.
See: https://www.comet.com/docs/opik/integrations/adk

The integration automatically:
- Logs all agent executions
- Tracks tool calls
- Records LLM interactions
- Calculates costs
- Generates agent graphs

Usage:
    from travel_lotara.tracking import opik_tracer, flush_traces
    
    # Traces are automatic when running agents
    # Call flush_traces() before script exit to ensure all traces are sent
    
Example with custom spans:
    from travel_lotara.tracking import get_tracer
    
    tracer = get_tracer()
    with tracer.span("custom_operation") as span:
        span.set_attribute("key", "value")
        # your code here
"""

# Re-export from agent.py for convenience
try:
    from src.travel_lotara.agent import opik_tracer, flush_traces, get_tracer

    __all__ = ["opik_tracer", "flush_traces", "get_tracer"]
except ImportError:
    # Agent module not yet loaded or Opik not installed
    opik_tracer = None
    
    def flush_traces():
        pass
    
    def get_tracer():
        return None
    
    __all__ = ["opik_tracer", "flush_traces", "get_tracer"]
