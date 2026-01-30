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

from google.adk.agents import SequentialAgent
from google.genai import types
from openinference.instrumentation import using_session

from .prompt import *
from src.travel_lotara.agents.sub_agents import (
    pre_agent,
    inspiration_agent,
    planning_agent,
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


with using_session(session_id=uuid.uuid4()):
    # SequentialAgent requires name and sub_agents
    # Flow: pre_agent → inspiration_agent → planning_agent
    # Only planning_agent has output_schema (Itinerary)
    root_agent = SequentialAgent(
        name=ROOT_AGENT_NAME,
        sub_agents=[
            pre_agent,
            inspiration_agent,
            planning_agent,
        ],
        after_agent_callback=after_agent_callback,
    )

# Instrument with Opik tracing (automatically instruments all sub-agents)
setup_agent_tracing(root_agent, environment=settings.project_environment)