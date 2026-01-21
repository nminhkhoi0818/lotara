"""
Background Scheduler for Proactive Tasks

Monitors external conditions and triggers proactive workflows:
- Flight price monitoring
- Calendar gap detection
- Budget surplus identification
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from ..core.job_manager import JobManager
from ..core.workflow_executor import WorkflowExecutor


logger = logging.getLogger(__name__)


class ProactiveScheduler:
    """
    Background scheduler for proactive AI tasks.
    
    Features:
    - Flight price monitoring (every 6 hours)
    - Calendar gap detection (daily)
    - Budget surplus check (weekly)
    - Triggered suggestions
    
    Uses APScheduler for reliable task scheduling.
    """
    
    def __init__(
        self,
        job_manager: JobManager,
        workflow_executor: WorkflowExecutor,
    ):
        """
        Initialize scheduler.
        
        Args:
            job_manager: Job state manager
            workflow_executor: Workflow executor
        """
        self.job_manager = job_manager
        self.workflow_executor = workflow_executor
        
        # APScheduler
        self.scheduler = AsyncIOScheduler()
        
        # Active monitoring
        self._price_monitors: dict[str, dict] = {}  # user_id -> routes
        self._calendar_monitors: dict[str, dict] = {}  # user_id -> preferences
    
    def start(self):
        """
        Start background scheduler.
        
        Registers all periodic tasks and starts scheduler.
        """
        logger.info("Starting proactive scheduler...")
        
        # Price monitoring - every 6 hours
        self.scheduler.add_job(
            self._check_price_drops,
            trigger=IntervalTrigger(hours=6),
            id="price_monitoring",
            name="Flight Price Monitoring",
            replace_existing=True,
        )
        
        # Calendar gap detection - daily at 9 AM
        self.scheduler.add_job(
            self._check_calendar_gaps,
            trigger=CronTrigger(hour=9, minute=0),
            id="calendar_gaps",
            name="Calendar Gap Detection",
            replace_existing=True,
        )
        
        # Budget surplus - weekly on Mondays at 10 AM
        self.scheduler.add_job(
            self._check_budget_surplus,
            trigger=CronTrigger(day_of_week="mon", hour=10, minute=0),
            id="budget_surplus",
            name="Budget Surplus Check",
            replace_existing=True,
        )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("✓ Proactive scheduler started")
    
    def stop(self):
        """Stop scheduler."""
        self.scheduler.shutdown()
        logger.info("Proactive scheduler stopped")
    
    # ============================================
    # MONITORING REGISTRATION
    # ============================================
    
    async def register_price_monitor(
        self,
        user_id: str,
        routes: list[dict[str, str]],
        target_price_usd: Optional[float] = None,
    ):
        """
        Register user for price monitoring.
        
        Args:
            user_id: User to monitor for
            routes: List of routes to watch (origin, destination)
            target_price_usd: Alert if price drops below this
        """
        self._price_monitors[user_id] = {
            "routes": routes,
            "target_price": target_price_usd,
            "last_prices": {},
        }
        
        logger.info(f"Registered price monitoring for user {user_id}: {len(routes)} routes")
    
    async def register_calendar_monitor(
        self,
        user_id: str,
        preferences: dict[str, Any],
    ):
        """
        Register user for calendar gap detection.
        
        Args:
            user_id: User to monitor for
            preferences: Travel preferences (destinations, interests)
        """
        self._calendar_monitors[user_id] = preferences
        
        logger.info(f"Registered calendar monitoring for user {user_id}")
    
    # ============================================
    # PERIODIC TASKS
    # ============================================
    
    async def _check_price_drops(self):
        """
        Check for flight price drops.
        
        Runs every 6 hours.
        Triggers proactive suggestions when savings detected.
        """
        logger.info(f"Checking price drops for {len(self._price_monitors)} users...")
        
        from src.travel_lotara.tools.api_tools import APITools
        api_tools = APITools()
        
        for user_id, monitor_data in self._price_monitors.items():
            try:
                for route in monitor_data["routes"]:
                    origin = route["origin"]
                    destination = route["destination"]
                    
                    # Search current prices
                    # Note: In production, use real API with proper date
                    response = await api_tools.search_flights(
                        origin=origin,
                        destination=destination,
                        departure_date="2026-02-01",  # Example
                    )
                    
                    if response.data:
                        current_price = response.data[0]["price_usd"]
                        route_key = f"{origin}-{destination}"
                        
                        # Check if price dropped
                        last_price = monitor_data["last_prices"].get(route_key)
                        
                        if last_price and current_price < last_price * 0.85:  # 15% drop
                            savings = last_price - current_price
                            
                            logger.info(
                                f"Price drop detected for {user_id}: "
                                f"{route_key} ${last_price} → ${current_price} "
                                f"(save ${savings})"
                            )
                            
                            # Trigger proactive suggestion
                            await self.workflow_executor.execute_proactive_workflow(
                                job_id=None,  # Will be created by executor
                                user_id=user_id,
                                trigger_type="price_drop",
                                trigger_context={
                                    "route": route_key,
                                    "origin": origin,
                                    "destination": destination,
                                    "old_price": last_price,
                                    "new_price": current_price,
                                    "savings": savings,
                                    "flight_details": response.data[0],
                                },
                            )
                        
                        # Update last price
                        monitor_data["last_prices"][route_key] = current_price
            
            except Exception as e:
                logger.error(f"Price check failed for {user_id}: {e}")
    
    async def _check_calendar_gaps(self):
        """
        Detect calendar gaps (potential trip windows).
        
        Runs daily at 9 AM.
        Suggests trips when user has free time.
        """
        logger.info(f"Checking calendar gaps for {len(self._calendar_monitors)} users...")
        
        # In production:
        # 1. Query user's calendar (via product backend API)
        # 2. Identify 3+ day gaps in next 3 months
        # 3. Match with travel preferences
        # 4. Trigger suggestion workflow
        
        # Simplified for demo
        for user_id, preferences in self._calendar_monitors.items():
            try:
                # Simulate gap detection
                gap_start = datetime.utcnow() + timedelta(days=14)
                gap_end = gap_start + timedelta(days=5)
                
                logger.info(
                    f"Calendar gap detected for {user_id}: "
                    f"{gap_start.date()} to {gap_end.date()}"
                )
                
                # Trigger proactive suggestion
                await self.workflow_executor.execute_proactive_workflow(
                    job_id=None,
                    user_id=user_id,
                    trigger_type="calendar_gap",
                    trigger_context={
                        "gap_start": gap_start.isoformat(),
                        "gap_end": gap_end.isoformat(),
                        "duration_days": 5,
                        "preferences": preferences,
                    },
                )
            
            except Exception as e:
                logger.error(f"Calendar check failed for {user_id}: {e}")
    
    async def _check_budget_surplus(self):
        """
        Identify users with budget surplus.
        
        Runs weekly on Mondays.
        Suggests upgrades or additional experiences.
        """
        logger.info("Checking budget surplus...")
        
        # In production:
        # 1. Query user spending vs budget from product backend
        # 2. Identify surplus >$200
        # 3. Suggest hotel upgrade, extra activities, longer trip
        # 4. Trigger suggestion workflow
        
        # Simplified for demo
        example_user_id = "user123"
        
        logger.info(f"Budget surplus detected for {example_user_id}: $500 available")
        
        await self.workflow_executor.execute_proactive_workflow(
            job_id=None,
            user_id=example_user_id,
            trigger_type="budget_surplus",
            trigger_context={
                "surplus_usd": 500,
                "suggestions": [
                    "Upgrade to 4-star hotel",
                    "Add extra day in Tokyo",
                    "Book premium food tour",
                ],
            },
        )
    
    # ============================================
    # MANUAL TRIGGERS (for testing)
    # ============================================
    
    async def trigger_price_check_now(self):
        """Manually trigger price check (for testing)."""
        await self._check_price_drops()
    
    async def trigger_calendar_check_now(self):
        """Manually trigger calendar check (for testing)."""
        await self._check_calendar_gaps()
    
    async def trigger_budget_check_now(self):
        """Manually trigger budget check (for testing)."""
        await self._check_budget_surplus()
