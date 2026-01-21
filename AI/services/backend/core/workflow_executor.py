"""
Workflow Executor for Travel Lotara Backend

Bridges FastAPI layer with MotherAgent.
Handles async execution, event emission, and error recovery.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from src.travel_lotara.core.orchestrator.mother_agent import (
    MotherAgent,
    WorkflowContext,
    WorkflowState as MAWorkflowState,
    PlanningMode,
)
from src.travel_lotara.agents.base_agent import AgentContext
from src.travel_lotara.agents.flight_agent.flight_agent import FlightAgent
from src.travel_lotara.agents.hotel_agent.hotel_agent import HotelAgent
from src.travel_lotara.agents.activity_agent.activity_agent import ActivityAgent
from src.travel_lotara.agents.cost_agent.cost_agent import CostAgent
from src.travel_lotara.tools.api_tools import APITools
from src.travel_lotara.tools.rag_engine import RAGEngine
from src.travel_lotara.tracking.opik_tracker import get_opik_manager, TraceLevel

from ..api.models import JobStatus, WorkflowMode, TaskInfo
from .job_manager import JobManager


logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Execute workflows and emit events to JobManager.
    
    Responsibilities:
    - Initialize MotherAgent
    - Execute workflows asynchronously
    - Emit progress events
    - Handle errors gracefully
    - Track execution in Opik
    """
    
    def __init__(self, job_manager: JobManager):
        """
        Initialize executor.
        
        Args:
            job_manager: Job state manager
        """
        self.job_manager = job_manager
        self.opik_manager = get_opik_manager()
        
        # Active workflows (job_id -> task)
        self._active_workflows: dict[str, asyncio.Task] = {}
    
    async def execute_reactive_workflow(
        self,
        job_id: str,
        user_id: str,
        query: str,
        constraints: dict[str, Any],
    ):
        """
        Execute reactive (user-triggered) workflow.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            query: User query
            constraints: User constraints
        """
        # Create background task
        task = asyncio.create_task(
            self._run_workflow(
                job_id=job_id,
                user_id=user_id,
                mode=WorkflowMode.REACTIVE,
                query=query,
                constraints=constraints,
            )
        )
        
        self._active_workflows[job_id] = task
        
        # Don't await - runs in background
    
    async def execute_proactive_workflow(
        self,
        job_id: str,
        user_id: str,
        trigger_type: str,
        trigger_context: dict[str, Any],
        constraints: Optional[dict[str, Any]] = None,
    ):
        """
        Execute proactive (system-triggered) workflow.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            trigger_type: What triggered this
            trigger_context: Trigger data
            constraints: User constraints
        """
        # Create background task
        task = asyncio.create_task(
            self._run_workflow(
                job_id=job_id,
                user_id=user_id,
                mode=WorkflowMode.PROACTIVE,
                query=f"Proactive suggestion: {trigger_type}",
                constraints=constraints or {},
                trigger_context=trigger_context,
            )
        )
        
        self._active_workflows[job_id] = task
    
    async def cancel_workflow(self, job_id: str):
        """
        Cancel running workflow.
        
        Args:
            job_id: Job identifier
        """
        task = self._active_workflows.get(job_id)
        if task:
            task.cancel()
            del self._active_workflows[job_id]
            
            await self.job_manager.update_job_status(
                job_id,
                JobStatus.CANCELLED,
            )
            
            logger.info(f"Cancelled workflow {job_id}")
    
    # ============================================
    # INTERNAL WORKFLOW EXECUTION
    # ============================================
    
    async def _run_workflow(
        self,
        job_id: str,
        user_id: str,
        mode: WorkflowMode,
        query: str,
        constraints: dict[str, Any],
        trigger_context: Optional[dict[str, Any]] = None,
    ):
        """
        Internal workflow runner.
        
        This is the core execution loop that:
        1. Initializes MotherAgent
        2. Executes workflow
        3. Emits events to JobManager
        4. Handles errors
        """
        # Start Opik trace
        trace_id = await self.opik_manager.start_trace(
            name=f"workflow_{mode.value}",
            input_data={"query": query, "constraints": constraints},
            metadata={
                "job_id": job_id,
                "user_id": user_id,
                "mode": mode.value,
            },
            tags=[mode.value, "workflow"],
        )
        
        try:
            # Update status
            await self.job_manager.update_job_status(job_id, JobStatus.PLANNING)
            
            # Get Opik trace URL
            trace_url = await self.opik_manager.get_trace_url(trace_id)
            await self.job_manager.set_opik_trace(job_id, trace_id, trace_url)
            
            # Initialize Mother Agent
            mother_agent = MotherAgent()
            
            # Initialize tools (shared across agents)
            api_tools = APITools()
            rag_engine = RAGEngine()
            
            # Register sub-agents
            mother_agent.register_sub_agent("flight_agent", FlightAgent(api_tools))
            mother_agent.register_sub_agent("hotel_agent", HotelAgent(api_tools))
            mother_agent.register_sub_agent("activity_agent", ActivityAgent(rag_engine))
            mother_agent.register_sub_agent("cost_agent", CostAgent())
            # Note: VisaAgent not registered yet - needs implementation
            
            logger.info(f"Registered {len(mother_agent.sub_agents)} sub-agents")
            
            # Create workflow context
            context = WorkflowContext(
                session_id=job_id,
                user_id=user_id,
                mode=PlanningMode.REACTIVE if mode == WorkflowMode.REACTIVE else PlanningMode.PROACTIVE,
                user_query=query,
                budget_usd=constraints.get("budget_usd", 1000.0),
                budget_tokens=constraints.get("budget_tokens", 100000),
                preferences=constraints,
            )
            
            # Execute workflow with event callbacks
            result = await self._execute_with_callbacks(
                mother_agent,
                context,
                job_id,
            )
            
            # Update with final result
            if result.success:
                await self.job_manager.set_final_result(
                    job_id,
                    result.final_plan.model_dump() if result.final_plan else {},
                )
            else:
                await self.job_manager.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error={
                        "message": "Workflow execution failed",
                        "details": result.metadata.get("error_details"),
                    }
                )
            
            # End Opik trace
            await self.opik_manager.end_trace(
                trace_id,
                output_data={"success": result.success},
                metadata=result.metadata,
            )
        
        except asyncio.CancelledError:
            logger.info(f"Workflow {job_id} was cancelled")
            raise
        
        except Exception as e:
            logger.error(f"Workflow {job_id} failed: {e}", exc_info=True)
            
            await self.job_manager.update_job_status(
                job_id,
                JobStatus.FAILED,
                error={
                    "message": str(e),
                    "type": type(e).__name__,
                }
            )
            
            # Log error to Opik
            await self.opik_manager.end_trace(
                trace_id,
                output_data={"success": False},
                metadata={"error": str(e)},
            )
        
        finally:
            # Cleanup
            if job_id in self._active_workflows:
                del self._active_workflows[job_id]
    
    async def _execute_with_callbacks(
        self,
        mother_agent: MotherAgent,
        context: WorkflowContext,
        job_id: str,
    ):
        """
        Execute MotherAgent with event callbacks.
        
        This wraps the MotherAgent execution to emit events
        as the workflow progresses.
        """
        # Update status
        await self.job_manager.update_job_status(job_id, JobStatus.EXECUTING)
        
        # Monkey-patch state transitions to emit events
        original_handle_state = mother_agent._handle_state
        
        async def wrapped_handle_state(context: WorkflowContext):
            # Emit state change
            await self.job_manager.update_workflow_state(
                job_id,
                context.current_state.value,
            )
            
            # Call original
            return await original_handle_state(context)
        
        mother_agent._handle_state = wrapped_handle_state
        
        # Monkey-patch agent execution to emit task events
        # (This is a simplified version - in production, you'd want
        # a proper observer pattern)
        
        # Execute workflow
        result = await mother_agent.run(context)
        
        return result
    
    # ============================================
    # UTILITIES
    # ============================================
    
    def get_active_jobs(self) -> list[str]:
        """Get list of active job IDs."""
        return list(self._active_workflows.keys())
    
    async def cleanup(self):
        """Cancel all active workflows."""
        for job_id in list(self._active_workflows.keys()):
            await self.cancel_workflow(job_id)
