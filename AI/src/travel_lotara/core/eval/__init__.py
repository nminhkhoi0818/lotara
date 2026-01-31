"""
Evaluation Framework for Travel Lotara

Provides LLM-as-Judge evaluation and Opik experiment tracking.
Key component for the "Best Use of Opik" hackathon prize.

Usage:
    from travel_lotara.core.eval import (
        OpikExperimentRunner,
        LLMJudge,
        WorkflowSuccessMetric,
        SafetyMetric,
        GOLDEN_TEST_CASES,
    )
    
    # Run evaluation
    runner = OpikExperimentRunner()
    results = await runner.run_experiment(config, agent_func)
    
    # LLM-as-Judge
    judge = LLMJudge()
    scores = await judge.evaluate_workflow(request, response)
"""

from src.travel_lotara.core.eval.opik_evaluators import (
    # Dimensions
    EvalDimension,
    EvalResult,
    # Metrics (Opik-compatible)
    WorkflowSuccessMetric,
    SafetyMetric,
    ToolSelectionMetric,
    BudgetAdherenceMetric,
    # Evaluators
    LLMJudge,
    # Experiment Runner
    ExperimentConfig,
    ExperimentResult,
    OpikExperimentRunner,
    # Test Suite
    GOLDEN_TEST_CASES,
    get_golden_test_suite,
)

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
