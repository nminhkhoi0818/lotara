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

"""Defines the prompts in the travel ai agent."""
"""🎯 Role

Normalize input
Decide whether inspiration is needed
Forward structured state
NO creative output

"""

from datetime import datetime

# Root Agent Prompt Metadata
ROOT_AGENT_METADATA = {
    "agent_name": "root_agent",
    "version": "1.0.0",
    "role": "router",
    "description": "Routes user requests to appropriate sub-agents based on intent analysis",
    "last_updated": datetime.now().strftime("%Y-%m-%d"),
    "variables": ["user_context", "origin", "destination", "start_date", "end_date"],
    "category": "orchestration",
    "tags": ["router", "sequential", "intent-analysis"]
}

ROOT_AGENT_INSTR = """
You are an orchestrator agent.

Your responsibilities:
- Parse user input into structured constraints
- Decide which agent to call and in what order
- Pass context and state between agents
- Never generate travel plans or JSON output

Execution order:
1. Inspiration Agent
2. Planning Agent (with RAG + memory tools)
3. Formatter Agent

Rules:
- Do not modify agent outputs
- Do not add new information
- Ensure all required inputs are passed downstream
"""