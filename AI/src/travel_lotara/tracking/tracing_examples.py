"""
Opik Tracing Examples for Travel Lotara.

This module demonstrates various tracing patterns and best practices
for using Opik with Google ADK agents and tools.

Examples:
1. Basic Agent Tracing
2. Tool Function Tracing
3. Hybrid Tracing (Callbacks + Decorators)
4. Multi-Step Tool Tracing
5. Custom Metadata and Tags
6. Error Handling and Tracking
"""

from typing import Dict, Any, List
from google.adk.agents import LlmAgent, Agent
from src.travel_lotara.tracking import get_tracer, trace_tool, trace_async_tool
from src.travel_lotara.config import get_settings

settings = get_settings()


# ============================================================================
# Example 1: Basic Agent Tracing
# ============================================================================

def example_basic_agent_tracing():
    """
    Demonstrates basic agent instrumentation.
    
    This is the simplest way to add tracing to your agents.
    The tracer will automatically instrument all sub-agents and tools.
    """
    from google.adk.agents import Agent
    
    # Create your agent
    my_agent = Agent(
        model=settings.model,
        name="example_agent",
        description="An example agent",
        instruction="Answer questions helpfully"
    )
    
    # Get the global tracer and instrument the agent
    tracer = get_tracer()
    tracer.instrument_agent(my_agent)
    
    # That's it! All agent executions are now traced
    # result = my_agent.run("What's the weather?")
    
    print("✓ Example 1: Basic agent tracing setup complete")


# ============================================================================
# Example 2: Tool Function Tracing
# ============================================================================

@trace_tool(name="weather_lookup", tags=["weather", "external-api"])
def get_weather(city: str) -> Dict[str, Any]:
    """
    Example tool with tracing decorator.
    
    The @trace_tool decorator automatically creates a span for this function.
    When called from an instrumented agent, it will appear as a child span.
    """
    # Simulate weather lookup
    weather_data = {
        "city": city,
        "temperature": 25,
        "condition": "sunny",
        "humidity": 65
    }
    return weather_data


@trace_tool(name="user_preferences", tags=["context", "user"])
def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Example tool for fetching user preferences."""
    return {
        "user_id": user_id,
        "preferred_destinations": ["Paris", "Tokyo", "New York"],
        "budget_range": "medium",
        "travel_style": "adventure"
    }


def example_tool_tracing():
    """Demonstrates tool function tracing with decorators."""
    # These functions are already decorated, so they'll be traced automatically
    weather = get_weather("Paris")
    preferences = get_user_preferences("user_123")
    
    print("✓ Example 2: Tool tracing with decorators")
    print(f"  Weather: {weather}")
    print(f"  Preferences: {preferences}")


# ============================================================================
# Example 3: Hybrid Tracing (Callbacks + Decorators)
# ============================================================================

@trace_tool(name="location_validation", tags=["validation", "location"])
def validate_location(city: str) -> Dict[str, Any]:
    """Validate and normalize city names."""
    normalized_cities = {
        "nyc": "New York",
        "ny": "New York",
        "paris": "Paris",
        "tokyo": "Tokyo"
    }
    
    city_lower = city.lower().strip()
    validated_city = normalized_cities.get(city_lower, city.title())
    
    return {
        "original": city,
        "validated": validated_city,
        "is_valid": city_lower in normalized_cities
    }


@trace_tool(name="weather_data_processing", tags=["processing", "weather"])
def process_weather_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process raw weather data with additional computations."""
    processed = {
        "temperature_celsius": raw_data.get("temp_c", 0),
        "temperature_fahrenheit": raw_data.get("temp_c", 0) * 9/5 + 32,
        "conditions": raw_data.get("condition", "unknown"),
        "comfort_index": "comfortable" if 18 <= raw_data.get("temp_c", 0) <= 25 else "less comfortable"
    }
    return processed


@trace_tool(name="advanced_weather_lookup", tags=["weather", "multi-step"])
def get_advanced_weather(city: str) -> Dict[str, Any]:
    """
    Multi-step tool that combines multiple traced functions.
    
    This demonstrates hybrid tracing where:
    1. The main tool is traced with @trace_tool
    2. Internal steps are also traced with @trace_tool
    3. When used with an instrumented agent, all spans are properly nested
    """
    # Step 1: Validate location (traced)
    location_result = validate_location(city)
    
    if not location_result["is_valid"]:
        return {
            "status": "error",
            "error_message": f"Invalid location: {city}"
        }
    
    validated_city = location_result["validated"]
    
    # Step 2: Get raw weather data (simulated)
    raw_weather_data = {
        "New York": {"temp_c": 25, "condition": "sunny", "humidity": 65},
        "Paris": {"temp_c": 18, "condition": "cloudy", "humidity": 78},
        "Tokyo": {"temp_c": 22, "condition": "partly cloudy", "humidity": 70}
    }
    
    if validated_city not in raw_weather_data:
        return {
            "status": "error",
            "error_message": f"Weather data unavailable for {validated_city}"
        }
    
    raw_data = raw_weather_data[validated_city]
    
    # Step 3: Process the data (traced)
    processed_data = process_weather_data(raw_data)
    
    return {
        "status": "success",
        "city": validated_city,
        "report": f"Weather in {validated_city}: {processed_data['conditions']}, "
                 f"{processed_data['temperature_celsius']}°C "
                 f"({processed_data['temperature_fahrenheit']:.1f}°F). "
                 f"Comfort level: {processed_data['comfort_index']}.",
        "raw_humidity": raw_data["humidity"]
    }


def example_hybrid_tracing():
    """Demonstrates hybrid tracing with nested function calls."""
    result = get_advanced_weather("nyc")
    
    print("✓ Example 3: Hybrid tracing (callbacks + decorators)")
    print(f"  Result: {result}")


# ============================================================================
# Example 4: Agent with Custom Metadata
# ============================================================================

def example_agent_with_metadata():
    """
    Demonstrates instrumenting an agent with custom metadata and tags.
    
    Custom metadata helps you:
    - Filter traces in the Opik dashboard
    - Add business context to traces
    - Track versions, teams, or features
    """
    from google.adk.agents import Agent
    
    planning_agent = Agent(
        model=settings.model,
        name="planning_agent",
        description="Travel planning specialist",
        instruction="Create detailed travel itineraries"
    )
    
    tracer = get_tracer()
    
    # Instrument with custom metadata and tags
    tracer.instrument_agent(
        planning_agent,
        metadata={
            "team": "planning",
            "version": "2.0",
            "feature": "itinerary-generation",
            "model_type": "gemini"
        },
        tags=["planning", "itinerary", "production"]
    )
    
    print("✓ Example 4: Agent with custom metadata and tags")


# ============================================================================
# Example 5: Async Tool Tracing
# ============================================================================

@trace_async_tool(name="async_api_call", tags=["external", "async"])
async def fetch_external_data(url: str) -> Dict[str, Any]:
    """
    Example async tool with tracing.
    
    Use @trace_async_tool for async functions.
    """
    # Simulate async API call
    import asyncio
    await asyncio.sleep(0.1)
    
    return {
        "url": url,
        "status": "success",
        "data": {"example": "data"}
    }


async def example_async_tool_tracing():
    """Demonstrates async tool tracing."""
    result = await fetch_external_data("https://api.example.com/data")
    
    print("✓ Example 5: Async tool tracing")
    print(f"  Result: {result}")


# ============================================================================
# Example 6: Error Handling and Tracking
# ============================================================================

@trace_tool(name="risky_operation", tags=["error-handling"])
def risky_operation(value: int) -> Dict[str, Any]:
    """
    Example showing error tracking.
    
    Opik automatically captures exceptions and logs them to the trace.
    """
    if value < 0:
        raise ValueError(f"Value must be positive, got {value}")
    
    return {"result": value * 2}


def example_error_tracking():
    """Demonstrates error tracking in traces."""
    try:
        # This will succeed
        result1 = risky_operation(5)
        print(f"✓ Success: {result1}")
        
        # This will fail and be tracked
        result2 = risky_operation(-1)
    except ValueError as e:
        print(f"✓ Example 6: Error tracked in trace: {e}")


# ============================================================================
# Example 7: Creating Agent-Specific Tracers
# ============================================================================

def example_dedicated_agent_tracer():
    """
    Demonstrates creating dedicated tracers for specific agents.
    
    Use this when you want different agents to have separate
    trace configurations or when you need fine-grained control.
    """
    from google.adk.agents import Agent
    
    # Create multiple agents
    inspiration_agent = Agent(
        model=settings.model,
        name="inspiration_agent",
        description="Travel inspiration specialist"
    )
    
    planning_agent = Agent(
        model=settings.model,
        name="planning_agent",
        description="Itinerary planning specialist"
    )
    
    tracer = get_tracer()
    
    # Create dedicated tracer for inspiration agent
    inspiration_tracer = tracer.create_agent_tracer(
        "inspiration_agent",
        tags=["inspiration", "discovery"],
        metadata={"team": "inspiration", "priority": "high"}
    )
    
    # Create dedicated tracer for planning agent
    planning_tracer = tracer.create_agent_tracer(
        "planning_agent",
        tags=["planning", "itinerary"],
        metadata={"team": "planning", "priority": "critical"}
    )
    
    print("✓ Example 7: Created dedicated tracers for multiple agents")


# ============================================================================
# Running All Examples
# ============================================================================

def run_all_examples():
    """Run all tracing examples."""
    import asyncio
    
    print("\n" + "="*70)
    print("Opik Tracing Examples for Travel Lotara")
    print("="*70 + "\n")
    
    example_basic_agent_tracing()
    example_tool_tracing()
    example_hybrid_tracing()
    example_agent_with_metadata()
    
    # Run async example
    asyncio.run(example_async_tool_tracing())
    
    example_error_tracking()
    example_dedicated_agent_tracer()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")
    
    # Flush traces
    from src.travel_lotara.tracking import flush_traces
    flush_traces()


if __name__ == "__main__":
    run_all_examples()
