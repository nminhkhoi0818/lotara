import asyncio
from travel_lotara.core.parser import get_query_parser
from travel_lotara.tools.api_tools import APITools
from travel_lotara.agents.flight_agent.flight_agent import FlightAgent

async def simple_demo():
    print("🌍 Travel Lotara - Simple Demo\n")
    
    # Step 1: Parse user query
    print("Step 1: Parsing user request...")
    parser = get_query_parser()
    query = "Plan a 7-day trip to Tokyo for $3000. Love food and temples."
    parsed = await parser.parse(query)
    print(f"✅ Destination: {parsed.destination}")
    print(f"✅ Budget: ${parsed.budget_usd}")
    print(f"✅ Interests: {', '.join(parsed.interests)}\n")
    
    # Step 2: Search flights
    print("Step 2: Searching flights...")
    api_tools = APITools()
    flights = await api_tools.search_flights(
        origin="JFK",
        destination="NRT",
        departure_date="2026-03-15",
        budget=parsed.budget_usd
    )
    print(f"✅ Found {len(flights)} flight options")
    if flights:
        best = flights[0]
        print(f"   Best: {best['airline']} - ${best['price']}\n")
    
    # Step 3: Run Flight Agent
    print("Step 3: Running Flight Agent...")
    flight_agent = FlightAgent(api_tools)
    result = await flight_agent.run({
        "origin": "JFK",
        "destination": "NRT",
        "dates": {"departure": "2026-03-15"},
        "budget": parsed.budget_usd
    })
    print(f"✅ Agent confidence: {result.confidence:.1%}")
    print(f"   Recommendation: {result.result['recommendation']}\n")
    
    print("🎉 Demo complete!")

if __name__ == "__main__":
    asyncio.run(simple_demo())

    # uv run AI/tests/test_simple.py

    # Expected Output:
        #     🌍 Travel Lotara - Simple Demo

        # Step 1: Parsing user request...
        # ✅ Destination: Tokyo
        # ✅ Budget: $3000
        # ✅ Interests: food, temples

        # Step 2: Searching flights...
        # ✅ Found 5 flight options
        #    Best: JAL - $947

        # Step 3: Running Flight Agent...
        # ✅ Agent confidence: 92.0%
        #    Recommendation: JAL JFK→NRT nonstop

        # 🎉 Demo complete!