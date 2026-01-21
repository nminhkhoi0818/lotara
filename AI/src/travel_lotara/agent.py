# """
# Travel Lotara - Google ADK Multi-Agent System with Opik Tracing

# This module defines all the agents using Google ADK's Agent framework
# with full Opik observability for tracing, cost tracking, and debugging.

# Architecture:
# - LlmAgent for LLM-powered reasoning agents
# - Sub-agents for hierarchical delegation
# - Function tools for agent capabilities
# - OpikTracer for comprehensive observability
# - Guardrails for input/output validation
# """

# import os
# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm

# # Import Opik integration for ADK
# from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

# # Import tools
# from src.travel_lotara.tools.shared_tools.travel_tools import (
#     search_flights,
#     search_hotels,
#     search_activities,
#     get_destination_information,
#     check_visa_requirements,
#     calculate_trip_budget,
# )

# # Import guardrails
# from src.travel_lotara.guardrails.callbacks import (
#     input_guardrail_callback,
#     output_guardrail_callback,
# )

# # Import settings
# from src.travel_lotara.config.settings import get_settings

# # ============================================
# # CONFIGURATION
# # ============================================

# _settings = get_settings()

# # Model configuration (LiteLLM format for multi-provider support)
# DEFAULT_MODEL = _settings.model


# def get_llm():
#     """Get the configured LLM model."""
#     return LiteLlm(model=DEFAULT_MODEL)


# # ============================================
# # OPIK TRACER CONFIGURATION
# # ============================================

# opik_tracer = OpikTracer(
#     name="lotara-travel-assistant",
#     tags=_settings.opik_tags,
#     metadata={
#         "environment": _settings.environment,
#         "model": DEFAULT_MODEL,
#         "framework": "google-adk",
#         "version": "0.1.0",
#     },
#     project_name=_settings.opik_project,
# )


# # ============================================
# # FLIGHT AGENT
# # ============================================

# flight_agent = LlmAgent(
#     name="flight_agent",
#     model=get_llm(),
#     description="Specialist in finding and comparing flights. Searches for best flight deals and options.",
#     instruction="""You are a Flight Specialist Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Search for flights based on user requirements (origin, destination, dates)
# 2. Compare flight options by price, duration, and convenience
# 3. Consider user preferences like budget, airlines, layovers
# 4. Present the best options with clear reasoning

# When searching for flights:
# - Always confirm departure and return dates
# - Consider nearby airports for better deals
# - Explain trade-offs between price and convenience
# - Highlight any deals or savings

# Always use the search_flights tool to get real flight data. Present results clearly with:
# - Price
# - Airlines
# - Departure/arrival times
# - Number of stops
# - Total duration

# Be helpful, concise, and focus on finding the best value for the traveler.""",
#     tools=[search_flights],
# )


# # ============================================
# # HOTEL AGENT
# # ============================================

# hotel_agent = LlmAgent(
#     name="hotel_agent",
#     model=get_llm(),
#     description="Specialist in finding accommodations. Searches for hotels based on location, budget, and preferences.",
#     instruction="""You are a Hotel Specialist Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Search for hotels and accommodations based on user needs
# 2. Consider location, budget, amenities, and ratings
# 3. Match accommodations to traveler type (business, family, solo, etc.)
# 4. Present clear comparisons with pros and cons

# When searching for hotels:
# - Confirm check-in and check-out dates
# - Consider proximity to attractions and transport
# - Factor in amenities important to the user
# - Look for deals and special offers

# Always use the search_hotels tool to get real hotel data. Present results clearly with:
# - Price per night and total
# - Star rating and user reviews
# - Location description
# - Key amenities
# - Cancellation policy if available

# Be helpful and focus on finding comfortable stays within budget.""",
#     tools=[search_hotels],
# )


# # ============================================
# # ACTIVITY AGENT
# # ============================================

# activity_agent = LlmAgent(
#     name="activity_agent",
#     model=get_llm(),
#     description="Specialist in finding activities and attractions. Suggests things to do at destinations.",
#     instruction="""You are an Activity & Attractions Specialist Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Search for activities, tours, and attractions at destinations
# 2. Match activities to user interests and preferences
# 3. Create balanced itinerary suggestions
# 4. Consider logistics like timing, location, and booking requirements

# When searching for activities:
# - Ask about user interests if not specified
# - Mix popular attractions with hidden gems
# - Consider time needed for each activity
# - Group nearby activities together

# Always use the search_activities tool to get real activity data. Present results with:
# - Activity name and description
# - Price and duration
# - User ratings
# - Best time to visit
# - Booking requirements

# Be enthusiastic and help travelers discover amazing experiences!""",
#     tools=[search_activities],
# )


# # ============================================
# # VISA / REQUIREMENTS AGENT
# # ============================================

# visa_agent = LlmAgent(
#     name="visa_agent",
#     model=get_llm(),
#     description="Specialist in travel requirements. Checks visa needs, entry requirements, and travel documents.",
#     instruction="""You are a Travel Requirements Specialist Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Check visa requirements based on citizenship and destination
# 2. Provide information about entry requirements
# 3. Advise on required travel documents
# 4. Flag any travel advisories or restrictions

# When checking requirements:
# - Always confirm citizenship/passport country
# - Check for recent changes in requirements
# - Mention processing times for visas
# - Note any COVID or health requirements

# Always use the check_visa_requirements tool. Present results clearly:
# - Visa required: Yes/No
# - If yes: visa type, how to apply, processing time
# - Required documents
# - Any special notes or restrictions

# Always recommend verifying with official embassy sources for latest information.
# Be accurate and thorough - visa issues can ruin trips!""",
#     tools=[check_visa_requirements],
# )


# # ============================================
# # DESTINATION INFO AGENT
# # ============================================

# destination_agent = LlmAgent(
#     name="destination_agent",
#     model=get_llm(),
#     description="Expert on destinations. Provides general information, tips, and inspiration about places.",
#     instruction="""You are a Destination Expert Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Provide rich information about travel destinations
# 2. Share local tips, customs, and cultural insights
# 3. Offer travel inspiration and recommendations
# 4. Answer general questions about places

# When providing destination info:
# - Cover practical info: weather, currency, language, timezone
# - Share cultural tips and etiquette
# - Suggest best times to visit
# - Mention safety considerations

# Use the get_destination_information tool for data. Enhance it with:
# - Interesting facts and history
# - Local cuisine recommendations
# - Transportation tips
# - Best neighborhoods to explore

# Be engaging and make travelers excited about their destination!
# Share insider tips that make trips more memorable.""",
#     tools=[get_destination_information],
# )


# # ============================================
# # BUDGET / COST AGENT
# # ============================================

# budget_agent = LlmAgent(
#     name="budget_agent",
#     model=get_llm(),
#     description="Specialist in trip budgeting. Calculates costs and helps plan financially.",
#     instruction="""You are a Budget Planning Agent for Lotara Travel Assistant.

# Your responsibilities:
# 1. Calculate estimated trip costs
# 2. Create itemized budget breakdowns
# 3. Suggest cost-saving tips
# 4. Help users plan within their budget

# When calculating budgets:
# - Get all cost components (flights, hotels, activities, food)
# - Add reasonable buffers for unexpected expenses
# - Consider destination cost of living
# - Suggest budget alternatives if over limit

# Use the calculate_trip_budget tool for calculations. Present results with:
# - Itemized breakdown
# - Total estimated cost
# - Daily average spending
# - Money-saving suggestions

# Be practical and help travelers get the most value from their budget.
# Always include a small buffer for emergencies.""",
#     tools=[calculate_trip_budget],
# )


# # ============================================
# # ROOT AGENT (ORCHESTRATOR)
# # ============================================

# root_agent = LlmAgent(
#     name="lotara_travel_assistant",
#     model=get_llm(),
#     description="Lotara is a comprehensive AI travel planning assistant that helps users plan their perfect trips.",
#     instruction="""You are Lotara, an AI Travel Planning Assistant created by the Lotara team.

# Your personality:
# - Friendly, helpful, and enthusiastic about travel
# - Professional but conversational
# - Detail-oriented but not overwhelming
# - Proactive in suggesting useful information

# Your capabilities:
# - Plan complete trips from start to finish
# - Find flights, hotels, and activities
# - Check visa and travel requirements  
# - Calculate budgets and costs
# - Provide destination insights and tips

# How to help users:
# 1. First, understand their travel needs:
#    - Where do they want to go?
#    - When are they traveling?
#    - What's their budget?
#    - What are their interests?
#    - Who is traveling (solo, couple, family)?

# 2. Then coordinate with your specialist agents:
#    - flight_agent: For flight searches and bookings
#    - hotel_agent: For accommodation options
#    - activity_agent: For things to do
#    - visa_agent: For travel requirements
#    - destination_agent: For destination info and tips
#    - budget_agent: For cost calculations

# 3. Present comprehensive, well-organized travel plans

# For simple questions, answer directly.
# For complex planning, delegate to specialist agents.

# Always be helpful, accurate, and make travel planning enjoyable!
# Remember to double-check important details like dates and requirements.""",
#     sub_agents=[
#         flight_agent,
#         hotel_agent,
#         activity_agent,
#         visa_agent,
#         destination_agent,
#         budget_agent,
#     ],
#     # Apply guardrails for input/output validation
#     before_model_callback=input_guardrail_callback,
#     after_model_callback=output_guardrail_callback,
# )


# # ============================================
# # INSTRUMENT ALL AGENTS WITH OPIK TRACING
# # ============================================

# # This single call instruments the entire agent hierarchy
# # All agent calls, tool calls, and LLM interactions are traced
# track_adk_agent_recursive(root_agent, opik_tracer)


# # ============================================
# # HELPER FUNCTIONS
# # ============================================

# def flush_traces():
#     """Flush all pending traces to Opik. Call before script exit."""
#     opik_tracer.flush()


# def get_tracer() -> OpikTracer:
#     """Get the Opik tracer instance for custom tracing."""
#     return opik_tracer
