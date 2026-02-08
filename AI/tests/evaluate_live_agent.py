"""
Integrated Agent Evaluation Script

Evaluates the Travel Lotara agent system end-to-end using Opik metrics.
This script runs real agent queries and evaluates the results.

Usage:
    # Evaluate a single query
    python tests/evaluate_live_agent.py --query "Plan a trip to Paris"
    
    # Evaluate multiple test cases
    python tests/evaluate_live_agent.py --test-suite golden
    
    # Continuous evaluation mode
    python tests/evaluate_live_agent.py --continuous

Features:
✅ Runs your actual agent system
✅ Evaluates output with Opik LLM-as-judge
✅ Logs everything to Opik for tracking
✅ Generates evaluation reports
✅ Supports regression testing
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.travel_lotara.core.eval.opik_showcase import (
    OpikMetricsShowcase,
    TravelQualityGEval,
    AgentTaskCompletionMetric,
    create_evaluation_sample,
    print_evaluation_results,
)

from tests.eval_test_dataset import (
    get_all_test_cases,
    get_by_category,
    get_golden_cases,
)

from opik import track

# Will import agent dynamically to avoid import errors if not configured
try:
    from src.travel_lotara.agents.root_agent import RootAgent
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: Could not import RootAgent: {e}")
    print("Will use mock agent for demonstration")
    AGENT_AVAILABLE = False


class MockAgent:
    """Mock agent for testing when real agent is not available."""
    
    @track(name="mock_agent")
    def process(self, query: str, **kwargs):
        """Return a simple mock response."""
        return {
            "result": f"Mock response to: {query}. This is a placeholder itinerary.",
            "rag_context": [
                "Context chunk 1: Paris is the capital of France.",
                "Context chunk 2: Popular attractions include Eiffel Tower, Louvre."
            ],
            "agents_used": ["planning_agent", "formatter_agent"],
            "metadata": {"mock": True}
        }


class LiveAgentEvaluator:
    """
    Evaluates the Travel Lotara agent in real-time.
    
    Workflow:
    1. Run agent with user query
    2. Extract output and context
    3. Evaluate with Opik metrics
    4. Log results
    5. Generate report
    """
    
    def __init__(self, judge_model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize evaluator.
        
        Args:
            judge_model: LLM model to use for judging (default: Gemini 2.0 Flash)
        """
        self.judge_model = judge_model
        self.showcase = OpikMetricsShowcase(model=judge_model)
        self.quality_eval = TravelQualityGEval(model=judge_model)
        self.task_completion = AgentTaskCompletionMetric(model=judge_model)
        
        # Initialize agent
        if AGENT_AVAILABLE:
            try:
                self.agent = RootAgent()
                print("✅ RootAgent initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize RootAgent: {e}")
                print("Using MockAgent instead")
                self.agent = MockAgent()
        else:
            self.agent = MockAgent()
        
        self.results_history = []
    
    @track(name="evaluate_live_query")
    def evaluate_query(
        self,
        query: str,
        user_preferences: Optional[dict] = None,
        expected_result: Optional[str] = None,
    ) -> dict:
        """
        Run agent on query and evaluate result.
        
        Args:
            query: User's travel query
            user_preferences: Optional preferences (budget, interests, etc.)
            expected_result: Optional expected output for comparison
        
        Returns:
            Comprehensive evaluation results
        """
        print(f"\n{'='*80}")
        print(f"Running agent on query: {query}")
        print(f"{'='*80}\n")
        
        # Run agent
        try:
            agent_output = self.agent.process(
                query,
                user_preferences=user_preferences or {}
            )
            
            # Extract components based on agent output structure
            if isinstance(agent_output, dict):
                output_text = agent_output.get("result", str(agent_output))
                context = agent_output.get("rag_context", [])
                agents_used = agent_output.get("agents_used", [])
                metadata = agent_output.get("metadata", {})
            else:
                output_text = str(agent_output)
                context = []
                agents_used = []
                metadata = {}
            
            print(f"✅ Agent completed\n")
            print(f"Output length: {len(output_text)} chars")
            print(f"Context chunks: {len(context)}")
            print(f"Agents used: {', '.join(agents_used) if agents_used else 'unknown'}\n")
            
        except Exception as e:
            print(f"❌ Agent failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
        
        # Create evaluation sample
        sample = create_evaluation_sample(
            sample_id=f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_query=query,
            agent_output=output_text,
            context=context if isinstance(context, list) else [],
            expected_result=expected_result,
            user_preferences=user_preferences or {},
        )
        
        # Run comprehensive evaluation
        print("Running evaluations...")
        eval_results = self.showcase.evaluate_comprehensive(sample)
        
        # Add custom evaluations
        print("Running travel quality evaluation...")
        quality_result = self.quality_eval.score(
            user_query=query,
            output=output_text,
            user_preferences=user_preferences or {}
        )
        eval_results["evaluations"]["travel_quality"] = {
            "dimension": "travel_quality",
            "score": quality_result.value,
            "reasoning": quality_result.reason,
            "metadata": {"model": self.judge_model}
        }
        
        # Add task completion check
        print("Checking task completion...")
        task_result = self.task_completion.score(
            task_description=query,
            agent_output=output_text
        )
        eval_results["evaluations"]["task_completion"] = {
            "dimension": "task_completion",
            "score": task_result.value,
            "reasoning": task_result.reason,
            "metadata": {"model": self.judge_model}
        }
        
        # Add agent metadata
        eval_results["agent_metadata"] = {
            "agents_used": agents_used,
            "context_chunks_count": len(context),
            "output_length": len(output_text),
            **metadata
        }
        
        # Store results
        self.results_history.append(eval_results)
        
        # Print results
        print_evaluation_results(eval_results)
        
        # Print agent-specific insights
        self._print_agent_insights(eval_results)
        
        return eval_results
    
    def _print_agent_insights(self, results: dict):
        """Print actionable insights from evaluation."""
        print(f"\n{'='*80}")
        print("🔍 AGENT INSIGHTS & RECOMMENDATIONS")
        print(f"{'='*80}\n")
        
        score = results["overall_score"]
        
        # Overall assessment
        if score >= 0.85:
            print("✅ EXCELLENT - Agent performance is strong!")
        elif score >= 0.70:
            print("⚠️  GOOD - Minor improvements possible")
        elif score >= 0.50:
            print("⚠️  ACCEPTABLE - Some issues need attention")
        else:
            print("❌ NEEDS IMPROVEMENT - Significant issues detected")
        
        print(f"\nOverall Score: {score:.2f}/1.0\n")
        
        # Specific recommendations
        recommendations = []
        
        evals = results["evaluations"]
        
        # Check hallucination
        if evals.get("hallucination", {}).get("score", 1.0) < 0.7:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Hallucination detected",
                "action": "Review RAG context quality, ensure agent cites sources"
            })
        
        # Check relevance
        if evals.get("relevance", {}).get("score", 1.0) < 0.7:
            recommendations.append({
                "priority": "HIGH",
                "issue": "Response not relevant to query",
                "action": "Improve query understanding in pre-agent, refine prompts"
            })
        
        # Check context usage
        context_eval = evals.get("context_usage", {})
        if context_eval.get("precision_score", 1.0) < 0.6:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Using irrelevant context",
                "action": "Improve embedding model or add reranking"
            })
        if context_eval.get("recall_score", 1.0) < 0.6:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Missing important context",
                "action": "Increase retrieved chunks or improve retrieval threshold"
            })
        
        # Check safety
        if evals.get("safety", {}).get("score", 1.0) < 0.8:
            recommendations.append({
                "priority": "CRITICAL",
                "issue": "Safety concerns detected",
                "action": "Add content filters, review guardrails"
            })
        
        # Check travel quality
        if evals.get("travel_quality", {}).get("score", 1.0) < 0.7:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": "Travel-specific quality issues",
                "action": "Review itinerary structure, budget accuracy, personalization"
            })
        
        # Print recommendations
        if recommendations:
            print("📋 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. [{rec['priority']}] {rec['issue']}")
                print(f"   → {rec['action']}")
        else:
            print("✨ No major issues detected!")
        
        print(f"\n{'='*80}\n")
    
    def evaluate_test_suite(self, category: str = "golden") -> dict:
        """
        Evaluate agent on a test suite.
        
        Args:
            category: Test category (golden, hallucination, etc.)
        
        Returns:
            Aggregated results across all tests
        """
        print(f"\n{'█'*80}")
        print(f"█  EVALUATING TEST SUITE: {category.upper()}".ljust(79) + "█")
        print(f"{'█'*80}\n")
        
        test_cases = get_by_category(category)
        
        if not test_cases:
            print(f"❌ No test cases found for category: {category}")
            return {}
        
        print(f"Found {len(test_cases)} test cases\n")
        
        results = []
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'─'*80}")
            print(f"Test {i}/{len(test_cases)}: {test_case.id}")
            print(f"{'─'*80}")
            
            # For test dataset, we evaluate the pre-generated output
            # (not running agent again, since we want deterministic results)
            sample = create_evaluation_sample(
                sample_id=test_case.id,
                user_query=test_case.user_query,
                agent_output=test_case.agent_output,
                context=test_case.context,
                expected_result=test_case.expected_result,
                user_preferences=test_case.user_preferences,
            )
            
            eval_result = self.showcase.evaluate_comprehensive(sample)
            results.append(eval_result)
            
            # Check if passed expected range
            min_expected, max_expected = test_case.expected_score_range
            score = eval_result["overall_score"]
            
            if min_expected <= score <= max_expected:
                passed += 1
                status = "✅ PASS"
            else:
                failed += 1
                status = "❌ FAIL"
            
            print(f"\n{status} - Score: {score:.2f} (expected {min_expected:.2f}-{max_expected:.2f})")
        
        # Summary
        print(f"\n{'█'*80}")
        print(f"█  TEST SUITE SUMMARY".ljust(79) + "█")
        print(f"{'█'*80}")
        print(f"\nTotal: {len(test_cases)}")
        print(f"Passed: {passed} ({passed/len(test_cases)*100:.1f}%)")
        print(f"Failed: {failed} ({failed/len(test_cases)*100:.1f}%)")
        
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        print(f"\nAverage Score: {avg_score:.2f}")
        
        if failed == 0:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed} test(s) failed - review results above")
        
        print(f"\n{'█'*80}\n")
        
        return {
            "category": category,
            "total": len(test_cases),
            "passed": passed,
            "failed": failed,
            "average_score": avg_score,
            "results": results
        }
    
    def generate_report(self, output_file: Optional[str] = None):
        """Generate evaluation report."""
        if not self.results_history:
            print("No results to report")
            return
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "judge_model": self.judge_model,
            "total_evaluations": len(self.results_history),
            "results": self.results_history,
            "summary": {
                "average_score": sum(r["overall_score"] for r in self.results_history) / len(self.results_history),
                "min_score": min(r["overall_score"] for r in self.results_history),
                "max_score": max(r["overall_score"] for r in self.results_history),
            }
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {output_file}")
        else:
            print("\n" + "="*80)
            print("EVALUATION REPORT")
            print("="*80)
            print(json.dumps(report["summary"], indent=2))
        
        return report


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Evaluate Travel Lotara Agent with Opik LLM-as-a-judge"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Single query to evaluate"
    )
    
    parser.add_argument(
        "--test-suite",
        type=str,
        choices=["golden", "hallucination", "irrelevant", "poor_context", "safety", "edge", "all"],
        help="Run evaluation on test suite"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gemini/gemini-2.5-flash",
        help="LLM model for judging (default: gemini/gemini-2.5-flash)"
    )
    
    parser.add_argument(
        "--report",
        type=str,
        help="Output file for evaluation report (JSON)"
    )
    
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Continuous evaluation mode (interactive)"
    )
    
    args = parser.parse_args()
    
    # Check environment
    if not os.getenv("OPIK_API_KEY"):
        print("❌ OPIK_API_KEY not set!")
        print("Get it from: https://www.comet.com/signup")
        sys.exit(1)
    
    # Check for appropriate API key based on model
    if "openai" in args.model and not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("Set it or use a different --model (e.g., gemini/gemini-2.5-flash)")
        sys.exit(1)
    elif "gemini" in args.model and not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Set it or use a different --model (e.g., openai/gpt-4o-mini)")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = LiveAgentEvaluator(judge_model=args.model)
    
    # Run based on mode
    if args.query:
        # Single query evaluation
        evaluator.evaluate_query(args.query)
    
    elif args.test_suite:
        # Test suite evaluation
        if args.test_suite == "all":
            categories = ["golden", "hallucination", "irrelevant", "poor_context", "safety", "edge"]
            for category in categories:
                evaluator.evaluate_test_suite(category)
        else:
            evaluator.evaluate_test_suite(args.test_suite)
    
    elif args.continuous:
        # Continuous mode
        print("\n🔄 Continuous Evaluation Mode")
        print("Enter queries to evaluate (or 'quit' to exit)\n")
        
        while True:
            try:
                query = input("Query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query:
                    evaluator.evaluate_query(query)
            except KeyboardInterrupt:
                break
        
        print("\n👋 Exiting...")
    
    else:
        # No mode specified - show help
        parser.print_help()
        print("\nExamples:")
        print('  python tests/evaluate_live_agent.py --query "Plan a 5-day Paris trip"')
        print('  python tests/evaluate_live_agent.py --test-suite golden')
        print('  python tests/evaluate_live_agent.py --continuous')
    
    # Generate report if requested
    if args.report:
        evaluator.generate_report(args.report)


if __name__ == "__main__":
    main()
