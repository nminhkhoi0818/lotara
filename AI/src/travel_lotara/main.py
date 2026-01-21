"""
Entry point for Travel Lotara with Opik Tracing.

For ADK usage:
  adk run travel_lotara.agent
  adk web travel_lotara.agent

For direct Python usage:
  python -m travel_lotara.main --user-input "Plan a trip to Tokyo"

Environment Variables:
  GOOGLE_API_KEY or GEMINI_API_KEY - For Gemini models
  OPENAI_API_KEY - For OpenAI models
  OPIK_API_KEY - For Opik tracing (optional, uses Comet cloud)
  OPIK_PROJECT_NAME - Opik project name (default: lotara-travel)
  LOTARA_MODEL - Model to use (default: gemini/gemini-2.0-flash)

Entry point for Travel Lotara (Google ADK).

Usage:
  adk run travel_lotara.main
  adk web travel_lotara.main

CLI:
  python -m travel_lotara.main --user-input "Plan a trip to Tokyo"

Env:
  LOTARA_MODEL
  GOOGLE_API_KEY / GEMINI_API_KEY
"""

from __future__ import annotations

import argparse
import asyncio
import uuid
from typing import Optional

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def run_agent(
    user_input: str,
    user_id: Optional[str] = None,
) -> str:
    """
    Run the Travel Lotara root agent and return final text output.
    """

    from src.travel_lotara.agents import root_agent  # lazy import (important)

    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="lotara_travel",
    )

    session = await session_service.create_session(
        app_name="lotara_travel",
        user_id=user_id or f"cli_{uuid.uuid4().hex[:8]}",
    )

    final_text_parts: list[str] = []

    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=types.Content(
            parts=[types.Part(text=user_input)]
        ),
    ):
        # ADK events may contain partial or final model outputs
        if hasattr(event, "content") and event.content:
            for part in getattr(event.content, "parts", []):
                if hasattr(part, "text"):
                    final_text_parts.append(part.text)

    return "\n".join(final_text_parts).strip() or "No response generated."


async def async_main(args: argparse.Namespace) -> None:
    if not args.user_input:
        print("❌ Please provide --user-input")
        return

    print("\n🌴 Lotara Travel Assistant")
    print(f"📝 Query: {args.user_input}\n")

    try:
        response = await run_agent(
            user_input=args.user_input,
            user_id=args.user_id,
        )
        print("🤖 Response:\n")
        print(response)

    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"\n❌ Error: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lotara Travel AI (Google ADK)"
    )
    parser.add_argument(
        "--user-input",
        type=str,
        required=True,
        help="User query/request",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=None,
        help="Optional user ID for session tracking",
    )

    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()


    # run this with:
    # uv run src/travel_lotara/main.py --user-input "Plan a trip to from Tokyo to Ho Chi Minh City including flights, hotels, and activities within a budget of $1500"


