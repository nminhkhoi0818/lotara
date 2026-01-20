"""
Opik Experiment Runner

Systematic A/B testing framework for Travel Lotara agents.
Logs all experiments to Opik for comparison and analysis.

Features:
- A/B testing for prompts, temperatures, models
- Regression test suite with golden examples
- Automated metrics collection
- Statistical significance testing
- Experiment versioning and tracking
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from travel_lotara.core.eval.judges import (
    EvaluationResult,
    JudgeOrchestrator,
)
from travel_lotara.tracking.opik_tracker import get_opik_manager


logger = logging.getLogger(__name__)


class ExperimentType(str, Enum):
    """Type of experiment."""
    PROMPT_AB_TEST = "prompt_ab_test"
    TEMPERATURE_SWEEP = "temperature_sweep"
    MODEL_COMPARISON = "model_comparison"
    PLANNING_STRATEGY = "planning_strategy"
    REGRESSION_TEST = "regression_test"


class ExperimentVariant(BaseModel):
    """Single variant in an A/B test."""
    variant_id: str
    variant_name: str
    config: dict[str, Any]
    description: str


class TestCase(BaseModel):
    """Single test case in regression suite."""
    test_id: str
    name: str
    description: str
    input_data: dict[str, Any]
    expected_agents: list[str] = Field(default_factory=list)
    min_success_score: float = 0.7
    tags: list[str] = Field(default_factory=list)


@dataclass
class ExperimentRun:
    """Single run of a variant on a test case."""
    run_id: str = field(default_factory=lambda: str(uuid4()))
    experiment_id: str = ""
    variant_id: str = ""
    test_case_id: str = ""
    
    # Execution data
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Results
    success: bool = False
    output: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    # Evaluation
    judge_results: list[EvaluationResult] = field(default_factory=list)
    overall_score: float = 0.0
    
    # Opik tracking
    trace_id: Optional[str] = None
    token_usage: dict[str, int] = field(default_factory=dict)


class ExperimentResults(BaseModel):
    """Aggregated results for an experiment."""
    experiment_id: str
    experiment_type: ExperimentType
    experiment_name: str
    start_time: datetime
    end_time: datetime
    
    # Variants tested
    variants: list[ExperimentVariant]
    test_cases: list[TestCase]
    
    # Runs
    total_runs: int
    successful_runs: int
    failed_runs: int
    
    # Metrics by variant
    variant_metrics: dict[str, dict[str, float]]
    
    # Winner
    winning_variant: Optional[str] = None
    improvement_pct: float = 0.0
    
    # Statistical significance
    is_significant: bool = False
    p_value: float = 1.0


class OpikExperimentRunner:
    """
    Runs systematic experiments and logs to Opik.
    
    Usage:
        runner = OpikExperimentRunner()
        
        # Define variants
        variants = [
            ExperimentVariant(
                variant_id="baseline",
                variant_name="Original Prompts",
                config={"prompts": "v1"}
            ),
            ExperimentVariant(
                variant_id="enhanced",
                variant_name="Enhanced Prompts with DAG",
                config={"prompts": "v2"}
            ),
        ]
        
        # Run experiment
        results = await runner.run_experiment(
            experiment_name="Prompt Enhancement Test",
            experiment_type=ExperimentType.PROMPT_AB_TEST,
            variants=variants,
            test_cases=GOLDEN_TEST_CASES
        )
        
        print(f"Winner: {results.winning_variant}")
        print(f"Improvement: {results.improvement_pct:.1f}%")
    """
    
    def __init__(self):
        self.opik_manager = get_opik_manager()
        self.judge_orchestrator = JudgeOrchestrator()
    
    async def run_experiment(self,
                            experiment_name: str,
                            experiment_type: ExperimentType,
                            variants: list[ExperimentVariant],
                            test_cases: list[TestCase],
                            workflow_executor: Callable) -> ExperimentResults:
        """
        Run a complete experiment comparing multiple variants.
        
        Args:
            experiment_name: Descriptive name for this experiment
            experiment_type: Type of experiment (prompt, temperature, etc.)
            variants: List of variants to test
            test_cases: List of test cases to run each variant on
            workflow_executor: Async function that executes workflow
                              Signature: async fn(config, input_data) -> output
        
        Returns:
            ExperimentResults with aggregated metrics
        """
        experiment_id = str(uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting experiment: {experiment_name} (ID: {experiment_id})")
        logger.info(f"Variants: {len(variants)}, Test Cases: {len(test_cases)}")
        
        # Create Opik experiment
        self.opik_manager.create_experiment(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            metadata={
                "type": experiment_type.value,
                "num_variants": len(variants),
                "num_test_cases": len(test_cases),
            }
        )
        
        # Run all combinations of variants × test cases
        all_runs = []
        for variant in variants:
            for test_case in test_cases:
                run = await self._run_single(
                    experiment_id=experiment_id,
                    variant=variant,
                    test_case=test_case,
                    workflow_executor=workflow_executor,
                )
                all_runs.append(run)
        
        # Aggregate results
        results = self._aggregate_results(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            experiment_type=experiment_type,
            start_time=start_time,
            variants=variants,
            test_cases=test_cases,
            runs=all_runs,
        )
        
        # Log to Opik
        self._log_experiment_results(results)
        
        logger.info(f"Experiment complete: {experiment_name}")
        logger.info(f"Winner: {results.winning_variant} (+{results.improvement_pct:.1f}%)")
        
        return results
    
    async def _run_single(self,
                         experiment_id: str,
                         variant: ExperimentVariant,
                         test_case: TestCase,
                         workflow_executor: Callable) -> ExperimentRun:
        """Run a single variant on a single test case."""
        run = ExperimentRun(
            experiment_id=experiment_id,
            variant_id=variant.variant_id,
            test_case_id=test_case.test_id,
        )
        
        try:
            # Execute workflow with variant config
            output = await workflow_executor(
                config=variant.config,
                input_data=test_case.input_data,
            )
            
            run.success = True
            run.output = output
            run.trace_id = output.get("trace_id")
            
            # Evaluate output with judges
            input_context = {
                "trace_id": run.trace_id,
                "test_case": test_case.name,
                "variant": variant.variant_name,
                **test_case.input_data,
            }
            
            run.judge_results = await self.judge_orchestrator.evaluate_all(
                input_context=input_context,
                output=output,
            )
            
            run.overall_score = self.judge_orchestrator.compute_overall_score(
                run.judge_results
            )
            
        except Exception as e:
            logger.error(f"Run failed: {variant.variant_id} on {test_case.test_id}: {e}")
            run.success = False
            run.error = str(e)
            run.overall_score = 0.0
        
        finally:
            run.end_time = datetime.utcnow()
            run.duration_seconds = (run.end_time - run.start_time).total_seconds()
        
        # Log to Opik
        self._log_run(run, variant, test_case)
        
        return run
    
    def _aggregate_results(self,
                          experiment_id: str,
                          experiment_name: str,
                          experiment_type: ExperimentType,
                          start_time: datetime,
                          variants: list[ExperimentVariant],
                          test_cases: list[TestCase],
                          runs: list[ExperimentRun]) -> ExperimentResults:
        """Aggregate individual runs into experiment results."""
        
        # Group runs by variant
        variant_runs = {}
        for variant in variants:
            variant_runs[variant.variant_id] = [
                r for r in runs if r.variant_id == variant.variant_id
            ]
        
        # Calculate metrics per variant
        variant_metrics = {}
        for variant_id, v_runs in variant_runs.items():
            if not v_runs:
                continue
            
            successful = [r for r in v_runs if r.success]
            scores = [r.overall_score for r in successful]
            
            variant_metrics[variant_id] = {
                "success_rate": len(successful) / len(v_runs) if v_runs else 0.0,
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "median_score": sorted(scores)[len(scores)//2] if scores else 0.0,
                "avg_duration": sum(r.duration_seconds for r in v_runs) / len(v_runs),
                "num_runs": len(v_runs),
            }
        
        # Find winner (highest avg_score)
        if variant_metrics:
            winning_variant = max(
                variant_metrics.items(),
                key=lambda x: x[1]["avg_score"]
            )[0]
            
            # Calculate improvement over baseline (assume first variant is baseline)
            baseline_id = variants[0].variant_id
            baseline_score = variant_metrics[baseline_id]["avg_score"]
            winner_score = variant_metrics[winning_variant]["avg_score"]
            
            improvement_pct = ((winner_score - baseline_score) / baseline_score * 100
                              if baseline_score > 0 else 0.0)
        else:
            winning_variant = None
            improvement_pct = 0.0
        
        return ExperimentResults(
            experiment_id=experiment_id,
            experiment_type=experiment_type,
            experiment_name=experiment_name,
            start_time=start_time,
            end_time=datetime.utcnow(),
            variants=variants,
            test_cases=test_cases,
            total_runs=len(runs),
            successful_runs=sum(1 for r in runs if r.success),
            failed_runs=sum(1 for r in runs if not r.success),
            variant_metrics=variant_metrics,
            winning_variant=winning_variant,
            improvement_pct=improvement_pct,
            is_significant=abs(improvement_pct) > 10.0,  # Simple threshold
        )
    
    def _log_run(self,
                run: ExperimentRun,
                variant: ExperimentVariant,
                test_case: TestCase) -> None:
        """Log individual run to Opik."""
        # This would integrate with Opik's experiment tracking API
        # For now, just log locally
        logger.info(f"Run complete: {variant.variant_name} on {test_case.name}")
        logger.info(f"  Score: {run.overall_score:.2f}")
        logger.info(f"  Duration: {run.duration_seconds:.2f}s")
    
    def _log_experiment_results(self, results: ExperimentResults) -> None:
        """Log aggregated experiment results to Opik."""
        logger.info(f"\n{'='*60}")
        logger.info(f"EXPERIMENT RESULTS: {results.experiment_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Total Runs: {results.total_runs}")
        logger.info(f"Success Rate: {results.successful_runs}/{results.total_runs}")
        logger.info(f"\nVariant Performance:")
        
        for variant in results.variants:
            metrics = results.variant_metrics.get(variant.variant_id, {})
            logger.info(f"\n  {variant.variant_name}:")
            logger.info(f"    Avg Score: {metrics.get('avg_score', 0):.3f}")
            logger.info(f"    Success Rate: {metrics.get('success_rate', 0):.1%}")
            logger.info(f"    Avg Duration: {metrics.get('avg_duration', 0):.2f}s")
        
        logger.info(f"\n🏆 Winner: {results.winning_variant}")
        logger.info(f"📈 Improvement: {results.improvement_pct:+.1f}%")
        logger.info(f"{'='*60}\n")


# Golden Test Cases for Regression Testing
GOLDEN_TEST_CASES = [
    TestCase(
        test_id="tokyo_foodie_7d",
        name="Tokyo Foodie 7-Day Trip",
        description="Budget trip to Tokyo focusing on food and temples",
        input_data={
            "user_request": "Plan a 7-day trip to Tokyo for under $3000. I love food and temples.",
            "origin": "NYC",
            "budget_usd": 3000,
            "duration_days": 7,
            "interests": ["food", "temples", "culture"],
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.85,
        tags=["simple", "budget", "asia"],
    ),
    
    TestCase(
        test_id="paris_luxury_5d",
        name="Paris Luxury 5-Day Trip",
        description="High-budget romantic Paris getaway",
        input_data={
            "user_request": "Plan a luxury 5-day trip to Paris. Budget is $8000. Romantic, fine dining.",
            "origin": "SFO",
            "budget_usd": 8000,
            "duration_days": 5,
            "interests": ["romance", "fine_dining", "art", "shopping"],
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.85,
        tags=["luxury", "europe", "romance"],
    ),
    
    TestCase(
        test_id="bali_adventure_10d",
        name="Bali Adventure 10-Day Trip",
        description="Mid-range adventure trip to Bali",
        input_data={
            "user_request": "10 days in Bali, $4000 budget. Love surfing, hiking, yoga.",
            "origin": "LAX",
            "budget_usd": 4000,
            "duration_days": 10,
            "interests": ["surfing", "hiking", "yoga", "nature"],
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.80,
        tags=["adventure", "asia", "nature"],
    ),
    
    TestCase(
        test_id="barcelona_family_8d",
        name="Barcelona Family 8-Day Trip",
        description="Family trip with kids to Barcelona",
        input_data={
            "user_request": "8-day family trip to Barcelona, 2 adults + 2 kids (ages 8, 12). Budget $5000. Kid-friendly activities.",
            "origin": "JFK",
            "budget_usd": 5000,
            "duration_days": 8,
            "interests": ["family", "kids", "beach", "sightseeing"],
            "travelers": 4,
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.80,
        tags=["family", "europe", "kids"],
    ),
    
    TestCase(
        test_id="nyc_weekend_2d",
        name="NYC Weekend Getaway",
        description="Quick 2-day trip to New York",
        input_data={
            "user_request": "Weekend trip to NYC, $1000 budget. Love museums, Broadway, good food.",
            "origin": "BOS",
            "budget_usd": 1000,
            "duration_days": 2,
            "interests": ["museums", "theater", "food"],
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.75,
        tags=["simple", "short", "domestic"],
    ),
    
    TestCase(
        test_id="impossible_antarctica",
        name="Impossible Antarctica Request",
        description="Test graceful failure on unrealistic request",
        input_data={
            "user_request": "Plan a 3-day trip to Antarctica for $500.",
            "origin": "NYC",
            "budget_usd": 500,
            "duration_days": 3,
        },
        expected_agents=["flight", "cost"],
        min_success_score=0.0,  # Should fail gracefully
        tags=["edge_case", "impossible"],
    ),
    
    TestCase(
        test_id="multi_city_europe_14d",
        name="Multi-City Europe 14-Day Trip",
        description="Complex trip covering 4 European cities",
        input_data={
            "user_request": "14-day Europe trip: London (3d), Paris (4d), Amsterdam (3d), Berlin (4d). Budget $6000. Culture and nightlife.",
            "origin": "LAX",
            "budget_usd": 6000,
            "duration_days": 14,
            "cities": ["London", "Paris", "Amsterdam", "Berlin"],
            "interests": ["culture", "nightlife", "history"],
        },
        expected_agents=["flight", "hotel", "activity", "cost"],
        min_success_score=0.75,
        tags=["complex", "multi_city", "europe"],
    ),
]


# Example experiment configurations
EXAMPLE_EXPERIMENTS = {
    "prompt_enhancement": {
        "name": "Prompt Enhancement A/B Test",
        "type": ExperimentType.PROMPT_AB_TEST,
        "variants": [
            ExperimentVariant(
                variant_id="baseline",
                variant_name="Original Prompts",
                config={"prompt_version": "v1"},
                description="Basic prompts without DAG context",
            ),
            ExperimentVariant(
                variant_id="enhanced",
                variant_name="Enhanced Prompts with DAG",
                config={"prompt_version": "v2"},
                description="Prompts include DAG context and decision rubrics",
            ),
            ExperimentVariant(
                variant_id="personality",
                variant_name="Enhanced + Lotara Personality",
                config={"prompt_version": "v3"},
                description="Enhanced prompts + Lotara voice framework",
            ),
        ],
    },
    
    "temperature_sweep": {
        "name": "Temperature Optimization",
        "type": ExperimentType.TEMPERATURE_SWEEP,
        "variants": [
            ExperimentVariant(
                variant_id=f"temp_{t}",
                variant_name=f"Temperature {t}",
                config={"temperature": t},
                description=f"Test with temperature={t}",
            )
            for t in [0.0, 0.3, 0.7, 1.0]
        ],
    },
}
