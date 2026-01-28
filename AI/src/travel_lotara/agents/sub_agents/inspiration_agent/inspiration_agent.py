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
from google.adk.tools.agent_tool import AgentTool
from src.travel_lotara.tools import (
    user_profile_tool, 
    date_season_tool
)
# from src.travel_lotara.tools.search import google_search_grounding

from .prompt import *
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.shared_libraries import (
    DestinationDiscoveryPlan,
    ThemeAndStylePlan,
    ConstraintAlignmentPlan,
    OutputMessage,
    Inpsiration_Output
)
# from src.travel_lotara.tools import (
#     memorize
# )
from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model
print(f"[DEBUG] Inspiration Agent using model: {MODEL_ID}")

# ## Constants for Destination Discovery Agent
# DESTINATION_DISCOVERY_NAME = "destination_discovery_agent"
# DESTINATION_DISCOVERY_DESCRIPTION = "Discover and suggest travel destinations based on user preferences."
# DESTINATION_DISCOVERY_OUTPUT_KEY = "destination_discovery_plan"

# # Destination Discovery Agent Tool
# destination_discovery_config = AgentConfig(
#     model=MODEL_ID,
#     name=DESTINATION_DISCOVERY_NAME,
#     description=DESTINATION_DISCOVERY_DESCRIPTION,
#     instruction=DESTINATION_DISCOVERY_INSTR,
#     output_key=DESTINATION_DISCOVERY_OUTPUT_KEY,
# )

# destination_discovery_agent = BaseAgent(
#     config=destination_discovery_config
# ).create_agent()


# ## Constants for THEME&STYLE Agent
# THEME_AND_STYLE_NAME = "theme_and_style_agent"
# THEME_AND_STYLE_DESCRIPTION = "Suggest travel themes and styles based on user interests."
# THEME_AND_STYLE_OUTPUT_KEY = "theme_and_style_plan"

# # THEME&STYLE Agent Tool
# theme_and_style_config = AgentConfig(
#     model=MODEL_ID,
#     name=THEME_AND_STYLE_NAME,
#     description=THEME_AND_STYLE_DESCRIPTION,
#     instruction=THEME_AND_STYLE_INSTR,
#     output_key=THEME_AND_STYLE_OUTPUT_KEY,
# )
# theme_and_style_agent = BaseAgent(
#     config=theme_and_style_config
# ).create_agent()



# ## Constants for Constrant Alignment Agent
# CONSTRANT_ALIGNMENT_NAME = "constraint_alignment_agent"
# CONSTRANT_ALIGNMENT_DESCRIPTION = "Align travel plans with user constraints such as budget and time."
# CONSTRANT_ALIGNMENT_OUTPUT_KEY = "constraint_alignment_plan"

# # Constrant Alignment Agent Tool
# constraint_alignment_config = AgentConfig(
#     model=MODEL_ID,
#     name=CONSTRANT_ALIGNMENT_NAME,
#     description=CONSTRANT_ALIGNMENT_DESCRIPTION,
#     instruction=CONSTRAINT_ALIGNMENT_INSTR,
#     output_key=CONSTRANT_ALIGNMENT_OUTPUT_KEY,
# )
# constraint_alignment_agent = BaseAgent(
#     config=constraint_alignment_config
# ).create_agent()


## Inspiration Agent
inspiration_agent_config = AgentConfig(
    model=MODEL_ID,
    name="inspiration_agent",
    description="Provide travel inspiration based on user preferences and constraints.",
    instruction=INSPIRATION_AGENT_INSTR,
    # tools=[
    #     user_profile_tool,
    #     date_season_tool,
    #     AgentTool(agent=destination_discovery_agent), 
    #     AgentTool(agent=theme_and_style_agent),
    #     AgentTool(agent=constraint_alignment_agent)
    # ],
    output_schema=Inpsiration_Output,
    output_key="inspiration_output",
)

inspiration_agent = BaseAgent(
    config=inspiration_agent_config
).create_agent()