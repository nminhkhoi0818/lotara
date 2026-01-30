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

"""The 'memorize' tool for several agents to affect session states."""

import json
import os
from datetime import datetime
from typing import Any, Dict

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext
from src.travel_lotara.tracking import trace_tool
from src.travel_lotara.agents.shared_libraries import (
    SYSTEM_TIME,
    ITIN_INITIALIZED,
    ITIN_KEY,
    ITIN_START_DATE,
    ITIN_END_DATE,
    ITIN_DATETIME,
    START_DATE,
    END_DATE,
)

SAMPLE_SCENARIO_PATH = os.getenv(
    "TRAVEL_LOTARA_SAMPLE_SCENARIO",
    "src/travel_lotara/agents/profiles/itinerary_empty_default.json",
)


@trace_tool(name="memorize_list", tags=["memory", "state", "list"])
def memorize_list(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    if key not in mem_dict:
        mem_dict[key] = []
    if value not in mem_dict[key]:
        mem_dict[key].append(value)
    return {"status": f'Stored "{key}": "{value}"'}


@trace_tool(name="memorize", tags=["memory", "state", "key-value"])
def memorize(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information, one key-value pair at a time.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    mem_dict[key] = value
    return {"status": f'Stored "{key}": "{value}"'}


def forget(key: str, value: str, tool_context: ToolContext):
    """
    Forget pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be removed.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    if tool_context.state[key] is None:
        tool_context.state[key] = []
    if value in tool_context.state[key]:
        tool_context.state[key].remove(value)
    return {"status": f'Removed "{key}": "{value}"'}


def _set_initial_states(source: Dict[str, Any], target: State | dict[str, Any]):
    """
    Setting the initial session state given a JSON object of states.
    """

    # System metadata
    if SYSTEM_TIME not in target:
        target[SYSTEM_TIME] = str(datetime.now())

    # Prevent double init
    if ITIN_INITIALIZED in target:
        return

    target[ITIN_INITIALIZED] = True

    # Merge base state
    target.update(source)

    itinerary = source.get(ITIN_KEY, {})
    if not itinerary:
        return

    if itinerary:
        target[ITIN_START_DATE] = itinerary[START_DATE]
        target[ITIN_END_DATE] = itinerary[END_DATE]
        target[ITIN_DATETIME] = itinerary[START_DATE]


def _load_precreated_itinerary(callback_context: CallbackContext):
    """
    Sets up the initial state.
    Set this as a callback as before_agent_call of the root_agent.
    This gets called before the system instruction is contructed.

    Args:
        callback_context: The callback context.
    """
    # Only load sample data if state is empty (not set by backend JSON)
    # Check if origin or destination are already populated
    if callback_context.state.get("origin") or callback_context.state.get("destination"):
        print(f"\n[INFO] State already populated from backend JSON, skipping sample data load\n")
        return
    
    data = {}
    with open(SAMPLE_SCENARIO_PATH, "r") as file:
        data = json.load(file)
        print(f"\nLoading Initial State from sample: {data}\n")

    _set_initial_states(data["state"], callback_context.state)