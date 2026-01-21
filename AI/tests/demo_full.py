import asyncio
from datetime import datetime
from src.travel_lotara.core.orchestrator.mother_agent import MotherAgent, WorkflowContext, PlanningMode
from src.travel_lotara.tracking.opik_tracker import get_opik_manager
from src.travel_lotara.tools.api_tools import APITools
from src.travel_lotara.tools.rag_engine import RAGEngine

async def full_workflow_demo():
    print("=" * 60)
    print("🌍 TRAVEL LOTARA - FULL AI AGENT WORKFLOW DEMO")
    print("=" * 60)
    print()
    
    # Initialize Opik tracking
    opik = get_opik_manager()
    print(f"📊 Opik Dashboard: {opik.get_trace_url()}")
    print()
    
    # User request
    user_query = "Plan a 7-day trip to Tokyo for $3000. I love food and temples. Traveling in March 2026."
    print(f"👤 User Request: {user_query}")
    print()
    
    # Initialize Mother Agent
    print("🤖 Initializing Mother Agent...")
    api_tools = APITools()
    rag_engine = RAGEngine()
    mother_agent = MotherAgent(api_tools=api_tools, rag_engine=rag_engine)
    
    # Create workflow context
    context = WorkflowContext(
        user_id="demo_user_001",
        session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        user_query=user_query,
        planning_mode=PlanningMode.REACTIVE,
        budget_limit_usd=3000.0,
        budget_limit_tokens=100000
    )
    
    print("✅ Mother Agent initialized")
    print(f"   Mode: {context.planning_mode.value}")
    print(f"   Budget: ${context.budget_limit_usd}")
    print()
    
    # Execute workflow
    print("🚀 Starting workflow execution...")
    print("-" * 60)
    
    try:
        result = await mother_agent.run(context)
        
        print()
        print("=" * 60)
        print("✅ WORKFLOW COMPLETE!")
        print("=" * 60)
        print()
        
        # Display results
        print(f"📋 Final State: {result.final_state.value}")
        print(f"📊 Success: {result.success}")
        print(f"💰 Budget Used: ${result.budget_used_usd:.2f} / ${context.budget_limit_usd}")
        print(f"🎯 Confidence: {result.confidence:.1%}")
        print()
        
        if result.plan:
            print(f"📝 Generated Plan:")
            print(f"   Tasks: {len(result.plan.tasks)}")
            print(f"   Total Estimated Cost: ${result.plan.total_estimated_cost_usd:.2f}")
            print()
            
            print("   Task Breakdown:")
            for task in result.plan.tasks:
                print(f"   - {task.agent}: {task.id}")
        
        if result.execution_summary:
            print()
            print("📈 Execution Summary:")
            for key, value in result.execution_summary.items():
                print(f"   {key}: {value}")
        
        print()
        print(f"📊 View detailed trace: {opik.get_trace_url()}")
        
    except Exception as e:
        print()
        print(f"❌ Error during workflow: {str(e)}")
        print(f"   Check logs for details")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("Demo complete! Check Opik dashboard for full trace.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(full_workflow_demo())

    # uv run AI/tests/demo_full.py
    