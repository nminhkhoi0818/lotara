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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent
from google.genai import types
# Lazy import to avoid circular dependency
# from src.travel_lotara.tools import _load_precreated_itinerary
from openinference.instrumentation import using_session

from .prompt import *
from src.travel_lotara.agents.sub_agents import (
    inspiration_agent,
    planning_agent,
    pretrip_agent,
)
from ..tools.context_tools import user_profile_tool 
from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.agents.callbacks import (
    before_agent_callback, 
    before_tool_callback,
    after_agent_callback
    # after_tool_callback
)
from src.travel_lotara.agents.shared_libraries import OutputMessage


settings = get_settings()
MODEL_ID = settings.model
ROOT_AGENT_NAME = "travel_lotara_root_agent"
ROOT_AGENT_DESCRIPTION = "A Travel Conceirge using the services of multiple sub-agents"

# Configure retry options for handling 429/503 errors
retry_config = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            initial_delay=60,  # 60s initial delay for rate limits
            attempts=5  # Try up to 5 times at ADK level
        )
    )
)


with using_session(session_id=uuid.uuid4()):
    # SequentialAgent requires name and sub_agents
    root_agent = SequentialAgent(
        name=ROOT_AGENT_NAME,
        sub_agents=[
            inspiration_agent,
            planning_agent,
            # pretrip_agent,
        ],
        after_agent_callback=after_agent_callback,
    )

# Instrument with Opik tracing (automatically instruments all sub-agents)
from src.travel_lotara.tracking import get_tracer
tracer = get_tracer()
tracer.instrument_agent(root_agent)