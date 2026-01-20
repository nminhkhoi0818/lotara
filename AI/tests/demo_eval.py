import asyncio
from travel_lotara.core.eval.judges import WorkflowJudge, SafetyJudge
from travel_lotara.tracking.opik_tracker import get_opik_manager

async def evaluation_demo():
    print("🎯 EVALUATION DEMO - LLM as Judge\n")
    
    # Sample workflow output
    input_ctx = {
        "trace_id": "demo_trace_001",
        "user_request": "Plan 7-day Tokyo trip, $3000, love food",
        "agents_used": ["flight_agent", "hotel_agent", "activity_agent", "cost_agent"],
        "budget_limit": 3000.0
    }
    
    output = {
        "execution_plan": {
            "tasks": [
                {"id": "flight_search", "agent": "flight_agent"},
                {"id": "hotel_search", "agent": "hotel_agent"},
                {"id": "activities", "agent": "activity_agent"},
                {"id": "budget", "agent": "cost_agent"}
            ]
        },
        "result": {
            "flights": {"price": 947, "airline": "JAL"},
            "hotels": {"price": 840, "name": "Shinjuku Hotel"},
            "activities": {"count": 8, "focus": "food, temples"},
            "total_cost": 2847
        },
        "budget_used": 2847,
        "confidence": 0.94
    }
    
    # Evaluate with WorkflowJudge
    print("Running WorkflowJudge...")
    workflow_judge = WorkflowJudge()
    workflow_result = await workflow_judge.evaluate(input_ctx, output)
    
    print(f"✅ Workflow Score: {workflow_result.score:.1%}")
    print(f"   Reasoning: {workflow_result.reasoning}\n")
    
    # Evaluate with SafetyJudge
    print("Running SafetyJudge...")
    safety_judge = SafetyJudge()
    safety_result = await safety_judge.evaluate(input_ctx, output)
    
    print(f"✅ Safety Score: {safety_result.score:.1%}")
    print(f"   Reasoning: {safety_result.reasoning}\n")
    
    # Log to Opik
    opik = get_opik_manager()
    opik.log_judge_score(
        trace_id="demo_trace_001",
        dimension="workflow_quality",
        score=workflow_result.score,
        reasoning=workflow_result.reasoning
    )
    
    print(f"📊 Scores logged to Opik: {opik.get_trace_url()}")

if __name__ == "__main__":
    asyncio.run(evaluation_demo())

    # uv run AI/tests/demo_eval.py
    