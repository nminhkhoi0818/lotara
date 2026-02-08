"""
Simple Manual Evaluation Script

Since auto-getting trace IDs from callbacks has limitations,
this script provides a simple way to manually evaluate traces.

Usage:
    1. Run your agent and note the trace_id from Opik logs
    2. Run this script with that trace_id

Example:
    python tests/manual_eval.py --trace-id 019c3458-9337-7a19-bc17-9ec4fd2d84ce
"""

import argparse
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.travel_lotara.core.eval.feedback_evaluator import get_feedback_evaluator


def main():
    parser = argparse.ArgumentParser(description="Manually evaluate an Opik trace")
    parser.add_argument("--trace-id", required=True, help="Opik trace ID to evaluate")
    parser.add_argument("--query", default="Plan a trip", help="Original user query")
    parser.add_argument("--output", default="Sample itinerary output", help="Agent output (or path to JSON file)")
    parser.add_argument("--context", nargs="*", help="Context chunks")
    parser.add_argument("--model", default="gemini/gemini-2.5-flash", help="Judge model")
    
    args = parser.parse_args()
    
    # Check environment
    if not os.getenv("OPIK_API_KEY"):
        print("❌ OPIK_API_KEY not set!")
        return 1
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        return 1
    
    # Load output from file if it's a path
    agent_output = args.output
    if os.path.exists(args.output):
        with open(args.output) as f:
            agent_output = f.read()
    
    print("=" * 80)
    print(f"Evaluating Trace: {args.trace_id}")
    print("=" * 80)
    print(f"Query: {args.query}")
    print(f"Model: {args.model}")
    print()
    
    # Evaluate
    evaluator = get_feedback_evaluator(model=args.model)
    result = evaluator.evaluate_and_score_trace(
        trace_id=args.trace_id,
        user_query=args.query,
        agent_output=agent_output,
        context=args.context or [],
    )
    
    print("📊 Evaluation Results:")
    print(f"   Overall Score: {result.get('overall_score', 0):.2f}")
    print()
    
    if "scores" in result:
        for dim, data in result["scores"].items():
            if "value" in data:
                print(f"   {dim.capitalize()}: {data['value']:.2f}")
    
    print()
    print("✅ Scores added to trace!")
    print(f"   View at: https://www.comet.com/<workspace>/<project>/traces/{args.trace_id}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
