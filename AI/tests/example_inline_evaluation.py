"""
Example: Inline Evaluation with Comet Tracing

This example demonstrates how inline evaluation works with your Travel Lotara agent.
Each request is automatically evaluated and results appear in Comet's tracing UI.

Setup:
1. Set environment variables:
   - OPIK_API_KEY=your-opik-key
   - GOOGLE_API_KEY=your-gemini-key (for LLM-as-judge)
   
2. Enable inline evaluation (enabled by default):
   - ENABLE_INLINE_EVALUATION=true

3. Run this example:
   python tests/example_inline_evaluation.py

4. View results in Comet UI:
   https://www.comet.com/{workspace}/{project}/traces

What you'll see in Comet UI:
├── travel_lotara_root_agent (main trace)
│   ├── inspiration_agent
│   ├── rag_retrieval_parallel_agent
│   ├── planning_formatter_agent
│   └── inline_evaluation ⭐ (NEW - evaluation metrics)
│       ├── hallucination (score + reasoning)
│       ├── relevance (score + reasoning)
│       ├── safety (score + reasoning)
│       └── quality (score + reasoning)
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.travel_lotara.agents.root_agent import get_root_agent
from src.travel_lotara.core.eval.inline_evaluation import get_inline_evaluator


def check_setup():
    """Check if environment is configured correctly."""
    required = {
        "OPIK_API_KEY": "Get from https://www.comet.com/signup",
        "GOOGLE_API_KEY": "Get from https://makersuite.google.com/app/apikey",
    }
    
    missing = []
    for key, instruction in required.items():
        if not os.getenv(key):
            missing.append(f"  ❌ {key}: {instruction}")
    
    if missing:
        print("\n⚠️  Missing environment variables:")
        print("\n".join(missing))
        return False
    
    print("✅ Environment configured!")
    return True


def example_basic_usage():
    """Example 1: Standard agent usage (evaluation happens automatically)."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Standard Agent Usage with Automatic Evaluation")
    print("="*80 + "\n")
    
    # Get agent
    agent = get_root_agent()
    
    # Create a test request
    user_request = "Plan a romantic 3-day getaway to Santorini for my anniversary, budget $2500"
    
    print(f"User Request: {user_request}\n")
    print("Processing... (this will take 30-60 seconds)\n")
    
    # Process request - evaluation happens automatically in after_agent_callback!
    try:
        # Note: Adjust this based on your actual agent API
        # This is a placeholder - check your root_agent.py for the actual method
        result = agent.run(user_request)
        
        print("✅ Agent completed!")
        print(f"\nResult preview:")
        print(str(result)[:500] + "...")
        
        print("\n" + "="*80)
        print("🎯 Evaluation Results (logged to Comet automatically)")
        print("="*80)
        print("\nCheck Comet UI to see:")
        print("  • Hallucination score")
        print("  • Relevance score")
        print("  • Safety score")
        print("  • Travel quality score")
        print("  • Overall score\n")
        
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        import traceback
        traceback.print_exc()


def example_manual_evaluation():
    """Example 2: Manual evaluation of existing output."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Manual Evaluation of Agent Output")
    print("="*80 + "\n")
    
    from src.travel_lotara.core.eval.inline_evaluation import evaluate_agent_output
    
    # Simulate an agent response
    query = "What's the best area to stay in Barcelona?"
    output = """
Based on your interests, I recommend staying in the Gothic Quarter (Barri Gòtic).

**Why Gothic Quarter:**
- Central location - walk to major attractions
- Medieval architecture and charming narrow streets
- Great mix of restaurants, bars, and shops
- Safe and well-lit at night
- Near Las Ramblas and the waterfront

**Recommended Hotels:**
1. Hotel Neri (luxury) - €200-300/night
2. Catalonia Portal de l'Angel (mid-range) - €100-150/night
3. Barcelona Urbany Hostel (budget) - €25-40/night

**Alternative:** El Born neighborhood - slightly quieter, great food scene, similar charm.

All recommendations are based on high traveler ratings and authentic local experiences.
    """
    
    context = [
        "Gothic Quarter is Barcelona's historic center with medieval architecture.",
        "El Born is known for upscale boutiques and trendy restaurants.",
        "Las Ramblas is a famous tree-lined pedestrian street in central Barcelona.",
    ]
    
    print("Evaluating agent output...")
    
    result = evaluate_agent_output(
        user_query=query,
        agent_output=output,
        context=context,
        user_preferences={"interests": ["history", "food"], "budget": "mid-range"},
    )
    
    print("\n✅ Evaluation Complete!\n")
    print(f"Overall Score: {result.get('overall_score', 0):.2f} / 1.0\n")
    print("Dimension Scores:")
    
    for dim, scores in result.get("dimensions", {}).items():
        if "score" in scores:
            score = scores["score"]
            emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            print(f"  {emoji} {dim.capitalize():15s}: {score:.2f}")
    
    print("\n" + "="*80 + "\n")


def example_custom_evaluator():
    """Example 3: Create custom evaluator with specific dimensions."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Custom Evaluator Configuration")
    print("="*80 + "\n")
    
    from src.travel_lotara.core.eval.inline_evaluation import InlineEvaluator
    
    # Create evaluator with only specific dimensions
    evaluator = InlineEvaluator(
        model="gemini/gemini-2.5-flash",  # Fast & free
        enabled=True,
        dimensions=["hallucination", "relevance"]  # Only these two
    )
    
    query = "Is it safe to drink tap water in Tokyo?"
    output = "Yes, tap water in Tokyo is safe to drink. Japan has one of the best water systems in the world."
    context = ["Tokyo's tap water meets the highest international standards and is regularly tested."]
    
    print(f"Query: {query}")
    print(f"\nEvaluating with custom dimensions: {evaluator.dimensions}\n")
    
    result = evaluator.evaluate_response(
        user_query=query,
        agent_output=output,
        context=context,
    )
    
    print("✅ Evaluation Complete!\n")
    print(f"Model: {result.get('model')}")
    print(f"Overall Score: {result.get('overall_score', 0):.2f}\n")
    
    for dim, scores in result.get("dimensions", {}).items():
        print(f"{dim}:")
        print(f"  Score: {scores.get('score', 0):.2f}")
        print(f"  Reason: {scores.get('reason', 'N/A')[:100]}...")
        print()
    
    print("="*80 + "\n")


def example_check_evaluator_status():
    """Example 4: Check if inline evaluation is enabled."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Check Inline Evaluator Status")
    print("="*80 + "\n")
    
    evaluator = get_inline_evaluator()
    
    print(f"Enabled: {evaluator.enabled}")
    print(f"Model: {evaluator.model}")
    print(f"Dimensions: {', '.join(evaluator.dimensions)}")
    
    if evaluator.enabled:
        print("\n✅ Inline evaluation is ACTIVE")
        print("   → All agent requests will be evaluated automatically")
        print("   → Results logged to Comet traces")
    else:
        print("\n⚠️  Inline evaluation is DISABLED")
        print("   → Set ENABLE_INLINE_EVALUATION=true to enable")
    
    print("\n" + "="*80 + "\n")


def main():
    """Run all examples."""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  Inline Evaluation Examples".center(78) + "█")
    print("█" + "  Automatic LLM-as-Judge with Comet Tracing".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup incomplete - configure environment variables first!")
        return
    
    # Run examples
    try:
        example_check_evaluator_status()
        
        example_manual_evaluation()
        
        example_custom_evaluator()
        
        # Uncomment to test with real agent (takes 30-60s)
        # example_basic_usage()
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "  ✅ All examples completed!".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█" + "  📊 View traces at: https://www.comet.com".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
