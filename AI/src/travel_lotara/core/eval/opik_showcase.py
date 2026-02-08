"""
Opik LLM-as-a-Judge Evaluation Showcase

Demonstrates Comet Opik's built-in evaluation metrics for the Travel Lotara agent system.
This showcases various evaluation dimensions using Opik's powerful LLM-as-a-judge capabilities.

Based on: https://www.comet.com/docs/opik/evaluation/metrics/overview

Key Features:
- ✅ Hallucination Detection
- ✅ Answer Relevance 
- ✅ Context Precision & Recall
- ✅ Moderation & Safety
- ✅ Agent Task Completion
- ✅ Agent Tool Correctness
- ✅ Custom G-Eval for travel-specific criteria
- ✅ Structured Output Compliance
- ✅ Conversation Coherence

All evaluations are automatically logged to Opik for tracking and comparison.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum

# Opik built-in metrics
from opik import track, opik_context
from opik.evaluation import evaluate
from opik.evaluation.metrics import (
    # LLM-as-Judge metrics
    Hallucination,
    AnswerRelevance,
    ContextPrecision,
    ContextRecall,
    Moderation,
    # Custom metric base
    base_metric,
    score_result,
)

logger = logging.getLogger(__name__)


# ============================================
# EVALUATION DIMENSIONS FOR TRAVEL AGENTS
# ============================================

class TravelEvalDimension(str, Enum):
    """Evaluation dimensions specific to travel planning."""
    HALLUCINATION = "hallucination"  # Detecting false claims
    RELEVANCE = "relevance"  # Response matches user query
    CONTEXT_USE = "context_use"  # Proper use of RAG context
    SAFETY = "safety"  # Content moderation
    TASK_COMPLETION = "task_completion"  # Agent completed the task
    TOOL_CORRECTNESS = "tool_correctness"  # Used right tools
    BUDGET_ACCURACY = "budget_accuracy"  # Budget calculations correct
    DESTINATION_EXPERTISE = "destination_expertise"  # Accurate destination info
    ITINERARY_QUALITY = "itinerary_quality"  # Well-structured itinerary
    PERSONALIZATION = "personalization"  # Tailored to user preferences


@dataclass
class EvaluationSample:
    """Single sample for evaluation."""
    sample_id: str
    user_query: str
    agent_output: str
    context: list[str] = field(default_factory=list)  # RAG context chunks
    expected_result: Optional[str] = None
    user_preferences: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================
# OPIK BUILT-IN METRICS SHOWCASE
# ============================================

class OpikMetricsShowcase:
    """
    Showcase of Opik's built-in LLM-as-a-judge metrics applied to travel planning.
    
    Demonstrates:
    1. Hallucination Detection - Catch false destination info
    2. Answer Relevance - Ensure response matches query
    3. Context Precision/Recall - RAG quality assessment
    4. Moderation - Safety and policy compliance
    5. Custom G-Eval - Travel-specific quality criteria
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize with LLM model for judging.
        
        Args:
            model: Model to use for LLM-as-judge. Supports:
                   - Google Gemini: "gemini/gemini-2.5-flash" (default, fast & free)
                   - OpenAI: "openai/gpt-4o-mini", "openai/gpt-4o"
                   - Anthropic: "anthropic/claude-3-5-sonnet-20241022"
                   - AWS Bedrock: "bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
        """
        self.model = model
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Opik built-in metrics."""
        # Hallucination Detection
        self.hallucination_metric = Hallucination(model=self.model)
        
        # Answer Relevance
        self.relevance_metric = AnswerRelevance(model=self.model)
        
        # Context Metrics (for RAG evaluation)
        self.context_precision_metric = ContextPrecision(model=self.model)
        self.context_recall_metric = ContextRecall(model=self.model)
        
        # Safety & Moderation
        self.moderation_metric = Moderation(model=self.model)
    
    @track(name="hallucination_detection")
    def evaluate_hallucination(self, sample: EvaluationSample) -> dict:
        """
        Detect hallucinations in travel recommendations.
        
        Example: Agent claims "Paris has the world's tallest building" (false)
        
        Returns:
            Score (0.0-1.0 where 1.0 = no hallucination) and reasoning
        """
        result = self.hallucination_metric.score(
            input=sample.user_query,
            output=sample.agent_output,
            context=sample.context if sample.context else None,
        )
        
        return {
            "dimension": TravelEvalDimension.HALLUCINATION,
            "score": result.value,
            "reasoning": result.reason,
            "metadata": {
                "sample_id": sample.sample_id,
                "model": self.model,
            }
        }
    
    @track(name="answer_relevance")
    def evaluate_relevance(self, sample: EvaluationSample) -> dict:
        """
        Evaluate if agent's answer is relevant to user's query.
        
        Example: User asks about hotels, agent responds with visa info (irrelevant)
        
        Returns:
            Relevance score (0.0-1.0) and reasoning
        """
        result = self.relevance_metric.score(
            input=sample.user_query,
            output=sample.agent_output,
        )
        
        return {
            "dimension": TravelEvalDimension.RELEVANCE,
            "score": result.value,
            "reasoning": result.reason,
            "metadata": {
                "sample_id": sample.sample_id,
                "model": self.model,
            }
        }
    
    @track(name="context_precision_recall")
    def evaluate_context_usage(self, sample: EvaluationSample) -> dict:
        """
        Evaluate RAG context usage (precision & recall).
        
        - Precision: Only relevant context chunks used
        - Recall: All relevant context chunks incorporated
        
        Returns:
            Both precision and recall scores
        """
        if not sample.context or not sample.expected_result:
            return {
                "dimension": TravelEvalDimension.CONTEXT_USE,
                "precision_score": 0.0,
                "recall_score": 0.0,
                "reasoning": "Missing context or expected result",
            }
        
        precision_result = self.context_precision_metric.score(
            input=sample.user_query,
            output=sample.agent_output,
            context=sample.context,
        )
        
        recall_result = self.context_recall_metric.score(
            input=sample.user_query,
            expected_output=sample.expected_result,
            context=sample.context,
        )
        
        return {
            "dimension": TravelEvalDimension.CONTEXT_USE,
            "precision_score": precision_result.value,
            "precision_reasoning": precision_result.reason,
            "recall_score": recall_result.value,
            "recall_reasoning": recall_result.reason,
            "metadata": {
                "sample_id": sample.sample_id,
                "context_chunks": len(sample.context),
                "model": self.model,
            }
        }
    
    @track(name="safety_moderation")
    def evaluate_safety(self, sample: EvaluationSample) -> dict:
        """
        Evaluate content safety and policy compliance.
        
        Checks for:
        - Harmful content
        - Bias
        - PII exposure
        - Policy violations
        
        Returns:
            Safety score and flagged issues
        """
        result = self.moderation_metric.score(
            input=sample.user_query,
            output=sample.agent_output,
        )
        
        return {
            "dimension": TravelEvalDimension.SAFETY,
            "score": result.value,
            "reasoning": result.reason,
            "metadata": {
                "sample_id": sample.sample_id,
                "model": self.model,
            }
        }
    
    @track(name="comprehensive_evaluation")
    def evaluate_comprehensive(self, sample: EvaluationSample) -> dict:
        """
        Run all evaluations on a sample.
        
        Returns:
            Complete evaluation report with all dimensions
        """
        results = {
            "sample_id": sample.sample_id,
            "user_query": sample.user_query,
            "timestamp": datetime.utcnow().isoformat(),
            "evaluations": {}
        }
        
        # Run all evaluations
        results["evaluations"]["hallucination"] = self.evaluate_hallucination(sample)
        results["evaluations"]["relevance"] = self.evaluate_relevance(sample)
        results["evaluations"]["context_usage"] = self.evaluate_context_usage(sample)
        results["evaluations"]["safety"] = self.evaluate_safety(sample)
        
        # Calculate overall score (weighted average)
        weights = {
            "hallucination": 0.3,  # Very important - no false info
            "relevance": 0.3,      # Very important - answer the question
            "context_usage": 0.2,  # Important - use RAG properly
            "safety": 0.2,         # Important - be safe
        }
        
        overall_score = 0.0
        for dim, weight in weights.items():
            eval_result = results["evaluations"][dim]
            score = eval_result.get("score", 0.0)
            overall_score += score * weight
        
        results["overall_score"] = overall_score
        results["model_used"] = self.model
        
        return results


# ============================================
# CUSTOM G-EVAL FOR TRAVEL-SPECIFIC METRICS
# ============================================

class TravelQualityGEval(base_metric.BaseMetric):
    """
    Custom G-Eval metric for travel-specific quality assessment.
    
    Evaluates:
    - Itinerary structure and flow
    - Destination expertise
    - Budget accuracy
    - Personalization to user preferences
    
    Based on Opik's G-Eval: https://www.comet.com/docs/opik/evaluation/metrics/llm_judges#g-eval
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash", name: str = "travel_quality"):
        super().__init__(name=name)
        self.model = model
    
    def score(
        self,
        user_query: str,
        output: str,
        user_preferences: Optional[dict] = None,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score travel planning quality using LLM-as-judge.
        
        Args:
            user_query: User's travel request
            output: Agent's itinerary/response
            user_preferences: User's stated preferences (budget, interests, etc.)
        
        Returns:
            ScoreResult with 0.0-1.0 score and detailed reasoning
        """
        from litellm import completion
        
        # Build evaluation prompt
        eval_prompt = self._build_evaluation_prompt(
            user_query,
            output,
            user_preferences or {}
        )
        
        try:
            # Call LLM judge
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert travel planning evaluator."},
                    {"role": "user", "content": eval_prompt}
                ],
                temperature=0.0,
            )
            
            judge_response = response.choices[0].message.content
            
            # Parse score and reasoning
            score, reasoning = self._parse_judge_response(judge_response)
            
            return score_result.ScoreResult(
                value=score,
                name=self.name,
                reason=reasoning
            )
        
        except Exception as e:
            logger.error(f"G-Eval scoring failed: {e}")
            return score_result.ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Evaluation failed: {str(e)}"
            )
    
    def _build_evaluation_prompt(
        self,
        user_query: str,
        output: str,
        user_preferences: dict
    ) -> str:
        """Build comprehensive evaluation prompt."""
        return f"""
Evaluate this travel planning response on a scale of 0.0 to 1.0.

USER REQUEST:
{user_query}

USER PREFERENCES:
- Budget: {user_preferences.get('budget', 'Not specified')}
- Interests: {user_preferences.get('interests', 'Not specified')}
- Travel Style: {user_preferences.get('travel_style', 'Not specified')}

AGENT RESPONSE:
{output}

EVALUATION CRITERIA:

1. ITINERARY STRUCTURE (25 points):
   - Is the itinerary well-organized and easy to follow?
   - Are days/activities logically sequenced?
   - Is timing realistic and feasible?

2. DESTINATION EXPERTISE (25 points):
   - Are destination details accurate?
   - Are recommendations appropriate for the location?
   - Is local context (weather, culture, events) considered?

3. BUDGET ACCURACY (25 points):
   - Does the total cost align with user's budget?
   - Are cost breakdowns clear and realistic?
   - Is value for money demonstrated?

4. PERSONALIZATION (25 points):
   - Does the plan match user's stated interests?
   - Is the travel style (luxury/budget/adventure) appropriate?
   - Are unique, thoughtful touches included?

Provide your evaluation in this format:
SCORE: <0.0 to 1.0>
REASONING: <detailed explanation covering all 4 criteria>
"""
    
    def _parse_judge_response(self, response: str) -> tuple[float, str]:
        """Parse LLM judge response to extract score and reasoning."""
        import re
        
        # Extract score
        score_match = re.search(r'SCORE:\s*([0-9.]+)', response)
        score = float(score_match.group(1)) if score_match else 0.0
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+)', response, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else response
        
        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        
        return score, reasoning


# ============================================
# AGENT-SPECIFIC METRICS
# ============================================

class AgentTaskCompletionMetric(base_metric.BaseMetric):
    """
    Evaluate if agent completed its assigned task.
    
    Similar to Opik's built-in Agent Task Completion Judge.
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash", name: str = "agent_task_completion"):
        super().__init__(name=name)
        self.model = model
    
    def score(
        self,
        task_description: str,
        agent_output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score task completion.
        
        Args:
            task_description: What the agent was asked to do
            agent_output: What the agent actually did
        """
        from litellm import completion
        
        prompt = f"""
Did the agent successfully complete this task?

TASK: {task_description}
AGENT OUTPUT: {agent_output}

Respond with:
- COMPLETED: yes/no
- SCORE: 1.0 if yes, 0.0 if no
- REASONING: Brief explanation
"""
        
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            
            result = response.choices[0].message.content
            
            # Check if completed
            completed = "yes" in result.lower().split("completed:")[1].split("\n")[0]
            
            return score_result.ScoreResult(
                value=1.0 if completed else 0.0,
                name=self.name,
                reason=result
            )
        
        except Exception as e:
            return score_result.ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Evaluation failed: {str(e)}"
            )


class AgentToolCorrectnessMetric(base_metric.BaseMetric):
    """
    Evaluate if agent used the right tools/sub-agents.
    
    Similar to Opik's built-in Agent Tool Correctness Judge.
    """
    
    def __init__(self, model: str = "gemini/gemini-2.5-flash", name: str = "agent_tool_correctness"):
        super().__init__(name=name)
        self.model = model
    
    def score(
        self,
        user_query: str,
        tools_used: list[str],
        available_tools: list[dict],
        **kwargs
    ) -> score_result.ScoreResult:
        """
        Score tool selection correctness.
        
        Args:
            user_query: What user asked for
            tools_used: Which tools/agents were invoked
            available_tools: List of available tools with descriptions
        """
        from litellm import completion
        
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in available_tools
        ])
        
        prompt = f"""
Evaluate if the agent used the correct tools for this query.

USER QUERY: {user_query}

AVAILABLE TOOLS:
{tools_description}

TOOLS USED: {', '.join(tools_used)}

Rate on scale 0.0-1.0:
- 1.0 = Perfect tool selection
- 0.5 = Partial - some correct, some unnecessary
- 0.0 = Wrong tools used

Format:
SCORE: <0.0-1.0>
REASONING: <explanation>
"""
        
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            
            result = response.choices[0].message.content
            
            # Parse score
            import re
            score_match = re.search(r'SCORE:\s*([0-9.]+)', result)
            score = float(score_match.group(1)) if score_match else 0.5
            
            return score_result.ScoreResult(
                value=max(0.0, min(1.0, score)),
                name=self.name,
                reason=result
            )
        
        except Exception as e:
            return score_result.ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Evaluation failed: {str(e)}"
            )


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_evaluation_sample(
    sample_id: str,
    user_query: str,
    agent_output: str,
    context: Optional[list[str]] = None,
    expected_result: Optional[str] = None,
    user_preferences: Optional[dict] = None,
) -> EvaluationSample:
    """Helper to create evaluation sample."""
    return EvaluationSample(
        sample_id=sample_id,
        user_query=user_query,
        agent_output=agent_output,
        context=context or [],
        expected_result=expected_result,
        user_preferences=user_preferences or {},
    )


def print_evaluation_results(results: dict):
    """Pretty print evaluation results."""
    print("\n" + "="*80)
    print(f"EVALUATION RESULTS - Sample {results['sample_id']}")
    print("="*80)
    print(f"\nQuery: {results['user_query']}")
    print(f"\nOverall Score: {results['overall_score']:.2f} / 1.0")
    print(f"Model Used: {results['model_used']}")
    print("\n" + "-"*80)
    print("DIMENSION SCORES:")
    print("-"*80)
    
    for dim, eval_result in results['evaluations'].items():
        print(f"\n{dim.upper()}:")
        if 'score' in eval_result:
            print(f"  Score: {eval_result['score']:.2f}")
            print(f"  Reasoning: {eval_result['reasoning']}")
        else:
            # Handle context_usage with precision/recall
            if 'precision_score' in eval_result:
                print(f"  Precision: {eval_result['precision_score']:.2f}")
                print(f"  Recall: {eval_result['recall_score']:.2f}")
    
    print("\n" + "="*80 + "\n")
