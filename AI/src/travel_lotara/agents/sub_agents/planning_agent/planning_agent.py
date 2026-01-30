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
    memorize
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
from google.adk.tools import google_search
from src.travel_lotara.agents.tracing_config import setup_agent_tracing

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model
print(f"[DEBUG] Planning Agent using model: {MODEL_ID}")



## Constants for Itinerary Structuring Agent
GOOGLE_SEARCH_NAME = "google_search_agent"
GOOGLE_SEARCH_DESCRIPTION = "Perform Google searches to gather up-to-date information for itinerary planning about specified local attractions, locations, events, and activities."
GOOGLE_SEARCH_OUTPUT_KEY = "google_search_results"
GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS = True
GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT = True

# Google Search Agent Tool
google_search_config = AgentConfig(
    model=MODEL_ID,
    name=GOOGLE_SEARCH_NAME,
    description=GOOGLE_SEARCH_DESCRIPTION,
    instruction=GOOGLE_SEARCH_INSTR,
    # disallow_transfer_to_parent=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PARENT,
    # disallow_transfer_to_peers=GOOGLE_SEARCH_DISALLOW_TRANSFER_TO_PEERS,
    output_key=GOOGLE_SEARCH_OUTPUT_KEY,
    tools=[google_search],
    # output_schema=ItineraryStructurePlan,
    # generate_content_config=json_response_config,
)
google_search_agent = BaseAgent(
    config=google_search_config
).create_agent()

# Tracing
setup_agent_tracing(google_search_agent, environment=settings.project_environment)

## Planning Agent
planning_agent_config = AgentConfig(
    model=MODEL_ID,
    name="planning_agent",
    description="Create and manage travel itineraries based on user preferences and constraints.",
    instruction=PLANNING_AGENT_INSTR,
    output_schema=Itinerary,  # Removed to allow sequential flow - refactoring agent handles final output
    tools=[
        AgentTool(agent=google_search_agent),
        FunctionTool(func=memorize),  # memorize is a function, must wrap in FunctionTool
    ],
    output_key="itinerary",
)

planning_agent = BaseAgent(
    config=planning_agent_config
).create_agent()

# Tracing
setup_agent_tracing(planning_agent, environment=settings.project_environment)



# Refactored AgentTools for modular agents (not used directly here)
## Constants for Itinerary Structuring Agent
REFACTORING_OUTPUT_NAME = "refactoring_output_agent"
REFACTORING_OUTPUT_DESCRIPTION = "Refactor and restructure itinerary data into a standardized JSON format as per the defined schema."
REFACTORING_OUTPUT_OUTPUT_KEY = "refactored_itinerary"
REFACTORING_OUTPUT_DISALLOW_TRANSFER_TO_PEERS = True
REFACTORING_OUTPUT_DISALLOW_TRANSFER_TO_PARENT = True

# Refactoring Output Agent Tool
refactoring_output_config = AgentConfig(
    model=MODEL_ID,
    name=REFACTORING_OUTPUT_NAME,
    description=REFACTORING_OUTPUT_DESCRIPTION,
    instruction=REFACTORING_OUTPUT_INSTR,
    disallow_transfer_to_parent=REFACTORING_OUTPUT_DISALLOW_TRANSFER_TO_PARENT,
    disallow_transfer_to_peers=REFACTORING_OUTPUT_DISALLOW_TRANSFER_TO_PEERS,
    output_key=REFACTORING_OUTPUT_OUTPUT_KEY,
    output_schema=Itinerary,  # Final structured output
)
refactoring_output_agent = BaseAgent(
    config=refactoring_output_config
).create_agent()

# Tracing
setup_agent_tracing(refactoring_output_agent, environment=settings.project_environment)
