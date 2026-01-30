"""
Opik Tracing Integration for Travel Lotara AI Agents.

Official Opik ADK Integration:
https://www.comet.com/docs/opik/integrations/adk

This module provides comprehensive tracing capabilities:
- Automatic agent hierarchy tracing via track_adk_agent_recursive
- Tool function tracing via @trace_tool decorator
- Hybrid tracing combining callbacks and decorators
- Custom metadata and tags support
"""

import os
import functools
from typing import Optional, Dict, Any, Callable, List
from src.travel_lotara.config import get_settings

settings = get_settings()

try:
    import opik
    from opik.integrations.adk import OpikTracer as OpikADKTracer, track_adk_agent_recursive
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    print("[WARNING] Opik not installed. Install with: pip install opik")


class OpikTracer:
    """
    Wrapper for official Opik ADK integration with enhanced capabilities.
    
    Features:
    - Automatic agent hierarchy instrumentation
    - Tool function decorators
    - Custom metadata and tags
    - Proper error handling and logging
    - Context manager support
    
    Example:
        # Basic usage
        tracer = OpikTracer()
        tracer.instrument_agent(root_agent)
        
        # With custom metadata
        tracer.instrument_agent(
            agent,
            metadata={"team": "planning", "version": "1.0"}
        )
    """
    
    def __init__(self):
        """Initialize OpikTracer with configuration from settings."""
        self.opik_api_key = settings.opik_api_key or os.getenv("OPIK_API_KEY")
        self.project_name = settings.opik_project_name or os.getenv("OPIK_PROJECT_NAME", "Lotara")
        self.workspace_name = settings.opik_workspace_name or os.getenv("OPIK_WORKSPACE", "lotara-workspace")
        self.project_environment = settings.project_environment or os.getenv("ENV", "development")
        
        self.enabled = OPIK_AVAILABLE and bool(self.opik_api_key)
        self.opik_tracer: Optional[OpikADKTracer] = None
        
        # Registry to track all created tracers for proper flushing
        self._tracer_registry: List[OpikADKTracer] = []
        
        if self.enabled:
            self._configure_opik()
            self._initialize()
        else:
            if not OPIK_AVAILABLE:
                print("[INFO] Opik tracing disabled (package not installed)")
            else:
                print("[INFO] Opik tracing disabled (no API key configured)")
    
    def _configure_opik(self):
        """Configure Opik with API key and workspace."""
        try:
            opik.configure(
                api_key=self.opik_api_key,
                workspace=self.workspace_name
            )
            print(f"[OK] Opik configured for workspace: {self.workspace_name}")
            
        except Exception as e:
            print(f"[WARNING] Failed to configure Opik: {e}")
            self.enabled = False

    def _initialize(self):
        """Initialize the global Opik ADK tracer."""
        try:
            # Create the main OpikTracer for the application
            self.opik_tracer = OpikADKTracer(
                name="lotara-travel-assistant",
                tags=["travel", "multi-agent", "gemini", "hackathon"],
                metadata={
                    "environment": self.project_environment,
                    "framework": "google-adk",
                    "project": self.project_name,
                },
                project_name=self.project_name
            )
            
            # Register the global tracer
            self._tracer_registry.append(self.opik_tracer)
            
            print(f"[OK] Opik tracing enabled for project: {self.project_name}")
            print(f"[INFO] View traces at: https://www.comet.com/{self.workspace_name}/{self.project_name}/traces")
            
        except Exception as e:
            print(f"[WARNING] Failed to initialize Opik: {e}")
            self.enabled = False
    
    def create_agent_tracer(
        self,
        agent_name: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[OpikADKTracer]:
        """
        Create a dedicated tracer for a specific agent.
        
        This is useful when you want different agents to have separate
        trace configurations or metadata.
        
        Args:
            agent_name: Name of the agent
            tags: Custom tags for this agent's traces
            metadata: Custom metadata for this agent
            
        Returns:
            OpikADKTracer instance or None if tracing is disabled
            
        Example:
            planning_tracer = tracer.create_agent_tracer(
                "planning_agent",
                tags=["planning", "itinerary"],
                metadata={"team": "planning"}
            )
        """
        if not self.enabled:
            return None
            
        try:
            agent_metadata = {
                "environment": self.project_environment,
                "framework": "google-adk",
                "project": self.project_name,
                "agent": agent_name,
            }
            if metadata:
                agent_metadata.update(metadata)
            
            agent_tags = tags or []
            
            agent_tracer = OpikADKTracer(
                name=agent_name,
                tags=agent_tags,
                metadata=agent_metadata,
                project_name=self.project_name
            )
            
            # Register the agent-specific tracer for flushing
            self._tracer_registry.append(agent_tracer)
            
            print(f"[OK] Created tracer for agent: {agent_name}")
            return agent_tracer
            
        except Exception as e:
            print(f"[WARNING] Failed to create agent tracer: {e}")
            return None
    
    def instrument_agent(
        self,
        agent,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        use_dedicated_tracer: bool = False
    ):
        """
        Instrument an ADK agent with automatic tracing.
        
        Uses track_adk_agent_recursive to automatically instrument
        the agent and all its sub-agents with callbacks for:
        - before/after agent execution
        - before/after model calls (with cost tracking)
        - before/after tool calls
        
        Args:
            agent: ADK LlmAgent to instrument
            metadata: Optional custom metadata for this agent
            tags: Optional custom tags for this agent
            use_dedicated_tracer: If True, creates a dedicated tracer for this agent
        
        Example:
            tracer = OpikTracer()
            
            # Basic usage
            tracer.instrument_agent(root_agent)
            
            # With custom metadata
            tracer.instrument_agent(
                planning_agent,
                metadata={"team": "planning", "version": "2.0"},
                tags=["planning", "itinerary"]
            )
        """
        if not self.enabled:
            return
        
        try:
            # Determine which tracer to use
            if use_dedicated_tracer:
                agent_tracer = self.create_agent_tracer(
                    agent.name,
                    tags=tags,
                    metadata=metadata
                )
            else:
                agent_tracer = self.opik_tracer
            
            if not agent_tracer:
                print(f"[WARNING] No tracer available for agent: {agent.name}")
                return
            
            # Use official track_adk_agent_recursive for automatic instrumentation
            # This recursively adds Opik callbacks to the agent and all sub-agents
            track_adk_agent_recursive(agent, agent_tracer)
            
            metadata_str = f" with metadata: {metadata}" if metadata else ""
            tags_str = f" and tags: {tags}" if tags else ""
            print(f"[OK] Instrumented agent '{agent.name}'{metadata_str}{tags_str}")
            
        except Exception as e:
            print(f"[WARNING] Failed to instrument agent '{agent.name}': {e}")
    
    def flush(self):
        """
        Ensure all traces are sent to Opik before exit.
        
        This flushes ALL tracers including:
        - The global tracer (self.opik_tracer)
        - All agent-specific tracers created via create_agent_tracer()
        
        Call this before your script exits to ensure all traces are uploaded.
        
        Example:
            tracer = OpikTracer()
            # ... your code ...
            tracer.flush()
        """
        if not self.enabled:
            return
        
        if not self._tracer_registry:
            print("[INFO] No tracers to flush")
            return
        
        flushed_count = 0
        failed_count = 0
        
        for tracer in self._tracer_registry:
            try:
                tracer.flush()
                flushed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"[WARNING] Failed to flush tracer: {e}")
        
        if flushed_count > 0:
            print(f"[INFO] Flushed {flushed_count} tracer(s) to Opik")
        if failed_count > 0:
            print(f"[WARNING] Failed to flush {failed_count} tracer(s)")


# Global singleton instance
_tracer_instance: Optional[OpikTracer] = None


def get_tracer() -> OpikTracer:
    """
    Get or create the global OpikTracer instance.
    
    Returns:
        OpikTracer: Global tracer instance
        
    Example:
        from src.travel_lotara.tracking import get_tracer
        
        tracer = get_tracer()
        tracer.instrument_agent(my_agent)
    """
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = OpikTracer()
    return _tracer_instance


def flush_traces():
    """
    Flush all pending traces to Opik.
    
    Convenience function to flush traces from the global tracer.
    
    Example:
        from src.travel_lotara.tracking import flush_traces
        
        # At the end of your script
        flush_traces()
    """
    tracer = get_tracer()
    tracer.flush()


def trace_tool(
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace tool functions with Opik.
    
    This decorator uses Opik's @track decorator to create spans for tool
    functions. When used with instrumented agents, these spans will appear
    as children of the agent's tool execution spans.
    
    Args:
        name: Optional custom name for the trace (defaults to function name)
        tags: Optional tags for the trace
        metadata: Optional metadata for the trace
        
    Returns:
        Decorated function with tracing
        
    Example:
        from src.travel_lotara.tracking import trace_tool
        
        @trace_tool(name="user_profile_lookup", tags=["context", "user"])
        def get_user_profile(user_id: str) -> dict:
            # Your tool implementation
            return {"user_id": user_id, "preferences": [...]}
        
        # Multi-step tool with internal tracing
        @trace_tool(name="advanced_search", tags=["search", "multi-step"])
        def advanced_search(query: str) -> dict:
            # Each internal step can also be traced
            results = _search_step_1(query)
            processed = _process_results(results)
            return processed
        
        @trace_tool(name="search_step_1", tags=["search", "internal"])
        def _search_step_1(query: str):
            # Internal step implementation
            pass
    """
    if not OPIK_AVAILABLE:
        # If Opik is not available, return a no-op decorator
        def decorator(func):
            return func
        return decorator
    
    def decorator(func: Callable) -> Callable:
        trace_name = name or func.__name__
        trace_tags = tags or []
        trace_metadata = metadata or {}
        
        # Add function info to metadata
        trace_metadata.update({
            "function": func.__name__,
            "module": func.__module__,
            "type": "tool"
        })
        
        @functools.wraps(func)
        @track(name=trace_name, tags=trace_tags, metadata=trace_metadata)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def trace_async_tool(
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace async tool functions with Opik.
    
    Similar to trace_tool but for async functions.
    
    Args:
        name: Optional custom name for the trace
        tags: Optional tags for the trace
        metadata: Optional metadata for the trace
        
    Returns:
        Decorated async function with tracing
        
    Example:
        from src.travel_lotara.tracking import trace_async_tool
        
        @trace_async_tool(name="async_api_call", tags=["api", "external"])
        async def fetch_weather_data(city: str) -> dict:
            # Async implementation
            async with httpx.AsyncClient() as client:
                response = await client.get(f"/weather/{city}")
                return response.json()
    """
    if not OPIK_AVAILABLE:
        def decorator(func):
            return func
        return decorator
    
    def decorator(func: Callable) -> Callable:
        trace_name = name or func.__name__
        trace_tags = tags or []
        trace_metadata = metadata or {}
        
        trace_metadata.update({
            "function": func.__name__,
            "module": func.__module__,
            "type": "async_tool"
        })
        
        @functools.wraps(func)
        @track(name=trace_name, tags=trace_tags, metadata=trace_metadata)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
