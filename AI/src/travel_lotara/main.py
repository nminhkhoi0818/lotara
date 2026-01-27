"""
Entry point for Travel Lotara with Opik Tracing and Backend JSON support.

Usage:
  # Natural language input:
  python -m travel_lotara.main --user-input "Plan a trip to Vietnam for 10 days"
  
  # Backend JSON input:
  python -m travel_lotara.main --json-input '{"duration":"medium","companions":"solo"...}'
"""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.travel_lotara.tracking import get_tracer, flush_traces
from src.travel_lotara.core.input_parser import parse_backend_input, create_natural_language_query


async def run_agent(
    user_input: str,
    user_id: Optional[str] = None,
    backend_json: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Run the Travel Lotara root agent and return final text output.
    
    Args:
        user_input: Natural language query
        user_id: Optional user ID for session tracking
        backend_json: Optional backend JSON with user preferences
    """
    from src.travel_lotara.agents import root_agent
    
    tracer = get_tracer()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="lotara_travel",
    )

    # Parse backend JSON if provided
    initial_state = {}
    if backend_json:
        initial_state = parse_backend_input(backend_json)
        user_input = create_natural_language_query(backend_json)
        print(f"[INFO] Parsed backend input:")
        print(f"   Duration: {backend_json.get('duration')} -> {initial_state['total_days']} days")
        print(f"   Style: {backend_json.get('travelStyle')} -> {initial_state['user_profile']['travel_style']}")
        print(f"   Budget: {backend_json.get('budget')} -> {initial_state['user_profile']['budget_range']}/day")
        print(f"\n[QUERY] Generated query: {user_input}\n")

    session = await session_service.create_session(
        app_name="lotara_travel",
        user_id=user_id or f"cli_{uuid.uuid4().hex[:8]}",
    )
    
    # Set default values for required context variables
    # Use defaults that won't break template substitution
    default_start = datetime.now() + timedelta(days=14)
    default_end = default_start + timedelta(days=10)
    
    session.state["origin"] = "Ho Chi Minh City, Vietnam"
    session.state["destination"] = "Vietnam"
    session.state["start_date"] = default_start.strftime("%Y-%m-%d")
    session.state["end_date"] = default_end.strftime("%Y-%m-%d")
    session.state["total_days"] = "10"
    session.state["itinerary_start_date"] = default_start.strftime("%Y-%m-%d")
    session.state["itinerary_end_date"] = default_end.strftime("%Y-%m-%d")
    session.state["average_budget_spend_per_day"] = "$50-100"
    session.state["user_profile"] = {}
    session.state["itinerary"] = {}
    
    # Override with backend JSON state if provided
    if initial_state:
        for key, value in initial_state.items():
            # Ensure total_days is always a string for template substitution
            if key == "total_days" and isinstance(value, int):
                session.state[key] = str(value)
            else:
                session.state[key] = value

    final_text_parts: list[str] = []

    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=types.Content(parts=[types.Part(text=user_input)]),
    ):
        if hasattr(event, "content") and event.content:
            parts = getattr(event.content, "parts", None)
            if parts:
                for part in parts:
                    if hasattr(part, "text") and part.text:
                        final_text_parts.append(part.text)

    return "\n".join(final_text_parts).strip() or "No response generated."


async def async_main(args: argparse.Namespace) -> None:
    if not args.user_input and not args.json_input:
        print("[ERROR] Provide --user-input or --json-input")
        return

    print("\n=== Lotara Travel Assistant ===")
    
    backend_json = None
    user_input = args.user_input
    
    if args.json_input:
        try:
            backend_json = json.loads(args.json_input)
            print(f"[INPUT] Backend JSON: {json.dumps(backend_json, indent=2)}\n")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return
    else:
        print(f"[QUERY] {args.user_input}\n")

    try:
        response = await run_agent(
            user_input=user_input or "",
            user_id=args.user_id,
            backend_json=backend_json,
        )
        print("[RESPONSE]\n")
        print(response)
    except Exception as exc:
        import traceback
        print(f"\n[ERROR] {exc}")
        traceback.print_exc()
    finally:
        flush_traces()


def main() -> None:
    parser = argparse.ArgumentParser(description="Lotara Travel AI")
    parser.add_argument("--user-input", type=str, default=None, help="Natural language query")
    parser.add_argument("--json-input", type=str, default=None, help="Backend JSON input")
    parser.add_argument("--user-id", type=str, default=None, help="User ID")
    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
