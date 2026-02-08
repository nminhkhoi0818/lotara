"""
Automatic Evaluation Integration for Travel Lotara Agent System

This module automatically evaluates every agent request/response and logs
the results to Opik traces. Makes it super easy to showcase evaluation
metrics in the Opik UI.

Features:
✅ Automatic evaluation on every request
✅ All 5 metrics logged to the same trace
✅ Non-blocking async evaluation
✅ Budget extraction from user preferences
✅ RAG context extraction
✅ Beautiful console output

Usage:
    # In your main.py or agent runner:
    from src.travel_lotara.core.eval.auto_evaluator import auto_evaluate_response
    
    # After agent processes request:
    auto_evaluate_response(
        user_query=user_input,
        agent_output=response,
        session_state=session.state,
    )

Author: Travel Lotara Team
Date: February 2026
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List

from opik import track
try:
    import opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    
from src.travel_lotara.core.eval.comprehensive_metrics import ComprehensiveTravelEvaluator
from src.travel_lotara.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AutoEvaluator:
    """
    Automatic evaluator that integrates with agent system.
    
    Automatically evaluates every request/response and logs to Opik.
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash", enabled: bool = True):
        """
        Initialize auto evaluator.
        
        Args:
            model: LLM model for evaluation (use LiteLLM format: "gemini/gemini-2.5-flash")
            enabled: Enable/disable automatic evaluation
        """
        self.enabled = enabled and settings.opik_api_key is not None and OPIK_AVAILABLE
        self.model = model
        self.eval_project = settings.opik_eval_project
        
        if self.enabled:
            # Configure Opik for evaluation project
            try:
                opik.configure(
                    api_key=settings.opik_api_key,
                    workspace=settings.opik_workspace_name,
                )
                logger.info(f"Opik configured for eval project: {self.eval_project}")
            except Exception as e:
                logger.warning(f"Failed to configure Opik for evaluations: {e}")
                self.enabled = False
            
            self.evaluator = ComprehensiveTravelEvaluator(model=model)
            logger.info(f"AutoEvaluator initialized with model: {model}")
        else:
            logger.info("AutoEvaluator disabled (no Opik API key or manually disabled)")
    
    @track(name="automatic_evaluation", project_name=settings.opik_eval_project)
    def evaluate_response(
        self,
        user_query: str,
        agent_output: str,
        session_state: Optional[Dict[str, Any]] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Automatically evaluate agent response and log to Opik trace.
        
        This method is @tracked, so it appears as a span in the eval project.
        
        Args:
            user_query: User's travel request
            agent_output: Agent's response
            session_state: Session state dict (contains preferences, itinerary, etc.)
            verbose: Print evaluation results to console
        
        Returns:
            Evaluation results dict with all scores
        """
        if not self.enabled:
            return {"enabled": False, "reason": "Evaluator disabled"}
        
        try:
            # Extract context and preferences from session state
            context = self._extract_rag_context(session_state)
            user_preferences = self._extract_user_preferences(session_state)
            expected_budget = self._extract_budget(user_preferences)
            
            # Run comprehensive evaluation
            results = self.evaluator.evaluate_all(
                user_query=user_query,
                agent_output=agent_output,
                context=context,
                expected_budget=expected_budget,
                user_preferences=user_preferences,
            )
            
            # Print results if verbose
            if verbose:
                self._print_results(results)
            
            return results
        
        except Exception as e:
            logger.error(f"Auto evaluation failed: {e}", exc_info=True)
            return {
                "enabled": True,
                "error": str(e),
                "reason": "Evaluation failed"
            }
    
    async def evaluate_response_async(
        self,
        user_query: str,
        agent_output: str,
        session_state: Optional[Dict[str, Any]] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Async version - evaluates in background without blocking.
        
        Use this for production to avoid delaying response to user.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.evaluate_response,
            user_query,
            agent_output,
            session_state,
            verbose,
        )
    
    def _extract_rag_context(self, session_state: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        """Extract RAG context from session state."""
        if not session_state:
            return None
        
        context_chunks = []
        
        # Try to extract from various possible locations in session state
        # Add any context from attraction retrieval
        attractions = session_state.get("attractions_context", [])
        if attractions:
            if isinstance(attractions, list):
                context_chunks.extend([str(a) for a in attractions])
            else:
                context_chunks.append(str(attractions))
        
        # Add any context from hotel retrieval
        hotels = session_state.get("hotels_context", [])
        if hotels:
            if isinstance(hotels, list):
                context_chunks.extend([str(h) for h in hotels])
            else:
                context_chunks.append(str(hotels))
        
        # Add any context from activities retrieval
        activities = session_state.get("activities_context", [])
        if activities:
            if isinstance(activities, list):
                context_chunks.extend([str(a) for a in activities])
            else:
                context_chunks.append(str(activities))
        
        # Also check for raw RAG results
        rag_results = session_state.get("rag_results", [])
        if rag_results:
            if isinstance(rag_results, list):
                context_chunks.extend([str(r) for r in rag_results])
        
        return context_chunks if context_chunks else None
    
    def _extract_user_preferences(self, session_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract user preferences from session state."""
        if not session_state:
            return {}
        
        preferences = {}
        
        # Get user profile if available
        user_profile = session_state.get("user_profile", {})
        if user_profile:
            preferences.update(user_profile)
        
        # Add budget info
        budget_str = session_state.get("average_budget_spend_per_day", "")
        if budget_str:
            preferences["budget"] = budget_str
        
        # Add duration
        total_days = session_state.get("total_days", "")
        if total_days:
            preferences["duration"] = f"{total_days} days"
        
        # Add destination
        destination = session_state.get("destination", "")
        if destination:
            preferences["destination"] = destination
        
        # Add interests/travel style
        travel_style = user_profile.get("travel_style", "")
        if travel_style:
            preferences["travel_style"] = travel_style
        
        interests = user_profile.get("interests", [])
        if interests:
            preferences["interests"] = interests
        
        return preferences
    
    def _extract_budget(self, user_preferences: Dict[str, Any]) -> Optional[float]:
        """Extract numeric budget from preferences."""
        budget_str = user_preferences.get("budget", "")
        
        if not budget_str:
            return None
        
        try:
            # Handle various budget formats:
            # "$100-200" -> 200 (take upper bound)
            # "$150/day" -> 150
            # "3000" -> 3000
            
            # Extract numbers
            numbers = re.findall(r'[\d,]+(?:\.\d{2})?', str(budget_str))
            if not numbers:
                return None
            
            # Convert to floats
            values = [float(n.replace(',', '')) for n in numbers]
            
            # If it's a range (like "$100-200"), take the upper bound
            budget = max(values)
            
            # If it's per-day budget, multiply by duration
            if "/day" in str(budget_str).lower() or "per day" in str(budget_str).lower():
                duration_str = user_preferences.get("duration", "")
                days_match = re.search(r'(\d+)', str(duration_str))
                if days_match:
                    days = int(days_match.group(1))
                    budget = budget * days
            
            return budget
        
        except Exception as e:
            logger.warning(f"Could not parse budget from '{budget_str}': {e}")
            return None
    
    def _print_results(self, results: Dict[str, Any]):
        """Print evaluation results to console in a beautiful format."""
        print("\n" + "="*80)
        print("📊 AUTOMATIC EVALUATION RESULTS")
        print("="*80)
        
        overall = results.get("overall_score", 0.0)
        print(f"\n🎯 Overall Score: {overall:.2f} / 1.0")
        
        if overall >= 0.8:
            print("   ✅ EXCELLENT - High quality response!")
        elif overall >= 0.6:
            print("   ✓ GOOD - Acceptable quality")
        elif overall >= 0.4:
            print("   ⚠️  NEEDS IMPROVEMENT")
        else:
            print("   ❌ POOR - Review needed")
        
        print("\n" + "-"*80)
        print("Individual Metrics:")
        print("-"*80)
        
        scores = results.get("scores", {})
        
        # Define display order and formatting
        metrics = [
            ("safety_moderation", "🛡️  Safety", True),
            ("hallucination", "🔍 Hallucination", False),  # Lower is better
            ("budget_compliance", "💰 Budget", True),
            ("itinerary_quality", "⭐ Quality", True),
            ("answer_relevance", "🎯 Relevance", True),
        ]
        
        for metric_key, metric_name, higher_is_better in metrics:
            if metric_key not in scores:
                continue
            
            score_data = scores[metric_key]
            
            if "error" in score_data:
                print(f"  {metric_name}: ❌ ERROR")
                print(f"     {score_data['error'][:60]}...")
                continue
            
            score = score_data.get("score", 0.0)
            reason = score_data.get("reason", "")
            
            # Format score with indicator
            if metric_key == "hallucination":
                # Lower is better for hallucination
                if score < 0.3:
                    indicator = "✅"
                elif score < 0.7:
                    indicator = "⚠️ "
                else:
                    indicator = "❌"
            else:
                # Higher is better for others
                if score >= 0.8:
                    indicator = "✅"
                elif score >= 0.6:
                    indicator = "✓"
                elif score >= 0.4:
                    indicator = "⚠️ "
                else:
                    indicator = "❌"
            
            print(f"  {metric_name}: {indicator} {score:.2f}")
            
            # Print reason (truncated)
            if reason:
                reason_short = reason[:70] + "..." if len(reason) > 70 else reason
                print(f"     → {reason_short}")
        
        print("\n" + "="*80)
        print(f"🔗 View in Opik: https://www.comet.com/{settings.opik_workspace_name}/{settings.opik_eval_project}/traces")
        print("="*80 + "\n")


# Global singleton instance
_global_auto_evaluator: Optional[AutoEvaluator] = None


def get_auto_evaluator() -> AutoEvaluator:
    """Get or create the global auto evaluator."""
    global _global_auto_evaluator
    
    if _global_auto_evaluator is None:
        _global_auto_evaluator = AutoEvaluator()
    
    return _global_auto_evaluator


@track(name="auto_evaluation_wrapper", project_name=settings.opik_eval_project)
def auto_evaluate_response(
    user_query: str,
    agent_output: str,
    session_state: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to automatically evaluate response.
    
    Use this after your agent processes a request.
    Logs evaluation results to the lotara-evals project in Opik.
    
    Args:
        user_query: User's travel request
        agent_output: Agent's response
        session_state: Session state from your agent
        verbose: Print results to console
    
    Returns:
        Evaluation results
    
    Example:
        # In your agent runner:
        response = await agent.process(user_query)
        
        # Automatically evaluate
        eval_results = auto_evaluate_response(
            user_query=user_query,
            agent_output=response,
            session_state=session.state,
        )
    """
    evaluator = get_auto_evaluator()
    return evaluator.evaluate_response(
        user_query=user_query,
        agent_output=agent_output,
        session_state=session_state,
        verbose=verbose,
    )


async def auto_evaluate_response_async(
    user_query: str,
    agent_output: str,
    session_state: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Async version - evaluates in background without blocking.
    
    Use this in production to avoid delaying response to user.
    """
    evaluator = get_auto_evaluator()
    return await evaluator.evaluate_response_async(
        user_query=user_query,
        agent_output=agent_output,
        session_state=session_state,
        verbose=verbose,
    )


__all__ = [
    "AutoEvaluator",
    "get_auto_evaluator",
    "auto_evaluate_response",
    "auto_evaluate_response_async",
]
