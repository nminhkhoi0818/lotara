"""
Opik Tracing Integration for Travel Lotara AI Agents.

Official Opik ADK Integration:
https://www.comet.com/docs/opik/integrations/adk

This uses the recommended approach with track_adk_agent_recursive
for automatic tracing of entire agent hierarchies.
"""

import os
from typing import Optional

try:
    from opik.integrations.adk import OpikTracer as OpikADKTracer, track_adk_agent_recursive
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    print("[WARNING] Opik not installed. Install with: pip install opik")


class OpikTracer:
    """Wrapper for official Opik ADK integration."""
    
    def __init__(self):
        self.enabled = OPIK_AVAILABLE and bool(os.getenv("OPIK_API_KEY"))
        self.project_name = os.getenv("OPIK_PROJECT", "Lotara")
        self.opik_tracer: Optional[OpikADKTracer] = None
        
        if self.enabled:
            self._initialize()
        else:
            print("[INFO] Opik tracing disabled (no API key or package not installed)")
    
    def _initialize(self):
        """Initialize Opik ADK tracer."""
        try:
            # Create OpikTracer from official integration
            self.opik_tracer = OpikADKTracer(
                name="lotara-travel-assistant",
                tags=["travel", "multi-agent", "gemini", "hackathon"],
                metadata={
                    "environment": os.getenv("ENV", "development"),
                    "framework": "google-adk",
                    "project": "lotara",
                },
                project_name=self.project_name
            )
            
            print(f"[OK] Opik tracing enabled for project: {self.project_name}")
            print(f"[INFO] View traces at: https://www.comet.com/opik/{self.project_name}/traces")
            
        except Exception as e:
            print(f"[WARNING] Failed to initialize Opik: {e}")
            self.enabled = False
    
    def instrument_agent(self, agent):
        """
        Instrument an ADK agent with automatic tracing.
        
        Uses track_adk_agent_recursive to automatically instrument
        the agent and all its sub-agents with callbacks for:
        - before/after agent execution
        - before/after model calls (with cost tracking)
        - before/after tool calls
        
        Args:
            agent: ADK LlmAgent to instrument
        
        Example:
            tracer = OpikTracer()
            tracer.instrument_agent(root_agent)
        """
        if not self.enabled or not self.opik_tracer:
            return
        
        try:
            # Use official track_adk_agent_recursive for automatic instrumentation
            # This recursively adds Opik callbacks to the agent and all sub-agents
            track_adk_agent_recursive(agent, self.opik_tracer)
            print(f"[OK] Instrumented agent '{agent.name}' with Opik tracing")
        except Exception as e:
            print(f"[WARNING] Failed to instrument agent: {e}")
    
    def flush(self):
        """
        Ensure all traces are sent to Opik before exit.
        
        Call this before your script exits to ensure all traces are uploaded.
        """
        if not self.enabled or not self.opik_tracer:
            return
        
        try:
            # Call flush on the OpikTracer instance
            self.opik_tracer.flush()
            print("[INFO] Traces flushed to Opik")
        except Exception as e:
            print(f"[WARNING] Failed to flush traces: {e}")


# Global singleton instance
_tracer_instance: Optional[OpikTracer] = None


def get_tracer() -> OpikTracer:
    """Get or create the global OpikTracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = OpikTracer()
    return _tracer_instance


def flush_traces():
    """Flush all pending traces to Opik."""
    tracer = get_tracer()
    tracer.flush()
