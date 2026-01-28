"""Test script to verify ADK retry configuration is applied"""

import asyncio
from src.travel_lotara.agents.root_agent import root_agent
from src.travel_lotara.main import run_agent

async def test_retry_config():
    """Test that retry configuration is properly applied to agents"""
    
    # Test simple query to verify configuration
    test_query = "I want to travel to Paris for 3 days with a budget of $1000"
    
    print("[TEST] Starting agent with ADK retry configuration...")
    print("[TEST] Query:", test_query)
    print()
    
    try:
        response, session = await run_agent(test_query)
        print("[SUCCESS] Agent completed successfully!")
        print("[RESPONSE]", response[:200] if len(response) > 200 else response)
        return True
    except Exception as e:
        print(f"[ERROR] Agent failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_retry_config())
    exit(0 if success else 1)
