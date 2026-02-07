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

"""Pre-agent for prompt generation and optimization."""

from .prompt import *
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.tracing_config import setup_agent_tracing
from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig

# GLOBAL SETTINGS
settings = get_settings()
MODEL_ID = settings.model
print(f"[DEBUG] Pre Agent using model: {MODEL_ID}")


## Pre Agent
pre_agent_config = AgentConfig(
    model=MODEL_ID,
    name="pre_agent",
    description="Generate optimized prompt for inspiration agent based on user input and context.",
    instruction=PRE_AGENT_INSTR,
    output_key="pre_output",
)

pre_agent = BaseAgent(
    config=pre_agent_config
).create_agent()

# Tracing
setup_agent_tracing(pre_agent, environment=settings.project_environment)