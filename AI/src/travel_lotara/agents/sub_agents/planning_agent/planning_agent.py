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
    calendar_tool, 
    date_season_tool,
    memorize,
    google_search_grounding_tool
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

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model

# ## Constants for Transport Planner Agent
# TRANSPORT_PLANNER_NAME = "transport_planner_agent"
# TRANSPORT_PLANNER_DESCRIPTION = "Plan and book transportation options for the trip."
# TRANSPORT_PLANNER_OUTPUT_KEY = "transport_plan"
# TRANSPORT_DISALLOW_TRANSFER_TO_PEERS = True
# TRANSPORT_DISALLOW_TRANSFER_TO_PARENT = True


# # Transport Planner Agent Tool

# transport_planner_config = AgentConfig(
#     model=MODEL_ID,
#     name=TRANSPORT_PLANNER_NAME,
#     description=TRANSPORT_PLANNER_DESCRIPTION,
#     instruction=TRANSPORT_PLANNER_INSTR,
#     disallow_transfer_to_parent=TRANSPORT_DISALLOW_TRANSFER_TO_PARENT,
#     disallow_transfer_to_peers=TRANSPORT_DISALLOW_TRANSFER_TO_PEERS,
#     output_key=TRANSPORT_PLANNER_OUTPUT_KEY,
#     output_schema=TransportPlan,
# )

# transport_planner_agent = BaseAgent(
#     config=transport_planner_config
# ).create_agent()

# ## Constants for Accomodation Planner Agent
# ACCOMODATION_PLANNER_NAME = "accomodation_planner_agent"
# ACCOMODATION_PLANNER_DESCRIPTION = "Plan and book accommodations for the trip."
# ACCOMODATION_PLANNER_OUTPUT_KEY = "accomodation_plan"
# ACCOMODATION_DISALLOW_TRANSFER_TO_PEERS = True
# ACCOMODATION_DISALLOW_TRANSFER_TO_PARENT = True

# # Accomodation Planner Agent Tool
# accomodation_planner_config = AgentConfig(
#     model=MODEL_ID,
#     name=ACCOMODATION_PLANNER_NAME,
#     description=ACCOMODATION_PLANNER_DESCRIPTION,
#     instruction=ACCOMODATION_PLANNER_INSTR,
#     disallow_transfer_to_parent=ACCOMODATION_DISALLOW_TRANSFER_TO_PARENT,
#     disallow_transfer_to_peers=ACCOMODATION_DISALLOW_TRANSFER_TO_PEERS,
#     output_key=ACCOMODATION_PLANNER_OUTPUT_KEY,
#     output_schema=AccomodationPlan,
# )
# accomodation_planner_agent = BaseAgent(
#     config=accomodation_planner_config
# ).create_agent()



# ## Constants for Itinerary Structuring Agent
# ITINERARY_STRUCTURING_NAME = "itinerary_structuring_agent"
# ITINERARY_STRUCTURING_DESCRIPTION = "Structure the overall itinerary based on booked transport and accommodation."
# ITINERARY_STRUCTURING_OUTPUT_KEY = "itinerary_structure_plan"
# ITINERARY_DISALLOW_TRANSFER_TO_PEERS = True
# ITINERARY_DISALLOW_TRANSFER_TO_PARENT = True

# # Itinerary Structuring Agent Tool
# itinerary_structuring_config = AgentConfig(
#     model=MODEL_ID,
#     name=ITINERARY_STRUCTURING_NAME,
#     description=ITINERARY_STRUCTURING_DESCRIPTION,
#     instruction=ITINERARY_STRUCTURING_INSTR,
#     disallow_transfer_to_parent=ITINERARY_DISALLOW_TRANSFER_TO_PARENT,
#     disallow_transfer_to_peers=ITINERARY_DISALLOW_TRANSFER_TO_PEERS,
#     output_key=ITINERARY_STRUCTURING_OUTPUT_KEY,
#     output_schema=ItineraryStructurePlan,
#     generate_content_config=json_response_config,
# )
# itinerary_structuring_agent = BaseAgent(
#     config=itinerary_structuring_config
# ).create_agent()


## Planning Agent
planning_agent_config = AgentConfig(
    model=MODEL_ID,
    name="planning_agent",
    description="Create and manage travel itineraries based on user preferences and constraints.",
    instruction=PLANNING_AGENT_INSTR,
    output_schema=Itinerary,  # Return complete itinerary in JSON format
    tools=[
        # AgentTool(agent=transport_planner_agent), 
        # AgentTool(agent=accomodation_planner_agent),
        # AgentTool(agent=itinerary_structuring_agent),
        google_search_grounding_tool,
        calendar_tool,
        date_season_tool,
        FunctionTool(func=memorize), 
    ],
    output_key="itinerary",
)

planning_agent = BaseAgent(
    config=planning_agent_config
).create_agent()

