"""
Travel Lotara AI - Agent Orchestrator for Vercel Serverless

Orchestrates the multi-agent system for travel planning.
Designed for serverless execution with Supabase persistence.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Add the src directory to path for imports
_src_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "src"
)
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    PROCESSING = "processing"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    ERROR = "error"


class TravelOrchestrator:
    """
    Orchestrates the multi-agent travel planning workflow.
    
    Designed for serverless:
    - Stateless execution
    - Persists state to Supabase between invocations
    - Handles timeouts gracefully
    """
    
    def __init__(self, supabase_client=None):
        """Initialize the orchestrator."""
        self.client = supabase_client
        self._agents_loaded = False
        self._root_agent = None
    
    def _lazy_load_agents(self):
        """Lazy load agents to minimize cold start time."""
        if self._agents_loaded:
            return
        
        try:
            from travel_lotara.agent import root_agent
            self._root_agent = root_agent
            self._agents_loaded = True
            logger.info("Agents loaded successfully")
        except ImportError as e:
            logger.warning(f"Could not load agents: {e}")
            self._agents_loaded = False
        except Exception as e:
            logger.warning(f"Error loading agents: {e}")
            self._agents_loaded = False
    
    async def process_plan_request(
        self,
        job_id: str,
        user_id: str,
        query: str,
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a travel planning request.
        
        Args:
            job_id: Unique job identifier
            user_id: User making the request
            query: Natural language travel request
            constraints: Structured constraints (budget, dates, etc.)
        
        Returns:
            Result with status and any outputs
        """
        self._lazy_load_agents()
        
        # Update job status to processing
        await self._update_job_status(job_id, "planning")
        
        try:
            # If agents are available, use them
            if self._root_agent:
                result = await self._run_agent_workflow(
                    job_id, user_id, query, constraints
                )
            else:
                # Fallback: Simple mock response for testing
                result = await self._mock_planning(
                    job_id, user_id, query, constraints
                )
            
            # Update job with result
            await self._update_job_result(job_id, result)
            return result
            
        except Exception as e:
            logger.exception(f"Error processing plan request: {e}")
            await self._update_job_error(job_id, str(e))
            raise
    
    async def _run_agent_workflow(
        self,
        job_id: str,
        user_id: str,
        query: str,
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """Run the full agent workflow using Google ADK."""
        try:
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            
            # Create session
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="travel-lotara",
                user_id=user_id,
            )
            
            # Build context-enriched query
            enhanced_query = self._build_enhanced_query(query, constraints)
            
            # Run the root agent
            runner = Runner(
                agent=self._root_agent,
                app_name="travel-lotara",
                session_service=session_service,
            )
            
            # Process the request
            response = await runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=enhanced_query,
            )
            
            # Extract and structure the response
            return {
                "status": "completed",
                "job_id": job_id,
                "result": {
                    "response": str(response) if response else "Planning complete",
                    "query": query,
                    "constraints": constraints,
                },
                "requires_approval": True,
                "message": "Planning complete. Please review the results.",
            }
            
        except ImportError as e:
            logger.warning(f"Google ADK not available: {e}")
            # Fall back to mock
            return await self._mock_planning(job_id, user_id, query, constraints)
        except Exception as e:
            logger.exception(f"Agent workflow error: {e}")
            raise
    
    def _build_enhanced_query(self, query: str, constraints: dict[str, Any]) -> str:
        """Build an enhanced query with constraints for the agent."""
        parts = [query]
        
        if constraints:
            parts.append("\n\nAdditional constraints:")
            if "budget_usd" in constraints:
                parts.append(f"- Budget: ${constraints['budget_usd']} USD")
            if "duration_days" in constraints:
                parts.append(f"- Duration: {constraints['duration_days']} days")
            if "destination" in constraints:
                parts.append(f"- Destination: {constraints['destination']}")
            if "interests" in constraints:
                parts.append(f"- Interests: {', '.join(constraints['interests'])}")
            if "departure_city" in constraints:
                parts.append(f"- Departing from: {constraints['departure_city']}")
            if "travel_dates" in constraints:
                parts.append(f"- Travel dates: {constraints['travel_dates']}")
        
        return "\n".join(parts)
    
    async def _mock_planning(
        self,
        job_id: str,
        user_id: str,
        query: str,
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Mock planning response for testing without full agent system.
        Returns a structured response based on the query.
        """
        # Parse basic info from query/constraints
        destination = constraints.get("destination") or "your destination"
        budget = constraints.get("budget_usd", 2000)
        duration = constraints.get("duration_days", 5)
        
        return {
            "status": "completed",
            "job_id": job_id,
            "result": {
                "summary": f"Trip planning for {destination}",
                "itinerary": {
                    "destination": destination,
                    "duration_days": duration,
                    "estimated_budget_usd": budget,
                    "status": "draft",
                },
                "recommendations": [
                    {
                        "type": "flight",
                        "description": f"Round-trip flights to {destination}",
                        "estimated_cost": int(budget * 0.3),
                    },
                    {
                        "type": "hotel",
                        "description": f"{duration} nights accommodation",
                        "estimated_cost": int(budget * 0.4),
                    },
                    {
                        "type": "activities",
                        "description": "Local experiences and tours",
                        "estimated_cost": int(budget * 0.2),
                    },
                ],
                "next_steps": [
                    "Review the proposed itinerary",
                    "Approve or modify recommendations",
                    "Proceed to booking",
                ],
            },
            "requires_approval": True,
            "message": "Planning complete. Please review and approve.",
        }
    
    async def _update_job_status(self, job_id: str, status: str) -> None:
        """Update job status in Supabase."""
        if not self.client:
            return
        
        try:
            self.client.table("jobs").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", job_id).execute()
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def _update_job_result(self, job_id: str, result: dict) -> None:
        """Update job with final result."""
        if not self.client:
            return
        
        try:
            update_data = {
                "status": "completed" if result.get("status") == "completed" else "waiting_approval",
                "final_result": result.get("result"),
                "awaiting_approval": result.get("requires_approval", False),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if result.get("status") == "completed":
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            self.client.table("jobs").update(update_data).eq("id", job_id).execute()
        except Exception as e:
            logger.error(f"Failed to update job result: {e}")
    
    async def _update_job_error(self, job_id: str, error: str) -> None:
        """Update job with error information."""
        if not self.client:
            return
        
        try:
            self.client.table("jobs").update({
                "status": "failed",
                "error": {"message": error, "timestamp": datetime.utcnow().isoformat()},
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", job_id).execute()
        except Exception as e:
            logger.error(f"Failed to update job error: {e}")


class SuggestionOrchestrator:
    """
    Orchestrates proactive suggestion workflows.
    
    Triggered by external events like:
    - Price drops
    - Calendar gaps
    - Trending destinations
    """
    
    def __init__(self, supabase_client=None):
        self.client = supabase_client
    
    async def process_suggestion(
        self,
        job_id: str,
        user_id: str,
        trigger_type: str,
        trigger_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a proactive suggestion trigger.
        
        Args:
            job_id: Unique job identifier
            user_id: User to suggest to
            trigger_type: Type of trigger (price_alert, calendar_gap, etc.)
            trigger_data: Trigger-specific data
        
        Returns:
            Suggestion result
        """
        # Get user preferences
        preferences = await self._get_user_preferences(user_id)
        
        # Generate suggestion based on trigger type
        if trigger_type == "price_alert":
            suggestion = await self._generate_price_alert_suggestion(
                trigger_data, preferences
            )
        elif trigger_type == "calendar_gap":
            suggestion = await self._generate_calendar_suggestion(
                trigger_data, preferences
            )
        else:
            suggestion = await self._generate_generic_suggestion(
                trigger_data, preferences
            )
        
        # Store result
        if self.client:
            self.client.table("jobs").update({
                "status": "completed",
                "final_result": suggestion,
                "completed_at": datetime.utcnow().isoformat(),
            }).eq("id", job_id).execute()
        
        return suggestion
    
    async def _get_user_preferences(self, user_id: str) -> dict:
        """Fetch user preferences from database."""
        if not self.client:
            return {}
        
        try:
            result = self.client.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
            return result.data or {}
        except Exception:
            return {}
    
    async def _generate_price_alert_suggestion(
        self, trigger_data: dict, preferences: dict
    ) -> dict:
        """Generate suggestion for price drop alert."""
        return {
            "type": "price_alert",
            "title": f"Price drop to {trigger_data.get('destination', 'destination')}!",
            "message": f"Flights dropped by {trigger_data.get('discount_percent', 20)}%",
            "action": "view_deal",
            "data": trigger_data,
        }
    
    async def _generate_calendar_suggestion(
        self, trigger_data: dict, preferences: dict
    ) -> dict:
        """Generate suggestion for calendar gap."""
        return {
            "type": "calendar_gap",
            "title": "You have time off coming up!",
            "message": f"Plan a trip for {trigger_data.get('dates', 'your free time')}",
            "action": "start_planning",
            "data": trigger_data,
        }
    
    async def _generate_generic_suggestion(
        self, trigger_data: dict, preferences: dict
    ) -> dict:
        """Generate generic travel suggestion."""
        return {
            "type": "recommendation",
            "title": "Travel inspiration",
            "message": "Discover new destinations based on your preferences",
            "action": "explore",
            "data": trigger_data,
        }


# Global instances (lazy-loaded)
_travel_orchestrator: Optional[TravelOrchestrator] = None
_suggestion_orchestrator: Optional[SuggestionOrchestrator] = None


def get_travel_orchestrator(supabase_client=None) -> TravelOrchestrator:
    """Get or create the travel orchestrator instance."""
    global _travel_orchestrator
    if _travel_orchestrator is None:
        _travel_orchestrator = TravelOrchestrator(supabase_client)
    elif supabase_client and _travel_orchestrator.client is None:
        _travel_orchestrator.client = supabase_client
    return _travel_orchestrator


def get_suggestion_orchestrator(supabase_client=None) -> SuggestionOrchestrator:
    """Get or create the suggestion orchestrator instance."""
    global _suggestion_orchestrator
    if _suggestion_orchestrator is None:
        _suggestion_orchestrator = SuggestionOrchestrator(supabase_client)
    elif supabase_client and _suggestion_orchestrator.client is None:
        _suggestion_orchestrator.client = supabase_client
    return _suggestion_orchestrator
