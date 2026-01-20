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


from google.adk.tools.agent_tool import AgentTool
from travel_lotara.shared_libraries import types
from travel_lotara.sub_agents.pre_trip import prompt
from travel_lotara.tools.search import google_search_grounding
from google.adk.agents import Agent

from travel_lotara.settings import get_settings

from travel_lotara.agents.base_agent import BaseAgent, AgentConfig

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model

## Constants for Transport Planner Agent
TRANSPORT_PLANNER_NAME = "transport_planner_agent"
TRANSPORT_PLANNER_DESCRIPTION = "Plan and book transportation options for the trip."
TRANSPORT_PLANNER_OUTPUT_KEY = "transport_plan"


# Transport Planner Agent Tool

transport_planner_config = AgentConfig(
    model=MODEL_ID,
    name=TRANSPORT_PLANNER_NAME,
    description=TRANSPORT_PLANNER_DESCRIPTION,
    instruction=prompt.TRANSPORT_PLANNER_INSTR,
    output_key=TRANSPORT_PLANNER_OUTPUT_KEY,
    output_schema=types.TransportPlan,
)

transport_planner_agent = BaseAgent(
    config=transport_planner_config
).create_agent()

## Constants for Accomodation Planner Agent
ACCOMODATION_PLANNER_NAME = "accomodation_planner_agent"
ACCOMODATION_PLANNER_DESCRIPTION = "Plan and book accommodations for the trip."
ACCOMODATION_PLANNER_OUTPUT_KEY = "accomodation_plan"

# Accomodation Planner Agent Tool
accomodation_planner_config = AgentConfig(
    model=MODEL_ID,
    name=ACCOMODATION_PLANNER_NAME,
    description=ACCOMODATION_PLANNER_DESCRIPTION,
    instruction=prompt.ACCOMODATION_PLANNER_INSTR,
    output_key=ACCOMODATION_PLANNER_OUTPUT_KEY,
    output_schema=types.AccomodationPlan,
)
accomodation_planner_agent = BaseAgent(
    config=accomodation_planner_config
).create_agent()



## Constants for Itinerary Structuring Agent
ITINERARY_STRUCTURING_NAME = "itinerary_structuring_agent"
ITINERARY_STRUCTURING_DESCRIPTION = "Structure the overall itinerary based on booked transport and accommodation."
ITINERARY_STRUCTURING_OUTPUT_KEY = "itinerary_structure_plan"

# Itinerary Structuring Agent Tool
itinerary_structuring_config = AgentConfig(
    model=MODEL_ID,
    name=ITINERARY_STRUCTURING_NAME,
    description=ITINERARY_STRUCTURING_DESCRIPTION,
    instruction=prompt.ITINERARY_STRUCTURING_INSTR,
    output_key=ITINERARY_STRUCTURING_OUTPUT_KEY,
    output_schema=types.ItineraryStructurePlan,
)
itinerary_structuring_agent = BaseAgent(
    config=itinerary_structuring_config
).create_agent()


## Planning Agent
planning_agent_config = AgentConfig(
    model=MODEL_ID,
    name="planning_agent",
    description="Create and manage travel itineraries based on user preferences and constraints.",
    instruction=prompt.PLANNING_AGENT_INSTR,
    tools=[
        AgentTool(agent=transport_planner_agent), 
        AgentTool(agent=accomodation_planner_agent),
        AgentTool(agent=itinerary_structuring_agent)
    ],
)

planning_agent = BaseAgent(
    config=planning_agent_config
).create_agent()