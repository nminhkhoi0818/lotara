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

"""Pre-Trip Agent for providing travel information before the trip."""


from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.travel_lotara.tools import (
    calendar_tool, 
    date_season_tool
)
from prompt import *
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.shared_libraries import types
from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model

## Constants for Budget & Cost Awareness Agent
BUDGET_AND_COST_AWARENESS_NAME = "budget_and_cost_awareness_agent"
BUDGET_AND_COST_AWARENESS_DESCRIPTION = "Provide budget and cost awareness information for the trip."
BUDGET_AND_COST_AWARENESS_OUTPUT_KEY = "budget_and_cost_awareness_pretrip"


# Budget & Cost Awareness Agent Tool
budget_and_cost_awareness_config = AgentConfig(
    model=MODEL_ID,
    name=BUDGET_AND_COST_AWARENESS_NAME,
    description=BUDGET_AND_COST_AWARENESS_DESCRIPTION,
    instruction=BUDGET_AND_COST_AWARENESS_INSTR,
    output_key=BUDGET_AND_COST_AWARENESS_OUTPUT_KEY,
    output_schema=types.BudgetAndCostAwarenessPretrip,
)
budget_and_cost_awareness_agent = BaseAgent(
    config=budget_and_cost_awareness_config
).create_agent()


## Constants for Packing & Prep Agent
PACKING_AND_PREP_NAME = "packing_and_prep_agent"
PACKING_AND_PREP_DESCRIPTION = "Provide packing and preparation information for the trip."
PACKING_AND_PREP_OUTPUT_KEY = "packing_and_prep_pretrip"

# Packing & Prep Agent Tool
packing_and_prep_config = AgentConfig(
    model=MODEL_ID,
    name=PACKING_AND_PREP_NAME,
    description=PACKING_AND_PREP_DESCRIPTION,
    instruction=PACKING_AND_PREP_INSTR,
    output_key=PACKING_AND_PREP_OUTPUT_KEY,
    output_schema=types.PackingAndPrepPretrip,
)
packing_and_prep_agent = BaseAgent(
    config=packing_and_prep_config
).create_agent()


## Constants for Readiness Check Agent
READINESS_CHECK_NAME = "readiness_check_agent"
READINESS_CHECK_DESCRIPTION = "Perform readiness checks for the trip."
READINESS_CHECK_OUTPUT_KEY = "readiness_check_pretrip"

# Readiness Check Agent Tool
readiness_check_config = AgentConfig(
    model=MODEL_ID,
    name=READINESS_CHECK_NAME,
    description=READINESS_CHECK_DESCRIPTION,
    instruction=READINESS_CHECK_INSTR,
    output_key=READINESS_CHECK_OUTPUT_KEY,
    output_schema=types.ReadinessCheckPretrip,
)
readiness_check_agent = BaseAgent(
    config=readiness_check_config
).create_agent()


## PreTrip Agent
pretrip_agent_config = AgentConfig(
    model=MODEL_ID,
    name="pretrip_agent",
    description="Provide travel information and preparation guidance before the trip.",
    instruction=PRETRIP_AGENT_INSTR,
    tools=[
        calendar_tool,
        date_season_tool,
        AgentTool(agent=budget_and_cost_awareness_agent), 
        AgentTool(agent=packing_and_prep_agent),
        AgentTool(agent=readiness_check_agent)
    ],
)

pretrip_agent = BaseAgent(
    config=pretrip_agent_config
).create_agent()