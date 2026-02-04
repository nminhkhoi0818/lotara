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

"""Formatter agent for travel itinerary creation and management."""


from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

from .prompt import *
from src.travel_lotara.config.settings import get_settings, JSON_GENERATION_CONFIG
from src.travel_lotara.config.logging_config import get_logger
from src.travel_lotara.agents.shared_libraries import Itinerary

from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig
from src.travel_lotara.agents.tracing_config import setup_agent_tracing

# GLOBAL SETTINGS
settings = get_settings()
logger = get_logger(__name__)
MODEL_ID = settings.model
logger.debug(f"Formatter Agent using model: {MODEL_ID}")


## Formatter Agent
formatter_agent_config = AgentConfig(
    model=MODEL_ID,
    name="formatter_agent",
    description="Format and structure the generated travel inspiration into a user-friendly output.",
    instruction=FORMATTER_AGENT_INSTR,
    output_schema=Itinerary,  # Enforce JSON output in final schema
    generate_content_config=JSON_GENERATION_CONFIG,  # Optimized for JSON output
    output_key="formatter_output"
)

formatter_agent = BaseAgent(
    config=formatter_agent_config
).create_agent()


# Tracing
setup_agent_tracing(formatter_agent, environment=settings.project_environment)