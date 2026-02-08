"""
Inline Evaluation Integration for Travel Lotara

Automatically evaluates agent responses in real-time and logs to Opik traces.
Each user request gets evaluated and the results appear in Comet's tracing UI.

Features:
✅ Evaluates every agent response automatically
✅ Logs evaluation metrics to the same trace as agent execution
✅ Shows scores in Comet UI for easy monitoring
✅ Configurable evaluation dimensions
✅ Async support for non-blocking evaluation
✅ Uses Gemini for fast, free LLM-as-judge

Setup:
    1. Enable in settings or environment:
       ENABLE_INLINE_EVALUATION=true
    
    2. Use the decorator on your agent:
       @with_inline_evaluation()
       def process_request(query):
           return agent.process(query)
    
    3. View in Comet UI:
       https://www.comet.com/{workspace}/{project}/traces
"""

import asyncio
import logging
import os
from functools import wraps
from typing import Any, Callable, Optional

from opik import track

from src.travel_lotara.config.settings import get_settings
from src.travel_lotara.core.eval.comprehensive_metrics import (
    SafetyModerationMetric,
    HallucinationDetectionMetric,
    BudgetComplianceMetric,
    ItineraryQualityMetric,
    AnswerRelevanceMetric,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class InlineEvaluator:
    """
    Evaluates agent responses inline with request processing.
    
    Automatically runs evaluation metrics and logs to Opik trace.
    """
    
    def __init__(
        self,
        model: str = "gemini/gemini-2.5-flash",
        enabled: Optional[bool] = None,
        dimensions: Optional[list[str]] = None
    ):
        """
        Initialize inline evaluator.
        
        Args:
            model: LLM model for judging (default: Gemini 2.5 Flash - fast & free)
            enabled: Enable/disable evaluation (default: from settings/env)
            dimensions: Which dimensions to evaluate (default: all)
        """
        # Check if enabled
        if enabled is None:
            enabled = os.getenv("ENABLE_INLINE_EVALUATION", "true").lower() == "true"
        
        self.enabled = enabled
        self.model = model
        
        # Which dimensions to evaluate
        self.dimensions = dimensions or [
            "hallucination",
            "relevance", 
            "safety",
            "quality",
            "budget"
        ]
        
        if not self.enabled:
            logger.info("Inline evaluation disabled")
            return
        
        # Initialize metrics
        self._init_metrics()
        logger.info(f"Inline evaluation enabled with model: {model}")
        logger.info(f"Evaluating dimensions: {', '.join(self.dimensions)}")
    
    def _init_metrics(self):
        """Initialize evaluation metrics."""
        try:
            if "hallucination" in self.dimensions:
                self.hallucination_metric = HallucinationDetectionMetric(model=self.model)
            
            if "relevance" in self.dimensions:
                self.relevance_metric = AnswerRelevanceMetric(model=self.model)
            
            if "safety" in self.dimensions:
                self.safety_metric = SafetyModerationMetric(model=self.model)
            
            if "quality" in self.dimensions:
                self.quality_metric = ItineraryQualityMetric(model=self.model)
            
            if "budget" in self.dimensions:
                self.budget_metric = BudgetComplianceMetric()
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics: {e}")
            self.enabled = False
    
    @track(name="inline_evaluation")
    def evaluate_response(
        self,
        user_query: str,
        agent_output: str,
        context: Optional[list[str]] = None,
        user_preferences: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Evaluate an agent response and log to current Opik trace.
        
        This method is automatically tracked by Opik and will appear
        as a nested span in the agent's trace.
        
        Args:
            user_query: User's original query
            agent_output: Agent's response
            context: RAG context chunks (if any)
            user_preferences: User preferences dict
            metadata: Additional metadata
        
        Returns:
            Dictionary with evaluation scores
        """
        if not self.enabled:
            return {"enabled": False}
        
        try:
            results = {
                "model": self.model,
                "dimensions": {},
                "metadata": metadata or {},
            }
            
            # Evaluate hallucination
            if "hallucination" in self.dimensions:
                try:
                    score = self.hallucination_metric.score(
                        input=user_query,
                        output=agent_output,
                        context=context,
                    )
                    results["dimensions"]["hallucination"] = {
                        "score": score.value,
                        "reason": score.reason,
                    }
                except Exception as e:
                    logger.error(f"Hallucination eval failed: {e}")
                    results["dimensions"]["hallucination"] = {"error": str(e)}
            
            # Evaluate relevance
            if "relevance" in self.dimensions:
                try:
                    score = self.relevance_metric.score(
                        input=user_query,
                        output=agent_output,
                    )
                    results["dimensions"]["relevance"] = {
                        "score": score.value,
                        "reason": score.reason,
                    }
                except Exception as e:
                    logger.error(f"Relevance eval failed: {e}")
                    results["dimensions"]["relevance"] = {"error": str(e)}
            
            # Evaluate safety
            if "safety" in self.dimensions:
                try:
                    score = self.safety_metric.score(
                        input=user_query,
                        output=agent_output,
                    )
                    results["dimensions"]["safety"] = {
                        "score": score.value,
                        "reason": score.reason,
                    }
                except Exception as e:
                    logger.error(f"Safety eval failed: {e}")
                    results["dimensions"]["safety"] = {"error": str(e)}
            
            # Evaluate itinerary quality
            if "quality" in self.dimensions:
                try:
                    score = self.quality_metric.score(
                        user_query=user_query,
                        output=agent_output,
                        user_preferences=user_preferences or {},
                    )
                    results["dimensions"]["quality"] = {
                        "score": score.value,
                        "reason": score.reason,
                    }
                except Exception as e:
                    logger.error(f"Quality eval failed: {e}")
                    results["dimensions"]["quality"] = {"error": str(e)}
            
            # Evaluate budget compliance
            if "budget" in self.dimensions:
                try:
                    expected_budget = None
                    if user_preferences:
                        # Try to extract budget from preferences
                        budget_str = user_preferences.get("budget", "")
                        if budget_str:
                            import re
                            # Extract number from budget string like "$3000" or "3000"
                            match = re.search(r'[\d,]+(?:\.\d{2})?', str(budget_str))
                            if match:
                                expected_budget = float(match.group().replace(',', ''))
                    
                    score = self.budget_metric.score(
                        output=agent_output,
                        expected_budget=expected_budget,
                    )
                    results["dimensions"]["budget"] = {
                        "score": score.value,
                        "reason": score.reason,
                    }
                except Exception as e:
                    logger.error(f"Budget eval failed: {e}")
                    results["dimensions"]["budget"] = {"error": str(e)}
            
            # Calculate overall score
            valid_scores = [
                d["score"] for d in results["dimensions"].values()
                if "score" in d
            ]
            if valid_scores:
                results["overall_score"] = sum(valid_scores) / len(valid_scores)
            else:
                results["overall_score"] = 0.0
            
            # Log summary
            logger.info(
                f"Inline evaluation complete: "
                f"overall={results['overall_score']:.2f}, "
                f"dimensions={len(valid_scores)}"
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Inline evaluation failed: {e}")
            return {"error": str(e), "enabled": True}
    
    async def evaluate_response_async(
        self,
        user_query: str,
        agent_output: str,
        context: Optional[list[str]] = None,
        user_preferences: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Async version of evaluate_response.
        
        Runs evaluation in background without blocking agent response.
        """
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.evaluate_response,
            user_query,
            agent_output,
            context,
            user_preferences,
            metadata,
        )


# Global evaluator instance (singleton)
_global_evaluator: Optional[InlineEvaluator] = None


def get_inline_evaluator() -> InlineEvaluator:
    """Get or create the global inline evaluator."""
    global _global_evaluator
    
    if _global_evaluator is None:
        _global_evaluator = InlineEvaluator()
    
    return _global_evaluator


def with_inline_evaluation(
    extract_query: Optional[Callable] = None,
    extract_output: Optional[Callable] = None,
    extract_context: Optional[Callable] = None,
    extract_preferences: Optional[Callable] = None,
    async_eval: bool = False,
):
    """
    Decorator to add inline evaluation to a function.
    
    Automatically evaluates the function's output and logs to Opik.
    
    Args:
        extract_query: Function to extract query from args/kwargs
        extract_output: Function to extract output from result
        extract_context: Function to extract RAG context from result
        extract_preferences: Function to extract user preferences
        async_eval: Run evaluation asynchronously (non-blocking)
    
    Example:
        @with_inline_evaluation(
            extract_query=lambda args, kwargs: args[0],
            extract_output=lambda result: result['response'],
        )
        def process_travel_request(query, preferences=None):
            return agent.process(query, preferences)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call original function
            result = func(*args, **kwargs)
            
            # Get evaluator
            evaluator = get_inline_evaluator()
            
            if not evaluator.enabled:
                return result
            
            try:
                # Extract components
                if extract_query:
                    query = extract_query(args, kwargs)
                else:
                    # Default: first arg is query
                    query = args[0] if args else kwargs.get("query", "")
                
                if extract_output:
                    output = extract_output(result)
                else:
                    # Default: result is output or result['response']
                    if isinstance(result, dict):
                        output = result.get("response", result.get("result", str(result)))
                    else:
                        output = str(result)
                
                context = extract_context(result) if extract_context else None
                preferences = extract_preferences(args, kwargs) if extract_preferences else None
                
                # Evaluate
                if async_eval:
                    # Fire and forget
                    asyncio.create_task(evaluator.evaluate_response_async(
                        user_query=query,
                        agent_output=output,
                        context=context,
                        user_preferences=preferences,
                    ))
                else:
                    # Synchronous evaluation
                    evaluator.evaluate_response(
                        user_query=query,
                        agent_output=output,
                        context=context,
                        user_preferences=preferences,
                    )
            
            except Exception as e:
                logger.error(f"Inline evaluation decorator failed: {e}")
            
            return result
        
        return wrapper
    
    return decorator


# ============================================
# HELPER FUNCTIONS
# ============================================

def evaluate_agent_output(
    user_query: str,
    agent_output: str,
    context: Optional[list[str]] = None,
    user_preferences: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Convenience function to evaluate agent output.
    
    This is a simple wrapper around the global evaluator.
    
    Args:
        user_query: User's query
        agent_output: Agent's response
        context: RAG context
        user_preferences: User preferences
        metadata: Additional metadata
    
    Returns:
        Evaluation results dict
    
    Example:
        result = agent.process(query)
        eval_result = evaluate_agent_output(
            user_query=query,
            agent_output=result['response'],
            context=result.get('rag_context'),
        )
        print(f"Quality score: {eval_result['overall_score']:.2f}")
    """
    evaluator = get_inline_evaluator()
    return evaluator.evaluate_response(
        user_query=user_query,
        agent_output=agent_output,
        context=context,
        user_preferences=user_preferences,
        metadata=metadata,
    )


if __name__ == "__main__":
    # Demo usage
    print("\\n" + "="*80)
    print("Inline Evaluation Demo")
    print("="*80 + "\\n")
    
    # Create evaluator
    evaluator = InlineEvaluator()
    
    # Example evaluation
    query = "Plan a 3-day trip to Paris"
    output = """
    Day 1: Visit Eiffel Tower and Louvre Museum
    Day 2: Explore Montmartre and Sacré-Cœur
    Day 3: Day trip to Versailles Palace
    
    Estimated cost: $1,200 for accommodation and activities.
    """
    
    context = [
        "Paris is the capital of France with famous landmarks like Eiffel Tower.",
        "Versailles Palace is a UNESCO World Heritage site near Paris.",
    ]
    
    result = evaluator.evaluate_response(
        user_query=query,
        agent_output=output,
        context=context,
        user_preferences={"budget": "$1500", "interests": ["museums", "history"]},
    )
    
    print(f"Overall Score: {result.get('overall_score', 0):.2f}")
    print(f"\\nDimensions:")
    for dim, scores in result.get("dimensions", {}).items():
        if "score" in scores:
            print(f"  {dim}: {scores['score']:.2f}")
    
    print("\\n" + "="*80)
    print("✅ Evaluation complete! Check Comet UI for trace details.")
    print("="*80 + "\\n")
