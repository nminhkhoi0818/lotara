"""
Comprehensive Evaluation Metrics for Travel Lotara AI Agent System

This module implements all evaluation metrics for the travel assistant with proper Opik tracing:
1. Safety Moderation (Opik built-in)
2. Hallucination Detection (Opik built-in)
3. Budget Compliance (Custom metric)
4. Itinerary Quality (Custom G-Eval metric)
5. Answer Relevance (Opik built-in)

Reference: https://www.comet.com/docs/opik/python-sdk-reference/evaluation/metrics/

Author: Travel Lotara Team
Date: February 2026
"""

import logging
import re
from typing import Any, Optional, Dict, List
from dataclasses import dataclass

# Opik imports
from opik import track
from opik.evaluation.metrics import (
    # Built-in Opik metrics
    Hallucination,
    AnswerRelevance,
    Moderation,
    ContextPrecision,
    ContextRecall,
    # Base classes for custom metrics
    base_metric,
    score_result,
)

from src.travel_lotara.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================
# DATACLASSES FOR STRUCTURED INPUTS
# ============================================

@dataclass
class TravelEvaluationInput:
    """Structured input for travel evaluation metrics."""
    user_query: str
    agent_output: str
    context: Optional[List[str]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    expected_budget: Optional[float] = None
    expected_tools: Optional[List[str]] = None


# ============================================
# 1. SAFETY MODERATION METRIC (Opik Built-in)
# ============================================

class SafetyModerationMetric:
    """
    Safety Moderation using Opik's built-in Moderation metric.
    
    Checks for:
    - Inappropriate content
    - Harmful recommendations
    - Privacy violations
    - Policy compliance
    
    Reference: https://www.comet.com/docs/opik/python-sdk-reference/evaluation/metrics/Moderation.html
    
    Score: 0.0 (flagged) to 1.0 (safe)
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize safety moderation metric.
        
        Args:
            model: LLM model for moderation checks (e.g., "gemini/gemini-2.5-flash")
        """
        self.metric = Moderation(model=model)
        self.model = model
        logger.info(f"SafetyModeration initialized with model: {model}")
    
    @track(name="safety_moderation_check", project_name=settings.opik_eval_project)
    def score(
        self,
        input: str,
        output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score content safety.
        
        Args:
            input: User's query
            output: Agent's response
        
        Returns:
            ScoreResult with value 0.0-1.0 (1.0 = safe)
        """
        try:
            result = self.metric.score(
                input=input,
                output=output,
            )
            logger.info(f"Safety score: {result.value:.2f}")
            return result
        except Exception as e:
            logger.error(f"Safety moderation failed: {e}")
            return score_result.ScoreResult(
                value=0.0,
                name="safety_moderation",
                reason=f"Evaluation failed: {str(e)}"
            )


# ============================================
# 2. HALLUCINATION DETECTION (Opik Built-in)
# ============================================

class HallucinationDetectionMetric:
    """
    Hallucination Detection using Opik's built-in Hallucination metric.
    
    Detects when the agent makes false or unverifiable claims about:
    - Destination information
    - Prices and costs
    - Travel requirements
    - Facilities and amenities
    
    Reference: https://www.comet.com/docs/opik/python-sdk-reference/evaluation/metrics/Hallucination.html
    
    Score: 0.0 (no hallucination) to 1.0 (severe hallucination)
    Note: Lower is better!
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize hallucination detection metric.
        
        Args:
            model: LLM model for hallucination detection
        """
        self.metric = Hallucination(model=model)
        self.model = model
        logger.info(f"HallucinationDetection initialized with model: {model}")
    
    @track(name="hallucination_detection", project_name=settings.opik_eval_project)
    def score(
        self,
        input: str,
        output: str,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Detect hallucinations in agent output.
        
        Args:
            input: User's query
            output: Agent's response
            context: RAG context chunks (if available)
        
        Returns:
            ScoreResult with value 0.0-1.0 (0.0 = no hallucination, lower is better)
        """
        try:
            result = self.metric.score(
                input=input,
                output=output,
                context=context if context else None,
            )
            logger.info(f"Hallucination score: {result.value:.2f} (lower is better)")
            return result
        except Exception as e:
            logger.error(f"Hallucination detection failed: {e}\")")
            return score_result.ScoreResult(
                value=1.0,  # Assume worst case on error
                name="hallucination",
                reason=f"Evaluation failed: {str(e)}"
            )


# ============================================
# 3. BUDGET COMPLIANCE METRIC (Custom)
# ============================================

class BudgetComplianceMetric(base_metric.BaseMetric):
    """
    Custom metric to evaluate budget compliance in travel itineraries.
    
    Checks:
    - Total cost vs user budget
    - Cost breakdown clarity
    - Value for money
    - Transparent pricing
    
    Score: 0.0 (way over budget) to 1.0 (within budget)
    """
    
    def __init__(self, name: str = "budget_compliance", tolerance: float = 0.1):
        """
        Initialize budget compliance metric.
        
        Args:
            name: Metric name for tracking
            tolerance: Acceptable budget overage (0.1 = 10%)
        """
        super().__init__(name=name)
        self.tolerance = tolerance
        logger.info(f"BudgetCompliance initialized with tolerance: {tolerance*100}%")
    
    @track(name="budget_compliance_check", project_name=settings.opik_eval_project)
    def score(
        self,
        output: str,
        expected_budget: Optional[float] = None,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score budget compliance.
        
        Args:
            output: Agent's itinerary response
            expected_budget: User's stated budget
        
        Returns:
            ScoreResult with compliance score 0.0-1.0
        """
        if not expected_budget:
            return score_result.ScoreResult(
                value=0.5,
                name=self.name,
                reason="No budget specified by user - cannot evaluate compliance"
            )
        
        # Extract costs from output
        costs = self._extract_costs(output)
        
        if not costs:
            return score_result.ScoreResult(
                value=0.3,
                name=self.name,
                reason="No costs found in itinerary - poor budget transparency"
            )
        
        # Calculate total and compare to budget
        total_cost = max(costs)  # Assume largest value is total
        
        return self._calculate_compliance_score(total_cost, expected_budget)
    
    def _extract_costs(self, text: str) -> List[float]:
        """Extract all cost values from text."""
        # Match patterns like: $1,234.56 or $1234 or 1234.56
        cost_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $1,234.56
            r'€[\d,]+(?:\.\d{2})?',   # €1,234.56
            r'£[\d,]+(?:\.\d{2})?',   # £1,234.56
        ]
        
        costs = []
        for pattern in cost_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Remove currency symbols and commas
                    clean_value = re.sub(r'[$€£,]', '', match)
                    costs.append(float(clean_value))
                except ValueError:
                    continue
        
        return costs
    
    def _calculate_compliance_score(self, total_cost: float, budget: float) -> score_result.ScoreResult:
        """Calculate compliance score based on budget adherence."""
        ratio = total_cost / budget
        
        if ratio <= 1.0:
            # Within budget - perfect score
            score = 1.0
            reason = f"✓ Excellent! Total ${total_cost:,.0f} is within budget of ${budget:,.0f}"
        elif ratio <= 1.0 + self.tolerance:
            # Within tolerance (e.g., 10% over)
            score = 0.8
            overage_pct = (ratio - 1.0) * 100
            reason = f"Acceptable: ${total_cost:,.0f} is {overage_pct:.1f}% over budget of ${budget:,.0f}"
        elif ratio <= 1.25:
            # 25% over budget
            score = 0.5
            overage_pct = (ratio - 1.0) * 100
            reason = f"⚠ Over budget: ${total_cost:,.0f} is {overage_pct:.1f}% over ${budget:,.0f}"
        elif ratio <= 1.5:
            # 50% over budget
            score = 0.3
            overage_pct = (ratio - 1.0) * 100
            reason = f"✗ Significantly over: ${total_cost:,.0f} is {overage_pct:.1f}% over ${budget:,.0f}"
        else:
            # Way over budget
            score = 0.1
            overage_pct = (ratio - 1.0) * 100
            reason = f"✗✗ Way over budget: ${total_cost:,.0f} is {overage_pct:.1f}% over ${budget:,.0f}"
        
        logger.info(f"Budget compliance: {score:.2f} - {reason}")
        
        return score_result.ScoreResult(
            value=score,
            name=self.name,
            reason=reason
        )


# ============================================
# 4. ITINERARY QUALITY METRIC (Custom G-Eval)
# ============================================

class ItineraryQualityMetric(base_metric.BaseMetric):
    """
    Custom G-Eval metric for itinerary quality assessment.
    
    Evaluates:
    - Structure and organization
    - Activity diversity
    - Logical flow and pacing
    - Completeness (hotels, flights, activities, etc.)
    - Personalization to user preferences
    
    Reference: https://www.comet.com/docs/opik/python-sdk-reference/evaluation/metrics/GEval.html
    
    Score: 0.0 (poor quality) to 1.0 (excellent quality)
    """
    
    def __init__(
        self,
        model: str = "gemini/gemini-2.5-flash",
        name: str = "itinerary_quality"
    ):
        """
        Initialize itinerary quality metric.
        
        Args:
            model: LLM model for G-Eval assessment
            name: Metric name for tracking
        """
        super().__init__(name=name)
        self.model = model
        logger.info(f"ItineraryQuality initialized with model: {model}")
    
    @track(name="itinerary_quality_assessment")
    def score(
        self,
        user_query: str,
        output: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score itinerary quality using LLM-as-judge.
        
        Args:
            user_query: User's travel request
            output: Agent's itinerary
            user_preferences: User preferences (budget, interests, etc.)
        
        Returns:
            ScoreResult with quality score 0.0-1.0
        """
        from litellm import completion
        
        preferences = user_preferences or {}
        
        # Build G-Eval prompt
        eval_prompt = self._build_quality_prompt(user_query, output, preferences)
        
        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert travel planning evaluator. Be critical but fair."},
                    {"role": "user", "content": eval_prompt}
                ],
                temperature=0.0,  # Deterministic for evaluation
            )
            
            judge_response = response.choices[0].message.content
            
            # Parse score and reasoning
            score, reasoning = self._parse_judge_response(judge_response)
            
            logger.info(f"Itinerary quality score: {score:.2f}")
            
            return score_result.ScoreResult(
                value=score,
                name=self.name,
                reason=reasoning
            )
        
        except Exception as e:
            logger.error(f"Itinerary quality evaluation failed: {e}")
            return score_result.ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Evaluation failed: {str(e)}"
            )
    
    def _build_quality_prompt(
        self,
        user_query: str,
        output: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Build comprehensive quality evaluation prompt."""
        return f"""Evaluate this travel itinerary on a scale of 0.0 to 1.0.

USER REQUEST:
{user_query}

USER PREFERENCES:
- Budget: {preferences.get('budget', 'Not specified')}
- Interests: {preferences.get('interests', 'Not specified')}
- Duration: {preferences.get('duration', 'Not specified')}
- Travel Style: {preferences.get('travel_style', 'Not specified')}

ITINERARY PROVIDED:
{output}

EVALUATION CRITERIA (rate each 0.0-1.0):

1. STRUCTURE & ORGANIZATION (30%):
   - Is the itinerary well-organized by days/activities?
   - Are timings realistic and feasible?
   - Is there a logical flow to activities?
   - Clear sections for flights, hotels, activities?

2. COMPLETENESS (25%):
   - Does it include all essential components (transport, accommodation, activities)?
   - Are important details provided (addresses, times, costs)?
   - Are travel documents/requirements mentioned if needed?

3. QUALITY & DIVERSITY (25%):
   - Are activities diverse and interesting?
   - Is there good pacing (not too rushed or too slow)?
   - Mix of popular attractions and authentic experiences?
   - Appropriate for the destination?

4. PERSONALIZATION (20%):
   - Does it match the user's stated interests?
   - Is the style (luxury/budget/adventure) appropriate?
   - Are unique, thoughtful recommendations included?
   - Does it address user's specific requests?

Provide your evaluation in this EXACT format:
SCORE: <single number 0.0 to 1.0>
REASONING: <2-3 sentence explanation covering all criteria>

Example:
SCORE: 0.85
REASONING: The itinerary is well-structured with clear daily breakdowns and realistic timing. It includes all essential components and shows good personalization to the user's food and culture interests. Minor improvement needed in activity diversity.
"""
    
    def _parse_judge_response(self, response: str) -> tuple[float, str]:
        """Parse LLM judge response to extract score and reasoning."""
        # Extract score
        score_match = re.search(r'SCORE:\s*([0-9.]+)', response, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
        else:
            # Fallback: look for any number between 0-1
            numbers = re.findall(r'\b0\.\d+\b|\b1\.0\b', response)
            score = float(numbers[0]) if numbers else 0.5
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            # Use the whole response if no clear reasoning section
            reasoning = response.strip()
        
        # Clamp score to valid range
        score = max(0.0, min(1.0, score))
        
        return score, reasoning


# ============================================
# 5. ANSWER RELEVANCE METRIC (Opik Built-in)
# ============================================

class AnswerRelevanceMetric:
    """
    Answer Relevance using Opik's built-in AnswerRelevance metric.
    
    Checks if the agent's response is relevant to the user's query.
    
    Reference: https://www.comet.com/docs/opik/python-sdk-reference/evaluation/metrics/AnswerRelevance.html
    
    Score: 0.0 (irrelevant) to 1.0 (highly relevant)
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize answer relevance metric.
        
        Args:
            model: LLM model for relevance assessment
        """
        # AnswerRelevance requires context by default - disable for travel use case
        self.metric = AnswerRelevance(model=model, require_context=False)
        self.model = model
        logger.info(f"AnswerRelevance initialized with model: {model} (context not required)")
    
    @track(name="answer_relevance_check", project_name=settings.opik_eval_project)
    def score(
        self,
        input: str,
        output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score answer relevance.
        
        Args:
            input: User's query
            output: Agent's response
        
        Returns:
            ScoreResult with relevance score 0.0-1.0
        """
        try:
            result = self.metric.score(
                input=input,
                output=output,
            )
            logger.info(f"Answer relevance score: {result.value:.2f}")
            return result
        except Exception as e:
            logger.error(f"Answer relevance check failed: {e}")
            return score_result.ScoreResult(
                value=0.0,
                name="answer_relevance",
                reason=f"Evaluation failed: {str(e)}"
            )


# ============================================
# COMPREHENSIVE EVALUATOR
# ============================================

class ComprehensiveTravelEvaluator:
    """
    Comprehensive evaluator that runs all metrics on agent outputs.
    
    Usage:
        evaluator = ComprehensiveTravelEvaluator()
        results = evaluator.evaluate_all(
            user_query="Plan a trip to Paris for $3000",
            agent_output="Here's your Paris itinerary...",
            context=["Paris is...", "Hotels in Paris..."],
            expected_budget=3000,
            user_preferences={"interests": ["art", "food"]}
        )
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize all metrics.
        
        Args:
            model: LLM model for LLM-as-judge metrics
        """
        self.model = model
        
        # Initialize all metrics
        self.safety = SafetyModerationMetric(model=model)
        self.hallucination = HallucinationDetectionMetric(model=model)
        self.budget = BudgetComplianceMetric()
        self.itinerary_quality = ItineraryQualityMetric(model=model)
        self.relevance = AnswerRelevanceMetric(model=model)
        
        logger.info(f"ComprehensiveTravelEvaluator initialized with model: {model}")
    
    @track(name="comprehensive_evaluation", project_name=settings.opik_eval_project)
    def evaluate_all(
        self,
        user_query: str,
        agent_output: str,
        context: Optional[List[str]] = None,
        expected_budget: Optional[float] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run all evaluation metrics on agent output.
        
        Args:
            user_query: User's travel request
            agent_output: Agent's response/itinerary
            context: RAG context chunks
            expected_budget: User's budget
            user_preferences: User preferences dict
        
        Returns:
            Dictionary with all evaluation scores and overall assessment
        """
        results = {
            "user_query": user_query,
            "model": self.model,
            "scores": {},
            "metadata": {}
        }
        
        # 1. Safety Moderation
        try:
            safety_result = self.safety.score(input=user_query, output=agent_output)
            results["scores"]["safety_moderation"] = {
                "score": safety_result.value,
                "reason": safety_result.reason,
            }
        except Exception as e:
            logger.error(f"Safety evaluation failed: {e}")
            results["scores"]["safety_moderation"] = {"error": str(e)}
        
        # 2. Hallucination Detection
        try:
            hallucination_result = self.hallucination.score(
                input=user_query,
                output=agent_output,
                context=context
            )
            results["scores"]["hallucination"] = {
                "score": hallucination_result.value,
                "reason": hallucination_result.reason,
            }
        except Exception as e:
            logger.error(f"Hallucination evaluation failed: {e}")
            results["scores"]["hallucination"] = {"error": str(e)}
        
        # 3. Budget Compliance
        try:
            budget_result = self.budget.score(
                output=agent_output,
                expected_budget=expected_budget
            )
            results["scores"]["budget_compliance"] = {
                "score": budget_result.value,
                "reason": budget_result.reason,
            }
        except Exception as e:
            logger.error(f"Budget evaluation failed: {e}")
            results["scores"]["budget_compliance"] = {"error": str(e)}
        
        # 4. Itinerary Quality
        try:
            quality_result = self.itinerary_quality.score(
                user_query=user_query,
                output=agent_output,
                user_preferences=user_preferences
            )
            results["scores"]["itinerary_quality"] = {
                "score": quality_result.value,
                "reason": quality_result.reason,
            }
        except Exception as e:
            logger.error(f"Itinerary quality evaluation failed: {e}")
            results["scores"]["itinerary_quality"] = {"error": str(e)}
        
        # 5. Answer Relevance
        try:
            relevance_result = self.relevance.score(
                input=user_query,
                output=agent_output
            )
            results["scores"]["answer_relevance"] = {
                "score": relevance_result.value,
                "reason": relevance_result.reason,
            }
        except Exception as e:
            logger.error(f"Answer relevance evaluation failed: {e}")
            results["scores"]["answer_relevance"] = {"error": str(e)}
        
        # Calculate overall score (weighted average)
        weights = {
            "safety_moderation": 0.25,     # Critical
            "hallucination": 0.25,         # Critical (inverted: low is good)
            "budget_compliance": 0.20,     # Important
            "itinerary_quality": 0.20,     # Important
            "answer_relevance": 0.10,      # Nice to have
        }
        
        overall_score = 0.0
        valid_scores = 0
        
        for metric_name, weight in weights.items():
            score_data = results["scores"].get(metric_name, {})
            if "score" in score_data and "error" not in score_data:
                score = score_data["score"]
                
                # Invert hallucination score (lower is better, so 1.0 - score)
                if metric_name == "hallucination":
                    score = 1.0 - score
                
                overall_score += score * weight
                valid_scores += weight
        
        # Normalize if some metrics failed
        if valid_scores > 0:
            overall_score = overall_score / valid_scores
        
        results["overall_score"] = overall_score
        results["metadata"]["valid_metrics"] = list(
            k for k, v in results["scores"].items() if "error" not in v
        )
        
        logger.info(f"Overall evaluation score: {overall_score:.2f}")
        
        return results


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "SafetyModerationMetric",
    "HallucinationDetectionMetric",
    "BudgetComplianceMetric",
    "ItineraryQualityMetric",
    "AnswerRelevanceMetric",
    "ComprehensiveTravelEvaluator",
    "TravelEvaluationInput",
]
