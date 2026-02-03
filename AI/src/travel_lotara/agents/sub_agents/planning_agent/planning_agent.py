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

"""Planning agent for travel itinerary creation and management."""


from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from src.travel_lotara.tools import (
    memorize,
    chromadb_retrieval_tool,
)

from .prompt import *
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.shared_libraries import (
    TransportPlan,
    AccomodationPlan,
    ItineraryStructurePlan,
    Itinerary,
)
from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig
from src.travel_lotara.agents.tracing_config import setup_agent_tracing

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model
print(f"[DEBUG] Planning Agent using model: {MODEL_ID}")



# ## Constants for Itinerary Structuring Agent
# GOOGLE_SEARCH_NAME = "google_search_agent"
# GOOGLE_SEARCH_DESCRIPTION = "Perform Google searches to gather up-to-date information for itinerary planning about specified local attractions, locations, events, and activities."
# GOOGLE_SEARCH_OUTPUT_KEY = "google_search_results"
# GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS = True
# GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT = True

# # Google Search Agent Tool
# google_search_config = AgentConfig(
#     model=MODEL_ID,
#     name=GOOGLE_SEARCH_NAME,
#     description=GOOGLE_SEARCH_DESCRIPTION,
#     instruction=GOOGLE_SEARCH_INSTR,
#     # disallow_transfer_to_parent=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT,
#     # disallow_transfer_to_peers=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS,
#     output_key=GOOGLE_SEARCH_OUTPUT_KEY,
#     tools=[google_search],
#     # output_schema=ItineraryStructurePlan,
#     # generate_content_config=json_response_config,
# )
# google_search_agent = BaseAgent(
#     config=google_search_config
# ).create_agent()

# # Tracing
# setup_agent_tracing(google_search_agent, environment=settings.project_environment)

# ## Constants for Itinerary Structuring Agent
# GOOGLE_SEARCH_NAME = "google_search_agent"
# GOOGLE_SEARCH_DESCRIPTION = "Perform Google searches to gather up-to-date information for itinerary planning about specified local attractions, locations, events, and activities."
# GOOGLE_SEARCH_OUTPUT_KEY = "google_search_results"
# GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS = True
# GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT = True

# # Google Search Agent Tool
# google_search_config = AgentConfig(
#     model=MODEL_ID,
#     name=GOOGLE_SEARCH_NAME,
#     description=GOOGLE_SEARCH_DESCRIPTION,
#     instruction=GOOGLE_SEARCH_INSTR,
#     # disallow_transfer_to_parent=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT,
#     # disallow_transfer_to_peers=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS,
#     output_key=GOOGLE_SEARCH_OUTPUT_KEY,
#     tools=[google_search],
#     # output_schema=ItineraryStructurePlan,
#     # generate_content_config=json_response_config,
# )
# google_search_agent = BaseAgent(
#     config=google_search_config
# ).create_agent()

# # Tracing
# setup_agent_tracing(google_search_agent, environment=settings.project_environment)


# ========================================
# RETRIEVAL AGENT FACTORY FUNCTIONS
# ========================================
# These create NEW instances each time to avoid the "already has parent" error
# when using agents in ParallelAgent

def create_attraction_retrieval_agent():
    """Create a new attraction retrieval agent instance."""
    instruction = """Retrieve Vietnam tourism attractions using the available retrieval tool.

Build a natural language query from the state:
- Read inspiration_output for recommended regions
- Read travel_style, budget, companions for user preferences
- Combine into a descriptive query

Example query: "Find cultural destinations in Nha Trang and Hoi An for solo traveler with midrange budget"

Call the retrieval tool with:
- query: your constructed query
- top_k: 10

Return the complete tool response containing location data with Images, Ratings, Hotels, Destinations, and Activities."""
    
    config = AgentConfig(
        model=MODEL_ID,
        name="attraction_retrieval_agent",
        description="Retrieve relevant local attractions and points of interest based on user preferences and itinerary context.",
        instruction=instruction,
        output_key="rag_attractions",
        tools=[chromadb_retrieval_tool],
    )
    agent = BaseAgent(config=config).create_agent()
    setup_agent_tracing(agent, environment=settings.project_environment)
    return agent


def create_hotel_retrieval_agent():
    """Create a new hotel retrieval agent instance."""
    instruction = """Retrieve Vietnam hotels and accommodations using the available retrieval tool.

Build query from state:
- Read inspiration_output for recommended regions  
- Read budget and accommodation preferences

Example query: "Find midrange hotels in Hanoi and Hue with standard accommodation"

Call the retrieval tool with query and top_k=5.
Return the response containing hotel data."""
    
    config = AgentConfig(
        model=MODEL_ID,
        name="hotel_retrieval_agent",
        description="Retrieve relevant hotel options based on user preferences and itinerary context.",
        instruction=instruction,
        output_key="rag_hotels",
        tools=[chromadb_retrieval_tool],
    )
    agent = BaseAgent(config=config).create_agent()
    setup_agent_tracing(agent, environment=settings.project_environment)
    return agent


def create_activities_retrieval_agent():
    """Create a new activities retrieval agent instance."""
    instruction = """Retrieve Vietnam activities and experiences using the available retrieval tool.

Build query from state:
- Read inspiration_output for recommended regions
- Read travel_style, activity level, and pace preferences

Example query: "Find cultural activities in Hanoi and Hoi An for medium activity level with balanced pace"

Call the retrieval tool with query and top_k=5.
Return the response containing activity data."""
    
    config = AgentConfig(
        model=MODEL_ID,
        name="activities_retrieval_agent",
        description="Retrieve relevant local activities and experiences based on user preferences and itinerary context.",
        instruction=instruction,
        output_key="rag_activities",
        tools=[chromadb_retrieval_tool],
    )
    agent = BaseAgent(config=config).create_agent()
    setup_agent_tracing(agent, environment=settings.project_environment)
    return agent


# Legacy singleton instances for backward compatibility
# WARNING: Do NOT use these in ParallelAgent - use factory functions instead
attraction_retrieval_agent = create_attraction_retrieval_agent()
hotel_retrieval_agent = create_hotel_retrieval_agent()
activities_retrieval_agent = create_activities_retrieval_agent()




## Planning Agent
planning_agent_config = AgentConfig(
    model=MODEL_ID,
    name="planning_agent",
    description="Create and manage travel itineraries based on user preferences and constraints.",
    instruction=PLANNING_AGENT_INSTR,
    # output_schema removed - formatter_agent handles final JSON output
    tools=[
        # AgentTool(agent=google_search_agent),
        FunctionTool(func=memorize),  # memorize is a function, must wrap in FunctionTool
        chromadb_retrieval_tool,  # Add ChromaDB retrieval tool
    ],
    output_key="itinerary",
)

planning_agent = BaseAgent(
    config=planning_agent_config
).create_agent()

# Tracing
setup_agent_tracing(planning_agent, environment=settings.project_environment)


