"""
Alternative Approach: Store Trace ID in State

Since callbacks run outside the @track decorator context, we need to
store the trace ID in the agent state when it starts, then retrieve
it in the callback.

This integrates with the existing OpikTracer infrastructure.
"""

import logging
from typing import Optional

import opik
from opik.evaluation.metrics import (
    Hallucination,
    AnswerRelevance,
    Moderation,
)

from src.travel_lotara.core.eval.opik_showcase import TravelQualityGEval

logger = logging.getLogger(__name__)


def evaluate_with_stored_trace_id(
    state: dict,
    user_query: str,
    agent_output: str,
    context: Optional[list[str]] = None,
    user_preferences: Optional[dict] = None,
    model: str = "gemini/gemini-2.5-flash",
) -> dict:
    """
    Evaluate agent output using trace ID stored in state.
    
    This is designed for use in callbacks where the trace context
    is not directly available.
    
    Args:
        state: Agent state dictionary (should contain _opik_trace_id)
        user_query: User's original query
        agent_output: Agent's response
        context: RAG context chunks
        user_preferences: User preferences
        model: LLM judge model
    
    Returns:
        Evaluation results dictionary
    """
    # Get trace ID from state
    trace_id = state.get("_opik_trace_id")
    
    if not trace_id:
        logger.warning("No trace ID found in state - cannot add evaluation scores")
        logger.info("Make sure to store trace_id in state during agent initialization")
        return {"error": "No trace ID in state", "enabled": False}
    
    logger.info(f"Evaluating with trace ID from state: {trace_id}")
    
    # Initialize Opik client
    client = opik.Opik()
    
    results = {
        "trace_id": trace_id,
        "scores": {},
        "model": model,
    }
    
    try:
        # Initialize metrics
        hallucination_metric = Hallucination(model=model)
        relevance_metric = AnswerRelevance(model=model)
        moderation_metric = Moderation(model=model)
        quality_metric = TravelQualityGEval(model=model)
        
        # Evaluate hallucination
        try:
            score = hallucination_metric.score(
                input=user_query,
                output=agent_output,
                context=context or [],
            )
            results["scores"]["hallucination"] = score.value
            client.score(
                trace_id=trace_id,
                name="Hallucination",
                value=score.value,
                reason=score.reason,
            )
        except Exception as e:
            logger.error(f"Hallucination eval failed: {e}")
        
        # Evaluate relevance
        try:
            score = relevance_metric.score(
                input=user_query,
                output=agent_output,
            )
            results["scores"]["relevance"] = score.value
            client.score(
                trace_id=trace_id,
                name="Answer Relevance",
                value=score.value,
                reason=score.reason,
            )
        except Exception as e:
            logger.error(f"Relevance eval failed: {e}")
        
        # Evaluate safety
        try:
            score = moderation_metric.score(
                input=user_query,
                output=agent_output,
            )
            results["scores"]["safety"] = score.value
            client.score(
                trace_id=trace_id,
                name="Safety",
                value=score.value,
                reason=score.reason,
            )
        except Exception as e:
            logger.error(f"Safety eval failed: {e}")
        
        # Evaluate travel quality
        try:
            score = quality_metric.score(
                user_query=user_query,
                output=agent_output,
                user_preferences=user_preferences or {},
            )
            results["scores"]["quality"] = score.value
            client.score(
                trace_id=trace_id,
                name="Travel Quality",
                value=score.value,
                reason=score.reason,
            )
        except Exception as e:
            logger.error(f"Quality eval failed: {e}")
        
        # Calculate overall
        valid_scores = [s for s in results["scores"].values() if s is not None]
        if valid_scores:
            overall = sum(valid_scores) / len(valid_scores)
            results["overall_score"] = overall
            client.score(
                trace_id=trace_id,
                name="Overall Quality",
                value=overall,
                reason=f"Average of {len(valid_scores)} dimensions",
            )
            logger.info(f"✅ Evaluation complete: overall={overall:.2f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return {"error": str(e), "trace_id": trace_id}


def store_trace_id_in_state(state: dict):
    """
    Store current Opik trace ID in agent state.
    
    Call this in before_agent_callback or agent initialization.
    
    Args:
        state: Agent state dictionary
    """
    try:
        span_data = opik.get_current_span_data()
        if span_data and "trace_id" in span_data:
            trace_id = span_data["trace_id"]
            state["_opik_trace_id"] = trace_id
            logger.debug(f"Stored trace ID in state: {trace_id}")
            return trace_id
    except Exception as e:
        logger.debug(f"Could not store trace ID: {e}")
    
    return None
