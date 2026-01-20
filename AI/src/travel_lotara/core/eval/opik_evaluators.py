"""
Opik Evaluation Framework for Travel Lotara

LLM-as-Judge evaluators integrated with Opik for systematic quality assessment.
This is the key component for the "Best Use of Opik" hackathon prize.

Features:
- Multiple specialized judges (workflow, safety, agent-level)
- Automatic logging to Opik with structured metrics
- Scoring across multiple dimensions
- Support for A/B experiments
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field

import opik
from opik import track, opik_context
from opik.evaluation import evaluate
from opik.evaluation.metrics import base_metric, score_result

logger = logging.getLogger(__name__)


# ============================================
# EVALUATION DIMENSIONS
# ============================================

class EvalDimension(str, Enum):
    """Dimensions for agent evaluation."""
    SUCCESS = "success"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    SAFETY = "safety"
    BUDGET_ADHERENCE = "budget_adherence"
    TOOL_SELECTION = "tool_selection"
    EFFICIENCY = "efficiency"
    CREATIVITY = "creativity"
    USER_SATISFACTION = "user_satisfaction"


@dataclass
class EvalResult:
    """Result from an evaluation."""
    dimension: EvalDimension
    score: float  # 0.0 to 1.0
    reasoning: str
    criteria: dict[str, bool]
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================
# OPIK CUSTOM METRICS
# ============================================

class WorkflowSuccessMetric(base_metric.BaseMetric):
    """
    Opik metric for evaluating workflow success.
    
    Evaluates:
    - Did the agent complete the user's request?
    - Were appropriate tools/sub-agents used?
    - Is the output complete and actionable?
    """
    
    def __init__(self, name: str = "workflow_success"):
        super().__init__(name=name)
    
    def score(self, output: str, expected: Optional[str] = None, **kwargs) -> score_result.ScoreResult:
        """Score the workflow output."""
        # Simple heuristic scoring - in production use LLM-as-judge
        score = 0.0
        reason_parts = []
        
        if not output:
            return score_result.ScoreResult(value=0.0, name=self.name, reason="Empty output")
        
        # Check for key travel planning elements
        output_lower = output.lower()
        
        if any(word in output_lower for word in ["flight", "fly", "airline"]):
            score += 0.2
            reason_parts.append("✓ Flight info present")
        
        if any(word in output_lower for word in ["hotel", "accommodation", "stay"]):
            score += 0.2
            reason_parts.append("✓ Hotel info present")
        
        if any(word in output_lower for word in ["activity", "attraction", "visit", "see"]):
            score += 0.2
            reason_parts.append("✓ Activities present")
        
        if any(word in output_lower for word in ["$", "cost", "budget", "price"]):
            score += 0.2
            reason_parts.append("✓ Budget info present")
        
        if any(word in output_lower for word in ["visa", "passport", "document"]):
            score += 0.1
            reason_parts.append("✓ Travel docs mentioned")
        
        # Length check (reasonable response)
        if len(output) > 200:
            score += 0.1
            reason_parts.append("✓ Detailed response")
        
        return score_result.ScoreResult(
            value=min(score, 1.0),
            name=self.name,
            reason=" | ".join(reason_parts) if reason_parts else "Incomplete response"
        )


class SafetyMetric(base_metric.BaseMetric):
    """
    Opik metric for evaluating response safety.
    
    Checks for:
    - Hallucination indicators
    - Missing sources for factual claims
    - Potentially harmful content
    """
    
    def __init__(self, name: str = "safety"):
        super().__init__(name=name)
    
    def score(self, output: str, **kwargs) -> score_result.ScoreResult:
        """Score the safety of the output."""
        if not output:
            return score_result.ScoreResult(value=1.0, name=self.name, reason="Empty output - safe by default")
        
        issues = []
        score = 1.0
        output_lower = output.lower()
        
        # Check for hallucination indicators
        hallucination_phrases = [
            "i believe", "i think", "probably", "might be",
            "i'm not sure", "i don't have access to",
        ]
        for phrase in hallucination_phrases:
            if phrase in output_lower:
                score -= 0.1
                issues.append(f"Uncertainty indicator: '{phrase}'")
        
        # Check for missing attribution
        if "source" not in output_lower and "according to" not in output_lower:
            if any(word in output_lower for word in ["always", "never", "guaranteed", "definitely"]):
                score -= 0.15
                issues.append("Strong claims without attribution")
        
        # Check for sensitive content
        sensitive_terms = ["credit card", "ssn", "social security", "password"]
        for term in sensitive_terms:
            if term in output_lower:
                score -= 0.3
                issues.append(f"Sensitive content: {term}")
        
        score = max(0.0, score)
        reason = " | ".join(issues) if issues else "✓ No safety issues detected"
        
        return score_result.ScoreResult(value=score, name=self.name, reason=reason)


class ToolSelectionMetric(base_metric.BaseMetric):
    """
    Opik metric for evaluating tool/agent selection accuracy.
    
    Checks if the right specialist agents were invoked for the task.
    """
    
    def __init__(self, name: str = "tool_selection"):
        super().__init__(name=name)
    
    def score(self, output: str, expected_tools: Optional[list] = None, **kwargs) -> score_result.ScoreResult:
        """Score tool selection accuracy."""
        if not expected_tools:
            return score_result.ScoreResult(value=0.5, name=self.name, reason="No expected tools specified")
        
        output_lower = output.lower()
        tools_found = []
        tools_missing = []
        
        tool_indicators = {
            "flight_agent": ["flight", "fly", "airline", "departure", "arrival"],
            "hotel_agent": ["hotel", "accommodation", "stay", "room", "booking"],
            "activity_agent": ["activity", "attraction", "tour", "visit", "experience"],
            "visa_agent": ["visa", "passport", "entry", "requirement", "document"],
            "destination_agent": ["destination", "city", "country", "weather", "culture"],
            "budget_agent": ["budget", "cost", "price", "expense", "total"],
        }
        
        for tool in expected_tools:
            indicators = tool_indicators.get(tool, [])
            if any(ind in output_lower for ind in indicators):
                tools_found.append(tool)
            else:
                tools_missing.append(tool)
        
        if not expected_tools:
            score = 0.5
        else:
            score = len(tools_found) / len(expected_tools)
        
        reason = f"Found: {tools_found}" if tools_found else "No expected tools found"
        if tools_missing:
            reason += f" | Missing: {tools_missing}"
        
        return score_result.ScoreResult(value=score, name=self.name, reason=reason)


class BudgetAdherenceMetric(base_metric.BaseMetric):
    """
    Opik metric for evaluating budget adherence.
    """
    
    def __init__(self, name: str = "budget_adherence"):
        super().__init__(name=name)
    
    def score(self, output: str, user_budget: Optional[float] = None, **kwargs) -> score_result.ScoreResult:
        """Score budget adherence."""
        import re
        
        if not user_budget:
            return score_result.ScoreResult(value=0.5, name=self.name, reason="No budget specified")
        
        # Extract costs from output
        cost_pattern = r'\$[\d,]+(?:\.\d{2})?'
        costs = re.findall(cost_pattern, output)
        
        if not costs:
            return score_result.ScoreResult(value=0.5, name=self.name, reason="No costs found in output")
        
        # Parse the largest cost (likely total)
        parsed_costs = []
        for cost in costs:
            try:
                parsed_costs.append(float(cost.replace('$', '').replace(',', '')))
            except:
                pass
        
        if not parsed_costs:
            return score_result.ScoreResult(value=0.5, name=self.name, reason="Could not parse costs")
        
        max_cost = max(parsed_costs)
        
        if max_cost <= user_budget:
            score = 1.0
            reason = f"✓ Within budget: ${max_cost:,.0f} <= ${user_budget:,.0f}"
        elif max_cost <= user_budget * 1.1:
            score = 0.8
            reason = f"Slightly over: ${max_cost:,.0f} (10% over ${user_budget:,.0f})"
        elif max_cost <= user_budget * 1.25:
            score = 0.5
            reason = f"Over budget: ${max_cost:,.0f} (25% over ${user_budget:,.0f})"
        else:
            score = 0.2
            reason = f"✗ Way over budget: ${max_cost:,.0f} >> ${user_budget:,.0f}"
        
        return score_result.ScoreResult(value=score, name=self.name, reason=reason)


# ============================================
# LLM-AS-JUDGE EVALUATOR
# ============================================

class LLMJudge:
    """
    LLM-as-Judge evaluator using the same model as agents.
    
    Provides detailed evaluation with reasoning.
    """
    
    def __init__(self, model: str = "gemini/gemini-2.0-flash"):
        self.model = model
    
    @track(name="llm_judge_evaluation")
    async def evaluate_workflow(
        self,
        user_request: str,
        agent_output: str,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Comprehensive workflow evaluation using LLM-as-judge.
        
        Returns scores across multiple dimensions.
        """
        from litellm import acompletion
        
        evaluation_prompt = f"""You are an expert travel planning evaluator. Evaluate this AI travel assistant's response.

USER REQUEST:
{user_request}

ASSISTANT RESPONSE:
{agent_output}

Evaluate on these dimensions (score 0.0 to 1.0):

1. SUCCESS: Did the assistant address the user's request completely?
2. RELEVANCE: Is all information relevant to the trip?
3. COMPLETENESS: Are all aspects covered (flights, hotels, activities, budget)?
4. ACCURACY: Does the information appear factually correct?
5. HELPFULNESS: Would a real user find this response useful?
6. SAFETY: Are there any concerning claims or missing sources?

Return ONLY valid JSON in this exact format:
{{
    "success": {{"score": 0.0, "reason": "explanation"}},
    "relevance": {{"score": 0.0, "reason": "explanation"}},
    "completeness": {{"score": 0.0, "reason": "explanation"}},
    "accuracy": {{"score": 0.0, "reason": "explanation"}},
    "helpfulness": {{"score": 0.0, "reason": "explanation"}},
    "safety": {{"score": 0.0, "reason": "explanation"}},
    "overall": {{"score": 0.0, "reason": "overall assessment"}}
}}"""

        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.0,  # Deterministic for evaluation
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            return json.loads(result_text.strip())
            
        except Exception as e:
            logger.error(f"LLM Judge evaluation failed: {e}")
            # Return default scores
            return {
                "success": {"score": 0.5, "reason": f"Evaluation failed: {e}"},
                "relevance": {"score": 0.5, "reason": "Could not evaluate"},
                "completeness": {"score": 0.5, "reason": "Could not evaluate"},
                "accuracy": {"score": 0.5, "reason": "Could not evaluate"},
                "helpfulness": {"score": 0.5, "reason": "Could not evaluate"},
                "safety": {"score": 0.5, "reason": "Could not evaluate"},
                "overall": {"score": 0.5, "reason": f"Evaluation error: {e}"},
            }


# ============================================
# EXPERIMENT RUNNER
# ============================================

@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""
    name: str
    description: str
    variants: list[dict]  # Different configs to test
    test_cases: list[dict]  # Test inputs


@dataclass
class ExperimentResult:
    """Result from running an experiment."""
    experiment_name: str
    variant_name: str
    test_case_id: str
    output: str
    metrics: dict[str, float]
    trace_id: Optional[str] = None
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class OpikExperimentRunner:
    """
    Runs systematic experiments with Opik tracking.
    
    Perfect for:
    - A/B testing prompts
    - Comparing model temperatures
    - Testing different agent configurations
    """
    
    def __init__(self, project_name: str = "lotara-experiments"):
        self.project_name = project_name
        self.metrics = [
            WorkflowSuccessMetric(),
            SafetyMetric(),
            ToolSelectionMetric(),
        ]
        self.llm_judge = LLMJudge()
    
    @track(name="experiment_run")
    async def run_single_test(
        self,
        agent_func,
        test_input: str,
        variant_config: dict,
        expected_tools: Optional[list] = None,
        user_budget: Optional[float] = None,
    ) -> ExperimentResult:
        """Run a single test case with tracking."""
        import time
        
        start_time = time.time()
        
        # Run the agent
        try:
            output = await agent_func(test_input, **variant_config)
            if hasattr(output, 'content'):
                output = str(output.content)
            output = str(output)
        except Exception as e:
            output = f"Error: {e}"
        
        duration = time.time() - start_time
        
        # Calculate metrics
        metrics = {}
        for metric in self.metrics:
            kwargs = {}
            if expected_tools:
                kwargs['expected_tools'] = expected_tools
            if user_budget:
                kwargs['user_budget'] = user_budget
            
            result = metric.score(output, **kwargs)
            metrics[result.name] = result.value
        
        # Get current trace ID if available
        trace_id = None
        try:
            trace_id = opik_context.get_current_trace_data().trace_id
        except:
            pass
        
        return ExperimentResult(
            experiment_name=variant_config.get('experiment_name', 'unnamed'),
            variant_name=variant_config.get('variant_name', 'default'),
            test_case_id=variant_config.get('test_case_id', 'unknown'),
            output=output,
            metrics=metrics,
            trace_id=trace_id,
            duration_seconds=duration,
        )
    
    async def run_experiment(
        self,
        experiment_config: ExperimentConfig,
        agent_func,
    ) -> list[ExperimentResult]:
        """
        Run a full experiment across all variants and test cases.
        
        Returns results for analysis and comparison.
        """
        results = []
        
        for variant in experiment_config.variants:
            for test_case in experiment_config.test_cases:
                config = {
                    **variant,
                    'experiment_name': experiment_config.name,
                    'variant_name': variant.get('name', 'unnamed'),
                    'test_case_id': test_case.get('id', 'unknown'),
                }
                
                result = await self.run_single_test(
                    agent_func=agent_func,
                    test_input=test_case['input'],
                    variant_config=config,
                    expected_tools=test_case.get('expected_tools'),
                    user_budget=test_case.get('budget'),
                )
                results.append(result)
        
        return results
    
    def summarize_results(self, results: list[ExperimentResult]) -> dict:
        """Summarize experiment results by variant."""
        from collections import defaultdict
        
        by_variant = defaultdict(list)
        for r in results:
            by_variant[r.variant_name].append(r)
        
        summary = {}
        for variant_name, variant_results in by_variant.items():
            metric_totals = defaultdict(list)
            for r in variant_results:
                for metric_name, value in r.metrics.items():
                    metric_totals[metric_name].append(value)
            
            summary[variant_name] = {
                "count": len(variant_results),
                "avg_duration": sum(r.duration_seconds for r in variant_results) / len(variant_results),
                "metrics": {
                    name: sum(values) / len(values)
                    for name, values in metric_totals.items()
                },
            }
        
        return summary


# ============================================
# GOLDEN TEST SUITE
# ============================================

GOLDEN_TEST_CASES = [
    {
        "id": "tokyo_foodie_7d",
        "input": "Plan a 7-day trip to Tokyo for under $3000. I love food and temples.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "budget_agent"],
        "budget": 3000,
        "tags": ["asia", "food", "culture"],
    },
    {
        "id": "paris_romantic_5d",
        "input": "5-day romantic Paris trip with my partner. Budget $4000, we love art museums.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "budget_agent"],
        "budget": 4000,
        "tags": ["europe", "romance", "art"],
    },
    {
        "id": "bali_beach_10d",
        "input": "10-day beach vacation in Bali. Budget $2500, looking for relaxation and surfing.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "visa_agent", "budget_agent"],
        "budget": 2500,
        "tags": ["asia", "beach", "adventure"],
    },
    {
        "id": "nyc_business_3d",
        "input": "Quick 3-day business trip to NYC. Need hotel near Times Square, budget $1500.",
        "expected_tools": ["flight_agent", "hotel_agent", "budget_agent"],
        "budget": 1500,
        "tags": ["business", "city", "short"],
    },
    {
        "id": "barcelona_family_7d",
        "input": "Family trip to Barcelona for 7 days with 2 kids. Budget $5000, need kid-friendly activities.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "budget_agent"],
        "budget": 5000,
        "tags": ["europe", "family", "culture"],
    },
    {
        "id": "iceland_adventure_5d",
        "input": "Adventure trip to Iceland for Northern Lights. 5 days, budget $3500.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "visa_agent", "budget_agent"],
        "budget": 3500,
        "tags": ["europe", "adventure", "nature"],
    },
    {
        "id": "thailand_backpacker",
        "input": "Backpacking through Thailand for 2 weeks on a tight budget of $1000.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "visa_agent", "budget_agent"],
        "budget": 1000,
        "tags": ["asia", "budget", "backpacking"],
    },
    {
        "id": "london_solo_4d",
        "input": "Solo trip to London for 4 days. Love history and pubs. Budget $2000.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "budget_agent"],
        "budget": 2000,
        "tags": ["europe", "solo", "history"],
    },
    {
        "id": "dubai_luxury_5d",
        "input": "Luxury trip to Dubai for 5 days. No budget limit, want the best experiences.",
        "expected_tools": ["flight_agent", "hotel_agent", "activity_agent", "visa_agent"],
        "budget": 20000,
        "tags": ["luxury", "middle-east"],
    },
    {
        "id": "japan_visa_check",
        "input": "Do I need a visa to visit Japan as a US citizen?",
        "expected_tools": ["visa_agent", "destination_agent"],
        "budget": None,
        "tags": ["visa", "simple"],
    },
]


def get_golden_test_suite() -> list[dict]:
    """Get the golden test suite for regression testing."""
    return GOLDEN_TEST_CASES


# ============================================
# CONVENIENCE EXPORTS
# ============================================

__all__ = [
    # Dimensions
    "EvalDimension",
    "EvalResult",
    # Metrics
    "WorkflowSuccessMetric",
    "SafetyMetric",
    "ToolSelectionMetric",
    "BudgetAdherenceMetric",
    # Evaluators
    "LLMJudge",
    # Experiment Runner
    "ExperimentConfig",
    "ExperimentResult",
    "OpikExperimentRunner",
    # Test Suite
    "GOLDEN_TEST_CASES",
    "get_golden_test_suite",
]
