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
"""

from __future__ import annotations

import argparse
import asyncio
import os


async def _run_adk_agent(user_input: str) -> str:
    """Run using Google ADK runner with Opik tracing."""
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        # Import agent (this also sets up Opik tracing)
        from travel_lotara.agent import root_agent, flush_traces
        
        session_service = InMemorySessionService()
        
        runner = Runner(
            agent=root_agent,
            session_service=session_service,
            app_name="lotara_travel",
        )
        
        session = await session_service.create_session(
            app_name="lotara_travel",
            user_id="cli_user",
        )
        
        # runner.run_async() returns an async generator
        final_response = None
        async for event in runner.run_async(
            session_id=session.id,
            user_id="cli_user",
            new_message=types.Content(
                parts=[types.Part(text=user_input)]
            ),
        ):
            # Collect the final response
            if hasattr(event, 'content') and event.content:
                final_response = event.content
        
        # Flush traces before returning
        flush_traces()
        
        # Extract text from response
        if final_response:
            if hasattr(final_response, 'parts'):
                return " ".join(
                    part.text for part in final_response.parts 
                    if hasattr(part, 'text')
                )
            return str(final_response)
        
        return "No response generated"
        
    except ImportError as e:
        return f"ADK not properly installed: {e}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error running agent: {e}"


async def _run(args: argparse.Namespace) -> None:
    """Main async runner."""
    if not args.user_input:
        print("Please provide --user-input")
        return
    
    print(f"\n🌴 Lotara Travel Assistant (with Opik Tracing)")
    print(f"📝 Query: {args.user_input}\n")
    
    result = await _run_adk_agent(args.user_input)
    print(f"🤖 Response:\n{result}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Travel Lotara - AI Travel Assistant")
    parser.add_argument(
        "--mode", 
        choices=["reactive", "proactive"], 
        default="reactive",
        help="Planning mode (default: reactive)"
    )
    parser.add_argument(
        "--budget-usd", 
        type=float, 
        default=1000.0,
        help="Budget in USD (default: 1000)"
    )
    parser.add_argument(
        "--user-id", 
        type=str, 
        default=None,
        help="User ID for session tracking"
    )
    parser.add_argument(
        "--user-input", 
        type=str, 
        default=None,
        help="User query/request"
    )
    args = parser.parse_args()

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()


