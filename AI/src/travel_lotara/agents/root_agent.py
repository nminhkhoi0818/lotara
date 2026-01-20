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

from google.adk.agents import Agent
from openinference.instrumentation import using_session

from travel_lotara import prompt
from travel_lotara.agents.sub_agents import (
    inspiration_agent,
    planning_agent,
    pre_trip_agent,
)
from travel_lotara.tools.adk_memory import _load_precreated_itinerary

from travel_lotara.config.settings import get_settings

settings = get_settings()
MODEL_ID = settings.model
ROOT_AGENT_NAME = "travel_lotara_root_agent"
ROOT_AGENT_DESCRIPTION = "A Travel Conceirge using the services of multiple sub-agents"


with using_session(session_id=uuid.uuid4()):
    root_agent = Agent(
        model=MODEL_ID,
        name=ROOT_AGENT_NAME,
        description=ROOT_AGENT_DESCRIPTION,
        instruction=prompt.ROOT_AGENT_INSTR,
        sub_agents=[
            inspiration_agent,
            planning_agent,
            pre_trip_agent,
        ],
        before_agent_callback=_load_precreated_itinerary,
    )