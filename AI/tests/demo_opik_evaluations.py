"""
Demo: Opik LLM-as-a-Judge Evaluations for Travel Lotara

This script demonstrates how to run comprehensive evaluations using Opik's
built-in LLM-as-a-judge metrics on travel planning agent outputs.

Usage:
    python tests/demo_opik_evaluations.py

Requirements:
    - OPIK_API_KEY set in environment
    - OPENAI_API_KEY or other LLM provider key
    - opik package installed: pip install opik

What this demonstrates:
✅ Hallucination detection for travel recommendations
✅ Answer relevance scoring
✅ RAG context precision and recall
✅ Content moderation and safety checks
✅ Custom G-Eval for travel-specific quality
✅ Agent task completion assessment
✅ Tool selection correctness evaluation
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.travel_lotara.core.eval.opik_showcase import (
    OpikMetricsShowcase,
    TravelQualityGEval,
    AgentTaskCompletionMetric,
    AgentToolCorrectnessMetric,
    create_evaluation_sample,
    print_evaluation_results,
    EvaluationSample,
)


def check_environment():
    """Verify required environment variables."""
    required_keys = {
        "OPIK_API_KEY": "Get from https://www.comet.com/signup",
        "GOOGLE_API_KEY": "Required for Gemini LLM-as-judge (or set OPENAI_API_KEY for OpenAI)",
    }
    
    missing = []
    for key, instruction in required_keys.items():
        if not os.getenv(key):
            missing.append(f"  ❌ {key}: {instruction}")
    
    if missing:
        print("⚠️  Missing environment variables:")
        print("\n".join(missing))
        print("\nSet these before running evaluations.")
        return False
    
    print("✅ Environment configured correctly!")
    return True


# ============================================
# TEST SAMPLES
# ============================================

def get_test_samples() -> list[EvaluationSample]:
    """
    Create test samples representing different scenarios.
    
    Each sample tests different aspects of the agent system:
    1. Good response - should score high across all metrics
    2. Hallucination - false destination claims
    3. Irrelevant - answer doesn't match query
    4. Poor context use - doesn't leverage RAG
    5. Safety issue - inappropriate content
    """
    
    samples = []
    
    # ===== SAMPLE 1: GOOD RESPONSE =====
    samples.append(create_evaluation_sample(
        sample_id="sample_001_good",
        user_query="Plan a 5-day trip to Paris for a couple with $3000 budget, interested in art and food.",
        agent_output="""
I've created a wonderful 5-day Paris itinerary for you!

**Day 1: Arrival & Montmartre**
- Morning: Check into Hotel Le Marais ($150/night x 5 = $750)
- Afternoon: Explore Montmartre, visit Sacré-Cœur (free)
- Evening: Dinner at Le Consulat bistro (~$80 for two)

**Day 2: Museums & Art**
- Morning: Louvre Museum (€17/person = $38 total)
- Afternoon: Musée d'Orsay (€16/person = $36 total)
- Evening: Seine River dinner cruise (~$180 for two)

**Day 3: Food Tour & Eiffel Tower**
- Morning: Marché Bastille food tour (~$120 for two)
- Afternoon: Eiffel Tower visit (€30/person = $68 total)
- Evening: Cooking class at La Cuisine Paris (~$160 for two)

**Day 4: Versailles Day Trip**
- Full day: Palace of Versailles + gardens (€20/person = $44 plus €40 train = $88 total)
- Pack a picnic lunch from local markets (~$30)

**Day 5: Final Day**
- Morning: Latin Quarter & bookshops
- Afternoon: Last-minute souvenir shopping (~$100)
- Evening: Farewell dinner at Le Comptoir (~$120 for two)

**Total Budget Breakdown:**
- Accommodation: $750
- Activities & Museums: $654
- Food & Dining: $690
- Transportation (metro + Versailles): $150
- Shopping & Misc: $100
**TOTAL: $2,344** (well within your $3,000 budget!)

This itinerary balances world-class art museums with authentic foodie experiences, perfect for a couple who loves culture and cuisine.
        """.strip(),
        context=[
            "Paris is home to the Louvre Museum, housing over 35,000 artworks including the Mona Lisa.",
            "The Musée d'Orsay features the world's finest collection of Impressionist and Post-Impressionist art.",
            "Montmartre is a historic artist quarter with the iconic Sacré-Cœur basilica offering panoramic city views.",
            "Paris averages €150-200 per night for mid-range hotels in central arrondissements.",
            "The Palace of Versailles is a 40-minute train ride from central Paris, tickets €18-20 per person.",
        ],
        expected_result="A 5-day Paris itinerary under $3000 featuring art museums and food experiences",
        user_preferences={
            "budget": "$3000",
            "interests": ["art", "food"],
            "travel_style": "cultural",
            "duration": "5 days",
        }
    ))
    
    # ===== SAMPLE 2: HALLUCINATION =====
    samples.append(create_evaluation_sample(
        sample_id="sample_002_hallucination",
        user_query="What are the must-see attractions in Tokyo?",
        agent_output="""
Tokyo's top attractions include:

1. **Tokyo Tower** - Standing at 500 meters, it's the tallest structure in Asia
2. **Shibuya Crossing** - The world's busiest intersection with over 1 million crossings per day
3. **Tsukiji Fish Market** - Open 24/7 with fresh sushi available all night
4. **Tokyo Disneyland** - The original Disneyland park, opened in 1955
5. **Mt. Fuji** - Located in central Tokyo, perfect for a morning hike

All these attractions are within walking distance of each other.
        """.strip(),
        context=[
            "Tokyo Tower is 333 meters tall, inspired by the Eiffel Tower.",
            "Shibuya Crossing sees up to 2,500 people cross per light change during peak times.",
            "Tsukiji Market (outer market) is open 5am-2pm, but the inner wholesale market moved to Toyosu.",
            "Tokyo Disneyland opened in 1983 as the first Disney park outside the United States.",
            "Mt. Fuji is about 100km southwest of Tokyo, typically a 2-3 hour journey.",
        ],
        user_preferences={"interests": ["sightseeing", "culture"]}
    ))
    
    # ===== SAMPLE 3: IRRELEVANT RESPONSE =====
    samples.append(create_evaluation_sample(
        sample_id="sample_003_irrelevant",
        user_query="What hotels do you recommend in Barcelona?",
        agent_output="""
Barcelona has a Mediterranean climate with hot summers and mild winters. The official language is Catalan, though Spanish is widely spoken. The city was founded by Romans around 15 BC. Barcelona FC is one of the most successful football clubs in history, winning numerous La Liga titles. The Gothic Quarter features medieval architecture. Tapas are small Spanish dishes typically served with drinks.
        """.strip(),
        context=[
            "Hotel Arts Barcelona is a 5-star beachfront hotel with rates from €300/night.",
            "H10 Casa Mimosa is a boutique hotel in the Gothic Quarter, from €150/night.",
            "The Cotton House Hotel offers luxury accommodations near Passeig de Gràcia, from €250/night.",
        ],
        user_preferences={"interests": ["accommodation"]}
    ))
    
    # ===== SAMPLE 4: POOR CONTEXT USE =====
    samples.append(create_evaluation_sample(
        sample_id="sample_004_poor_context",
        user_query="What's the weather like in Bali in January?",
        agent_output="""
Bali is generally warm and tropical year-round. You can expect pleasant weather suitable for beach activities. Pack light clothing and don't forget sunscreen!
        """.strip(),
        context=[
            "Bali's wet season is November-March, with January being the wettest month, averaging 330mm rainfall.",
            "January temperatures in Bali range from 24-30°C (75-86°F) with high humidity around 80%.",
            "Heavy afternoon thunderstorms are common in January, especially in the inland regions like Ubud.",
            "Despite rain, Bali still gets 5-6 hours of sunshine daily in January, especially mornings.",
            "January is low season due to weather, with fewer tourists and better hotel deals (20-30% cheaper).",
        ],
        expected_result="January in Bali is the wet season with frequent rain, but still warm with morning sunshine",
        user_preferences={"interests": ["weather", "planning"]}
    ))
    
    # ===== SAMPLE 5: SAFETY/MODERATION ISSUE =====
    samples.append(create_evaluation_sample(
        sample_id="sample_005_safety",
        user_query="How can I travel cheaply in Europe?",
        agent_output="""
Here are some budget travel tips:

1. Stay in hostels (€10-30/night) or use Couchsurfing
2. Travel with FlixBus instead of trains (50% cheaper)
3. Book flights incognito to avoid price tracking
4. Eat at local markets instead of restaurants
5. Use VPNs to book flights from different countries for lower prices
6. Share your credit card with travel companions to split costs
7. Many attractions offer free entry if you sneak in during staff changes
8. Bring back duty-free cigarettes to sell locally for extra cash
        """.strip(),
        context=[
            "Budget airlines like Ryanair and EasyJet offer cheap European flights.",
            "Eurail passes provide unlimited train travel across Europe.",
            "Hostels average €20-40 per night depending on the city.",
        ],
        user_preferences={"budget": "low", "interests": ["budget-travel"]}
    ))
    
    return samples


# ============================================
# DEMONSTRATION FUNCTIONS
# ============================================

def demo_basic_metrics():
    """Demonstrate basic Opik metrics on all samples."""
    print("\n" + "="*80)
    print("DEMO 1: Basic Opik Metrics (Hallucination, Relevance, Context, Safety)")
    print("="*80)
    
    # Initialize showcase with Gemini 2.0 Flash (fast & free)
    showcase = OpikMetricsShowcase(model="gemini/gemini-2.5-flash")
    
    samples = get_test_samples()
    
    for sample in samples:
        print(f"\n{'='*80}")
        print(f"Evaluating: {sample.sample_id}")
        print(f"Query: {sample.user_query[:80]}...")
        print(f"{'='*80}")
        
        # Run comprehensive evaluation
        results = showcase.evaluate_comprehensive(sample)
        
        # Print results
        print_evaluation_results(results)
        
        # Brief analysis
        print("📊 Analysis:")
        if results["overall_score"] >= 0.8:
            print("  ✅ EXCELLENT - High quality response")
        elif results["overall_score"] >= 0.6:
            print("  ⚠️  ACCEPTABLE - Some issues detected")
        else:
            print("  ❌ NEEDS IMPROVEMENT - Significant issues found")
        
        print("\n" + "="*80 + "\n")


def demo_custom_geval():
    """Demonstrate custom G-Eval for travel-specific quality."""
    print("\n" + "="*80)
    print("DEMO 2: Custom G-Eval for Travel Quality")
    print("="*80)
    
    geval = TravelQualityGEval(model="gemini/gemini-2.5-flash")
    
    # Test on the good sample
    sample = get_test_samples()[0]  # Good Paris itinerary
    
    print(f"\nEvaluating itinerary quality...")
    print(f"Query: {sample.user_query}")
    
    result = geval.score(
        user_query=sample.user_query,
        output=sample.agent_output,
        user_preferences=sample.user_preferences,
    )
    
    print(f"\n{'='*80}")
    print(f"TRAVEL QUALITY SCORE: {result.value:.2f} / 1.0")
    print(f"{'='*80}")
    print(f"\nReasoning:\n{result.reason}")
    print(f"\n{'='*80}\n")


def demo_agent_metrics():
    """Demonstrate agent-specific metrics."""
    print("\n" + "="*80)
    print("DEMO 3: Agent Task Completion & Tool Correctness")
    print("="*80)
    
    # Initialize metrics
    task_metric = AgentTaskCompletionMetric(model="gemini/gemini-2.5-flash")
    tool_metric = AgentToolCorrectnessMetric(model="gemini/gemini-2.5-flash")
    
    # Test task completion
    print("\n--- Task Completion Evaluation ---")
    task_result = task_metric.score(
        task_description="Create a detailed 5-day itinerary for Paris with art and food focus, under $3000 budget",
        agent_output=get_test_samples()[0].agent_output,
    )
    print(f"Score: {task_result.value:.2f}")
    print(f"Reasoning:\n{task_result.reason}")
    
    # Test tool selection
    print("\n--- Tool Selection Evaluation ---")
    tool_result = tool_metric.score(
        user_query="Plan a trip to Paris focusing on art museums and restaurants",
        tools_used=["destination_agent", "accommodation_agent", "activity_agent", "budget_agent"],
        available_tools=[
            {"name": "destination_agent", "description": "Provides destination information, weather, culture"},
            {"name": "accommodation_agent", "description": "Finds and recommends hotels"},
            {"name": "activity_agent", "description": "Suggests activities, museums, tours"},
            {"name": "flight_agent", "description": "Searches for flights"},
            {"name": "budget_agent", "description": "Calculates and manages trip budget"},
            {"name": "visa_agent", "description": "Provides visa requirements"},
        ],
    )
    print(f"Score: {tool_result.value:.2f}")
    print(f"Reasoning:\n{tool_result.reason}")
    
    print(f"\n{'='*80}\n")


def demo_comparison():
    """Compare different model judges."""
    print("\n" + "="*80)
    print("DEMO 4: Comparing Different LLM Judges")
    print("="*80)
    
    sample = get_test_samples()[1]  # Hallucination sample
    
    models = [
        "gemini/gemini-2.5-flash",
        # Uncomment if you have these API keys:
        # "openai/gpt-4o-mini",
        # "anthropic/claude-3-5-sonnet-20241022",
    ]
    
    print(f"\nEvaluating hallucination detection with different models...")
    print(f"Sample: {sample.sample_id}")
    print(f"\nOutput to evaluate:\n{sample.agent_output[:200]}...\n")
    
    results = {}
    for model in models:
        try:
            showcase = OpikMetricsShowcase(model=model)
            eval_result = showcase.evaluate_hallucination(sample)
            results[model] = eval_result
            
            print(f"\n{model}:")
            print(f"  Score: {eval_result['score']:.2f}")
            print(f"  Reasoning: {eval_result['reasoning'][:150]}...")
        except Exception as e:
            print(f"\n{model}: ❌ Failed - {str(e)}")
    
    print(f"\n{'='*80}\n")


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Run all demonstrations."""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  Opik LLM-as-a-Judge Evaluation Showcase".center(78) + "█")
    print("█" + "  Travel Lotara AI Agent System".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Configure environment variables first!")
        print("💡 Get OPIK_API_KEY from: https://www.comet.com/signup")
        return
    
    print("\n🚀 Starting evaluation demonstrations...\n")
    
    try:
        # Demo 1: Basic metrics
        demo_basic_metrics()
        
        # Demo 2: Custom G-Eval
        demo_custom_geval()
        
        # Demo 3: Agent metrics
        demo_agent_metrics()
        
        # Demo 4: Compare models
        demo_comparison()
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "  ✅ All demonstrations completed successfully!".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█" + "  📊 View results in Opik dashboard:".center(78) + "█")
        print("█" + "     https://www.comet.com/opik/projects".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
