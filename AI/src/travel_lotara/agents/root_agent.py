# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstration of Travel AI Conceirge using Agent Development Kit"""

import uuid

from google.adk.agents import SequentialAgent, ParallelAgent
from google.genai import types
from openinference.instrumentation import using_session

from travel_lotara.agents.sub_agents import formatter_agent

from .prompt import *
from src.travel_lotara.agents.sub_agents import (
    inspiration_agent,
    planning_agent,
    formatter_agent,
    # Import factory functions instead of singleton agents
    create_attraction_retrieval_agent,
    create_hotel_retrieval_agent,
    create_activities_retrieval_agent,
)
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.callbacks import (
    after_agent_callback
)
from src.travel_lotara.agents.shared_libraries import OutputMessage

# Tracing 
from src.travel_lotara.tracking import get_tracer
from src.travel_lotara.agents.tracing_config import (
    setup_agent_tracing
)


settings = get_settings()
MODEL_ID = settings.model
ROOT_AGENT_NAME = "travel_lotara_root_agent"
ROOT_AGENT_DESCRIPTION = "A Travel Conceirge using the services of multiple sub-agents"


# Global variable to hold the singleton instance
_root_agent_instance = None


def get_root_agent():
    """
    Get or create the root agent instance (singleton pattern).
    
    This ensures the root agent is only created once, even if the module
    is imported multiple times.
    
    Returns:
        The root agent instance
    """
    global _root_agent_instance
    
    if _root_agent_instance is not None:
        return _root_agent_instance
    
    # Create parallel agent 
    parallel_agent = ParallelAgent(
        name="rag_retrieval_parallel_agent",
        sub_agents=[
            create_attraction_retrieval_agent(),
            create_hotel_retrieval_agent(),
            create_activities_retrieval_agent(),
        ]
    )
    
    # Instrument parallel agent with Opik tracing
    setup_agent_tracing(parallel_agent, environment=settings.project_environment)
    
    with using_session(session_id=uuid.uuid4()):
        # SequentialAgent requires name and sub_agents
        # Flow: inspiration_agent → RAG retrieval (parallel) → planning_agent → formatter_agent
        # Create new instances of retrieval agents to avoid "already has parent" error
        _root_agent_instance = SequentialAgent(
            name=ROOT_AGENT_NAME,
            sub_agents=[
                inspiration_agent,
                parallel_agent,
                planning_agent,
                formatter_agent
            ],
            after_agent_callback=after_agent_callback,
        )

    # Instrument with Opik tracing (automatically instruments all sub-agents)
    setup_agent_tracing(_root_agent_instance, environment=settings.project_environment)
    
    return _root_agent_instance


# For backward compatibility, create a module-level reference
# This will be created on first access
def __getattr__(name):
    """
    Lazy loading of root_agent.
    
    This allows the module to be imported without immediately creating the agent.
    """
    if name == "root_agent":
        return get_root_agent()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")