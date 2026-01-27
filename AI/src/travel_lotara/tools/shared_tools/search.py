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

"""Wrapper to Google Search Grounding with custom prompt."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search


from src.travel_lotara.config.settings import get_settings
settings = get_settings()
MODEL_ID = settings.model

## Constants for Search Agent
SEARCH_AGENT_NAME = "search_agent"
SEARCH_AGENT_DESCRIPTION = "An agent providing Google-search grounding capability"
SEARCH_AGENT_OUTPUT_KEY = "search_results"

_search_agent = Agent(
    model=MODEL_ID,
    name=SEARCH_AGENT_NAME,
    description=SEARCH_AGENT_DESCRIPTION,
    instruction="""
    Answer the user's question directly using google_search grounding tool; Provide a brief but concise response.
    Rather than a detail response, provide the immediate actionable item for a tourist or traveler, in a single sentence.
    Do not ask the user to check or look up information for themselves, that's your role; do your best to be informative.
    """,
    tools=[google_search],
)

google_search_grounding_tool = AgentTool(agent=_search_agent)