"""
Centralized Opik Tracing Configuration for Travel Lotara Agents.

This module provides utilities for setting up comprehensive tracing
across all agents in the system with proper metadata, tags, and prompt tracking.
"""

from typing import Dict, Any, List, Optional
from src.travel_lotara.tracking import get_tracer
from src.travel_lotara.agents.prompt_manager import prompt_manager

# Agent metadata configurations
AGENT_METADATA_CONFIG = {
    "root_agent": {
        "tags": ["root", "sequential", "travel-concierge"],
        "metadata": {
            "agent_type": "sequential",
            "role": "orchestrator",
            "sub_agents": ["inspiration", "planning", "refactoring"],
            "version": "1.0"
        }
    },
    "inspiration_agent": {
        "tags": ["inspiration", "discovery", "preferences"],
        "metadata": {
            "agent_type": "single",
            "role": "inspiration",
            "team": "discovery",
            "purpose": "Generate travel inspiration based on user preferences",
            "version": "1.0"
        }
    },
    "planning_agent": {
        "tags": ["planning", "itinerary", "scheduling"],
        "metadata": {
            "agent_type": "single",
            "role": "planning",
            "team": "itinerary",
            "purpose": "Create detailed travel itineraries",
            "version": "1.0"
        }
    },
    "refactoring_output_agent": {
        "tags": ["refactoring", "output", "formatting"],
        "metadata": {
            "agent_type": "single",
            "role": "output_formatter",
            "team": "output",
            "purpose": "Refactor and structure itinerary output",
            "version": "1.0"
        }
    },
    "google_search_agent": {
        "tags": ["search", "google", "information-gathering"],
        "metadata": {
            "agent_type": "tool_agent",
            "role": "search",
            "team": "research",
            "purpose": "Perform Google searches for itinerary planning",
            "version": "1.0"
        }
    }
}


def get_agent_tracing_config(agent_name: str) -> Dict[str, Any]:
    """
    Get tracing configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Dictionary with 'tags' and 'metadata' keys
        
    Example:
        config = get_agent_tracing_config("inspiration_agent")
        tracer.instrument_agent(agent, **config)
    """
    config = AGENT_METADATA_CONFIG.get(
        agent_name,
        {
            "tags": ["agent", "custom"],
            "metadata": {
                "agent_type": "custom",
                "role": "unknown",
                "version": "1.0"
            }
        }
    )
    
    # Enrich with prompt metadata
    config = _enrich_with_prompt_metadata(agent_name, config)
    
    return config


def _enrich_with_prompt_metadata(agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich tracing configuration with prompt metadata.
    
    Args:
        agent_name: Name of the agent
        config: Existing configuration dictionary
        
    Returns:
        Enriched configuration with prompt metadata
    """
    try:
        prompt_metadata = prompt_manager.get_prompt_metadata(agent_name)
        
        if prompt_metadata:
            # Add prompt information to metadata
            config["metadata"]["prompt_version"] = prompt_metadata.get("version", "unknown")
            config["metadata"]["prompt_role"] = prompt_metadata.get("role", "unknown")
            config["metadata"]["prompt_description"] = prompt_metadata.get("description", "")
            config["metadata"]["prompt_last_updated"] = prompt_metadata.get("last_updated", "")
            
            # Add prompt tags if available
            prompt_tags = prompt_metadata.get("tags", [])
            if prompt_tags:
                config["tags"].extend([f"prompt:{tag}" for tag in prompt_tags])
    
    except Exception as e:
        # Don't fail if prompt metadata is unavailable
        pass
    
    return config


def instrument_agent_with_config(agent, agent_name: str, additional_metadata: Optional[Dict[str, Any]] = None):
    """
    Instrument an agent with predefined tracing configuration.
    
    Args:
        agent: The agent instance to instrument
        agent_name: Name of the agent (must match AGENT_METADATA_CONFIG keys)
        additional_metadata: Optional additional metadata to merge
        
    Example:
        from src.travel_lotara.agents.tracing_config import instrument_agent_with_config
        
        instrument_agent_with_config(inspiration_agent, "inspiration_agent")
    """
    tracer = get_tracer()
    
    if not tracer.enabled:
        print(f"[INFO] Tracing disabled, skipping instrumentation for {agent_name}")
        return
    
    config = get_agent_tracing_config(agent_name)
    
    # Merge additional metadata if provided
    if additional_metadata:
        config["metadata"].update(additional_metadata)
    
    # Add agent name to metadata
    config["metadata"]["agent_name"] = agent_name
    
    tracer.instrument_agent(
        agent,
        tags=config["tags"],
        metadata=config["metadata"]
    )
    
    print(f"[OK] Instrumented '{agent_name}' with Opik tracing")


def setup_agent_tracing(
    agent, # root_agent | inspiration_agent | planning_agent | refactoring_output_agent | google_search_agent
    environment: Optional[str] = None
):
    """
    Set up tracing for all agents in the system.
    
    This is a convenience function to instrument all agents at once.
    For hierarchical agents (like root_agent with sub-agents), you only
    need to instrument the root agent as sub-agents are automatically traced.
    
    Args:
        root_agent: The root sequential agent
        inspiration_agent: Optional inspiration agent (if instrumenting separately)
        planning_agent: Optional planning agent (if instrumenting separately)
        refactoring_output_agent: Optional refactoring agent (if instrumenting separately)
        google_search_agent: Optional search agent (if instrumenting separately)
        environment: Optional environment override (dev/staging/prod)
        
    Example:
        from src.travel_lotara.agents.tracing_config import setup_all_agent_tracing
        
        # For hierarchical setup (recommended)
        setup_all_agent_tracing(root_agent, environment="production")
        
        # For individual agent setup
        setup_all_agent_tracing(
            root_agent=root_agent,
            inspiration_agent=inspiration_agent,
            planning_agent=planning_agent,
            environment="development"
        )
    """
    from src.travel_lotara.config import get_settings
    
    settings = get_settings()
    env = environment or settings.project_environment
    
    # Common metadata for all agents
    common_metadata = {
        "environment": env,
        "model": settings.model,
        "project": settings.opik_project_name
    }
    
    # Instrument root agent (this automatically instruments sub-agents)
    print(f"[INFO - Opik Tracing] - Instrumenting root agent: {agent.name}")

    if agent.name == "travel_lotara_root_agent":
        root_config = get_agent_tracing_config("root_agent")
        
        # Add common metadata (environment, model, project)
        root_config["metadata"].update(common_metadata)
        
        tracer = get_tracer()
        tracer.instrument_agent(
            agent,
            tags=root_config["tags"],
            metadata=root_config["metadata"]
        )
        
        print(f"[OK] Instrumented root_agent and all sub-agents with Opik tracing")
    
    # Optionally instrument individual agents if provided
    # (useful for standalone testing or non-hierarchical setups)
    elif agent.name == "inspiration_agent":
        instrument_agent_with_config(agent, "inspiration_agent", common_metadata)
    
    elif agent.name == "planning_agent":
        instrument_agent_with_config(agent, "planning_agent", common_metadata)
    
    elif agent.name == "refactoring_output_agent":
        instrument_agent_with_config(agent, "refactoring_output_agent", common_metadata)
    
    elif agent.name == "google_search_agent":
        instrument_agent_with_config(agent, "google_search_agent", common_metadata)


def add_agent_metadata_config(agent_name: str, tags: List[str], metadata: Dict[str, Any]):
    """
    Add or update tracing configuration for a custom agent.
    
    Args:
        agent_name: Name of the agent
        tags: List of tags for tracing
        metadata: Metadata dictionary
        
    Example:
        add_agent_metadata_config(
            "custom_agent",
            tags=["custom", "experimental"],
            metadata={
                "agent_type": "experimental",
                "role": "testing",
                "team": "research"
            }
        )
    """
    AGENT_METADATA_CONFIG[agent_name] = {
        "tags": tags,
        "metadata": metadata
    }
    print(f"[INFO - Opik Tracing] - Added tracing config for '{agent_name}'")
   
