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
import time

# from flask import session
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types
from google.genai.errors import ServerError
from src.travel_lotara.tracking import get_tracer, flush_traces
from src.travel_lotara.core.input_parser import parse_backend_input, create_natural_language_query


async def run_agent(
    user_input: str,
    user_id: Optional[str] = None,
    backend_json: Optional[Dict[str, Any]] = None,
) -> tuple[str, Session]:
    """
    Run the Travel Lotara root agent and return final text output with session.
    
    Args:
        user_input: Natural language query
        user_id: Optional user ID for session tracking
        backend_json: Optional backend JSON with user preferences
        
    Returns:
        Tuple of (response_text, session)
    """
    from src.travel_lotara.agents import root_agent
    
    tracer = get_tracer()
    session_service = InMemorySessionService()
    
    # Debug: Print model being used
    from src.travel_lotara.config.settings import get_settings
    settings = get_settings()
    print(f"[DEBUG] Using model: {settings.model}")
    
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
        user_id=user_id if user_id else f"cli_{uuid.uuid4().hex[:8]}",
    )
    
    # Set default values for required context variables
    # Dates will be determined by agents based on user input
    session.state["origin"] = ""
    session.state["destination"] = ""
    session.state["total_days"] = "10"
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

    # Application-level retry wrapper (reduced since ADK has its own retry logic)
    # ADK now handles retries at the model level with 60s delay and 5 attempts
    max_retries = 1  # Reduced from 7 - ADK does the heavy lifting now
    base_delay = 30  # seconds - shorter since ADK already tried
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = base_delay * attempt
                print(f"[RETRY] Application-level retry - waiting {delay}s before attempt {attempt + 1}/{max_retries}...")
                print(f"[INFO] Note: Each attempt includes ADK's 5 internal retries with 60s delays")
                await asyncio.sleep(delay)
                print(f"[RETRY] Starting attempt {attempt + 1}/{max_retries}...")
            else:
                print("[INFO] Starting agent execution (ADK retry config: 5 attempts, 60s initial delay)...")
            
            # Reset text parts on retry
            final_text_parts = []
            
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
            
            # Combine all text parts into final response
            expected_output = final_text_parts[-1] if len(final_text_parts) > 0 else ""

            # Enforce final JSON output schema
            # Delete special token if present (```json ... ```,  <<JSON_OUTPUT>> etc)
            if expected_output.startswith("<<JSON_OUTPUT>>"):
                expected_output = expected_output.replace("<<JSON_OUTPUT>>", "").strip()
            if expected_output.startswith("```json"):
                expected_output = expected_output.replace("```json", "").replace("```", "").strip()

            # Print final output
            print("[INFO] Agent execution completed successfully")
            break  # Success - exit retry loop
            
        except Exception as e:
            # Check if it's a ServerError (including nested ones)
            error_str = str(e)
            is_429 = '429' in error_str or 'rate limit' in error_str.lower() or 'resource_exhausted' in error_str.lower()
            is_503 = '503' in error_str or 'overloaded' in error_str.lower()
            is_retryable = is_503 or is_429
            
            # Also check if it's a ServerError instance
            if isinstance(e, ServerError):
                is_retryable = hasattr(e, 'status_code') and e.status_code in [503, 429]
                is_429 = hasattr(e, 'status_code') and e.status_code == 429
            
            if is_retryable:
                if attempt < max_retries - 1:
                    error_type = "429 (QUOTA EXHAUSTED)" if is_429 else "503 (overloaded)"
                    print(f"\n[ERROR] {error_type} - All ADK retries exhausted")
                    print(f"[DEBUG] {error_str[:200]}..." if len(error_str) > 200 else f"[DEBUG] {error_str}")
                    print(f"[INFO] Application-level retry {attempt + 1}/{max_retries} - will retry after delay")
                    continue  # Retry
                else:
                    error_type = "rate limited" if is_429 else "overloaded"
                    print(f"\n[ERROR] Model still {error_type} after {max_retries} application attempts")
                    print(f"[ERROR] Total retries attempted: {max_retries} app-level × 5 ADK-level = {max_retries * 5}")
                    print(f"[ERROR] Final error: {error_str[:200]}..." if len(error_str) > 200 else f"[ERROR] {error_str}")
                    print("\n" + "="*80)
                    
                    if is_429:
                        print("🔴 CRITICAL: Google Gemini API QUOTA EXHAUSTED")
                        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        print("This is NOT a temporary rate limit - your quota is DEPLETED")
                        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                        print("📊 Likely causes:")
                        print("   • Daily request limit reached (1,500/day for gemini-1.5-flash)")
                        print("   • Tokens per minute exceeded (1M TPM)")
                        print("   • Too many requests in short time window\n")
                        print("✅ IMMEDIATE ACTIONS (priority order):\n")
                        print("   1. CHECK YOUR QUOTA:")
                        print("      → https://aistudio.google.com/app/apikey")
                        print("      → Look at RPM, RPD, and TPM usage\n")
                        print("   2. WAIT FOR QUOTA RESET:")
                        print("      → Daily limits reset at midnight UTC")
                        print("      → Minute limits reset after 60 seconds")
                        print("      → Recommended: Wait 10-15 minutes minimum\n")
                        print("   3. TRY ALTERNATIVE API KEY:")
                        print("      → Get new key: https://aistudio.google.com/")
                        print("      → Update GOOGLE_API_KEY in .env\n")
                        print("   4. SWITCH TO DIFFERENT MODEL:")
                        print("      → Edit .env: LOTARA_MODEL=gemini-1.5-pro")
                        print("      → Note: Different quotas per model\n")
                        print("   5. UPGRADE TO PAID TIER:")
                        print("      → https://ai.google.dev/pricing")
                        print("      → Get 10-100x higher limits\n")
                        print("⚠️  Current model: " + os.getenv('LOTARA_MODEL', 'gemini-1.5-flash'))
                        print("⚠️  DO NOT retry immediately - quota is exhausted!")
                    else:
                        print("[SOLUTION] The Google Gemini API is currently overloaded.")
                        print("\nImmediate actions:")
                        print("  1. WAIT: Try again in 5-10 minutes")
                        print("  2. CHECK STATUS: https://status.cloud.google.com/")
                        print("  3. SWITCH MODEL: Edit .env → LOTARA_MODEL=gemini-1.5-pro")
                    print("="*80 + "\n")
                    raise
            else:
                print(f"[ERROR] Non-retryable error: {e}")
                raise  # Re-raise non-retryable errors

    response_text = expected_output if expected_output else "No response generated."
    return response_text, session


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
        response, session = await run_agent(
            user_input=user_input or "",
            user_id=args.user_id,
            backend_json=backend_json,
        )
        
        print("\n" + "=" * 80, flush=True)
        print("[RESPONSE]", flush=True)
        print("=" * 80, flush=True)
        print(response, flush=True)
        print("=" * 80 + "\n", flush=True)

        # Save results to JSON files
        import os
        import sys
        OUTPUT_DIR = "output"
        STATE_DUMP_DIR = "state_dumps"
        
        print(f"[DEBUG] Creating directories...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(STATE_DUMP_DIR, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Save the agent's response (itinerary JSON)
        response_filename = f"itinerary_{timestamp}.json"
        response_path = os.path.join(OUTPUT_DIR, response_filename)
        
        print(f"[DEBUG] Saving agent response to: {response_path}", flush=True)
        try:
            # Try to parse response as JSON
            response_json = json.loads(response) if isinstance(response, str) else response
            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(response_json, f, indent=2, ensure_ascii=False)
            print(f"✓ Agent response saved to: {response_path}", flush=True)
        except json.JSONDecodeError:
            # If response is not valid JSON, save as text
            with open(response_path.replace('.json', '.txt'), "w", encoding="utf-8") as f:
                f.write(response)
            print(f"✓ Agent response (text) saved to: {response_path.replace('.json', '.txt')}", flush=True)
        except Exception as e:
            print(f"✗ Failed to save response: {e}", flush=True)
        
        # 2. Save the session state
        print(f"[DEBUG] Session: {session}, Has state: {hasattr(session, 'state') if session else False}", flush=True)
        
        if session and hasattr(session, 'state'):
            state_dump_path = os.path.join(
                STATE_DUMP_DIR,
                f"lotara_state_{timestamp}_{session.id}.json"
            )
            
            print(f"[DEBUG] Saving session state to: {state_dump_path}", flush=True)

            def json_safe_serializer(obj: Any) -> str:
                """Fallback serializer for non-JSON-serializable objects."""
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return str(obj)

            try:
                with open(state_dump_path, "w", encoding="utf-8") as f:
                    json.dump(
                        session.state,
                        f,
                        indent=2,
                        ensure_ascii=False,
                        default=json_safe_serializer,
                    )
                print(f"✓ Session state saved to: {state_dump_path}", flush=True)
            except Exception as e:
                print(f"✗ Failed to save state: {e}", flush=True)
                import traceback
                traceback.print_exc()
        else:
            print("[WARNING] Session or session.state not available", flush=True)
        
        # Summary
        print("\n" + "=" * 80, flush=True)
        print("[SAVE SUMMARY]", flush=True)
        print(f"✓ Response saved to: {OUTPUT_DIR}/", flush=True)
        print(f"✓ State saved to: {STATE_DUMP_DIR}/", flush=True)
        print("=" * 80 + "\n", flush=True)

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
