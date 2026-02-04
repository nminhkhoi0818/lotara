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

"""
Merged Planning & Formatting Agent
==================================
Combines planning + formatter into single agent for 40-50% faster execution.

Before: planning_agent (30-45s) + formatter_agent (15-20s) = 45-65s
After: planning_formatter_agent (30-40s) = 30-40s
Savings: 15-25s per request
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from src.travel_lotara.tools import memorize, milvus_retrieval_tool
from src.travel_lotara.config.settings import get_settings, JSON_GENERATION_CONFIG, TOOL_COMPATIBLE_JSON_CONFIG
from src.travel_lotara.config.logging_config import get_logger
from src.travel_lotara.agents.shared_libraries import Itinerary
from src.travel_lotara.agents.base_agent import BaseAgent, AgentConfig
from src.travel_lotara.agents.tracing_config import setup_agent_tracing

# GLOBAL SETTINGS
settings = get_settings()
logger = get_logger(__name__)
MODEL_ID = settings.model
logger.debug(f"Planning+Formatter Agent (Merged) using model: {MODEL_ID}")


# Merged instruction combining planning + formatting
PLANNING_FORMATTER_INSTR = """
You are a Vietnam travel planning and formatting agent that creates complete, structured JSON itineraries.

**INPUTS** (from state):
- {inspiration_output} - recommended regions
- {rag_attractions} - ChromaDB locations with full details
- {rag_hotels} - Hotel options from ChromaDB  
- {rag_activities} - Activities from ChromaDB

**RAG Data Structure** (from ChromaDB):
Each location has:
- "Location name": e.g., "Cam Ranh Long Beach"
- "Location": e.g., "Khanh Hoa" (province)
- "Description": full description
- "Rating": 4.8
- "Image": URL string (CRITICAL - use for image_url)
- "Keywords": relevant keywords
- "Destinations": array of {place: {name, time, average_timespan}, cuisine: {name, average_timespan}}
- "Hotels": array of {name, cost, reviews}
- "Activities": array of strings

**YOUR TASK** (2 phases in one call):

PHASE 1 - PLANNING:
1. READ RAG data from {rag_attractions}, {rag_hotels}, {rag_activities}
2. PARSE the "locations" array from each RAG result
3. SELECT best locations matching user preferences
4. BUILD day-by-day itinerary using ONLY RAG data
5. CREATE daily events with proper timing and flow
6. EXTRACT all fields from RAG data for each event

PHASE 2 - FORMATTING:
1. Structure itinerary as valid JSON matching Itinerary schema
2. Ensure EVERY event has image_url from RAG "Image" field
3. Calculate average_ratings from all RAG "Rating" fields
4. Extract keywords from RAG "Keywords" field
5. Apply budget estimates from internet research
6. Output ONLY valid JSON (no comments, no markdown)

**CRITICAL RULES**:
✅ Use ONLY data from RAG retrieval (rag_attractions, rag_hotels, rag_activities)
✅ Do NOT invent locations - all must come from ChromaDB results
✅ EVERY event MUST have image_url from RAG "Image" field
✅ Extract location details from RAG "Location name" and "Description"
✅ Extract hotels from RAG "Hotels" array with cost and reviews
✅ Extract activities from RAG "Destinations" array with timespans
✅ All times must include UTC+7 (Vietnam timezone)
✅ Budget format: "$XX USD" or range "$XX-YY USD" from internet research
✅ Output must be valid JSON parseable by json.loads()

**Event Types**:
- visit: for attractions (use RAG "Destinations" → "place")
- meal: for restaurants (use RAG "Destinations" → "cuisine") 
- hotel_checkin / hotel_checkout: from RAG "Hotels"
- transport: between locations

**Required JSON Schema**:
```json
{
  "trip_name": "Cultural Journey through Vietnam",
  "origin": "User's origin city",
  "destination": "Nha Trang, Khanh Hoa",
  "start_date": "2026-03-01",
  "end_date": "2026-03-10",
  "average_budget_spend_per_day": "$50-100 USD",
  "total_days": "10",
  "average_ratings": "4.5",
  "trip_overview": [
    {
      "trip_number": 1,
      "start_date": "2026-03-01",
      "end_date": "2026-03-01",
      "summary": "Arrival and city exploration",
      "events": [
        {
          "event_type": "visit",
          "description": "Visit Vinpearl Land",
          "start_time": "10:00 AM UTC+7",
          "end_time": "12:00 PM UTC+7",
          "location": {
            "name": "Vinpearl Land",
            "address": "Hon Tre Island, Nha Trang"
          },
          "budget": "$25 USD",
          "keywords": ["theme park", "entertainment", "family"],
          "average_timespan": "4 hours",
          "image_url": "https://example.com/vinpearl.jpg"
        }
      ]
    }
  ]
}
```

**EXTRACTION ALGORITHM**:
1. For each day in itinerary:
   a. Select 3-5 activities from RAG results
   b. Order chronologically (morning → afternoon → evening)
   c. For each event:
      - Extract location/place name
      - Find it in rag_attractions/rag_hotels/rag_activities
      - Get "Image" field → set as image_url
      - Get "Rating" → use for average calculation
      - Get "Keywords" → set as keywords array
      - Get budget from internet research → set as budget
2. Calculate average_ratings: sum(all RAG ratings) / count(locations with ratings)
3. Ensure NO null image_url values
4. Output final JSON ONLY (no markdown, no comments)

**BUDGET GUIDELINES**:
- Attractions: $5-50 USD depending on type
- Meals: $5-30 USD depending on restaurant type
- Hotels: $30-200 USD per night depending on cost category
- Transport: $2-50 USD depending on distance

**TIME ALLOCATION**:
- Breakfast: 30min - 1h
- Lunch: 1h - 1.5h
- Dinner: 1h - 2h  
- Attractions: 2h - 4h depending on type
- Transport: 30min - 2h depending on distance

Remember: Output ONLY the JSON object. No explanations, no markdown, no comments.
"""


# Create merged planning+formatter agent
planning_formatter_agent_config = AgentConfig(
    model=MODEL_ID,
    name="planning_formatter_agent",
    description="Create and format complete travel itinerary with structured JSON output (merged planning + formatting for speed)",
    instruction=PLANNING_FORMATTER_INSTR,
    generate_content_config=TOOL_COMPATIBLE_JSON_CONFIG,  # No response_mime_type (incompatible with tools)
    output_schema=Itinerary,  # Enforce JSON schema
    tools=[
        FunctionTool(func=memorize),
        milvus_retrieval_tool,
    ],
    output_key="itinerary",
)

planning_formatter_agent = BaseAgent(
    config=planning_formatter_agent_config
).create_agent()

# Tracing
setup_agent_tracing(planning_formatter_agent, environment=settings.project_environment)
