"""Workflow scheduler for automated execution."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Workflow execution frequency."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class WorkflowScheduler:
    """Scheduler for automated workflow execution."""
    
    def __init__(self, orchestrator, workflow_runner: Callable):
        """
        Initialize workflow scheduler.
        
        Args:
            orchestrator: OrchestratorAgent instance
            workflow_runner: Async function to run the workflow
        """
        self.orchestrator = orchestrator
        self.workflow_runner = workflow_runner
        self.scheduled_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.frequency: Optional[ScheduleFrequency] = None
        self.interval_seconds: Optional[int] = None
        self.enabled = False
    
    async def start(
        self,
        frequency: ScheduleFrequency = ScheduleFrequency.DAILY,
        interval_seconds: Optional[int] = None,
        run_immediately: bool = False
    ):
        """
        Start scheduled workflow execution.
        
        Args:
            frequency: How often to run (hourly, daily, weekly)
            interval_seconds: Custom interval in seconds (for CUSTOM frequency)
            run_immediately: Whether to run workflow immediately on start
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.frequency = frequency
        self.enabled = True
        
        # Calculate interval based on frequency
        if frequency == ScheduleFrequency.HOURLY:
            self.interval_seconds = 3600  # 1 hour
        elif frequency == ScheduleFrequency.DAILY:
            self.interval_seconds = 86400  # 24 hours
        elif frequency == ScheduleFrequency.WEEKLY:
            self.interval_seconds = 604800  # 7 days
        elif frequency == ScheduleFrequency.CUSTOM:
            if not interval_seconds:
                raise ValueError("interval_seconds required for CUSTOM frequency")
            self.interval_seconds = interval_seconds
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
        
        logger.info(f"Starting workflow scheduler: {frequency.value} (interval: {self.interval_seconds}s)")
        
        # Run immediately if requested
        if run_immediately:
            logger.info("Running workflow immediately on scheduler start")
            asyncio.create_task(self._run_workflow())
        
        # Start scheduled task
        self.is_running = True
        self.scheduled_task = asyncio.create_task(self._scheduler_loop())
        self._calculate_next_run()
        
        logger.info(f"Scheduler started. Next run: {self.next_run}")
    
    async def stop(self):
        """Stop scheduled workflow execution."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping workflow scheduler...")
        self.enabled = False
        self.is_running = False
        
        if self.scheduled_task:
            self.scheduled_task.cancel()
            try:
                await self.scheduled_task
            except asyncio.CancelledError:
                pass
        
        self.scheduled_task = None
        logger.info("Scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.enabled:
            try:
                # Wait until next run time
                if self.next_run:
                    now = datetime.now()
                    wait_seconds = (self.next_run - now).total_seconds()
                    
                    if wait_seconds > 0:
                        logger.info(f"Scheduler waiting {wait_seconds:.0f} seconds until next run")
                        await asyncio.sleep(wait_seconds)
                    
                    # Run workflow
                    await self._run_workflow()
                    
                    # Calculate next run
                    self._calculate_next_run()
                else:
                    # No next run scheduled, wait a bit and check again
                    await asyncio.sleep(60)
                    
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # Wait before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def _run_workflow(self):
        """Run the workflow."""
        try:
            logger.info("Scheduled workflow execution starting...")
            self.last_run = datetime.now()
            
            # Run the workflow
            await self.workflow_runner()
            
            logger.info("Scheduled workflow execution completed successfully")
            
        except Exception as e:
            logger.error(f"Error in scheduled workflow execution: {e}", exc_info=True)
            # Don't update last_run on error - will retry on next interval
    
    def _calculate_next_run(self):
        """Calculate next scheduled run time."""
        if not self.interval_seconds:
            self.next_run = None
            return
        
        base_time = self.last_run if self.last_run else datetime.now()
        self.next_run = base_time + timedelta(seconds=self.interval_seconds)
    
    def get_status(self) -> Dict:
        """Get scheduler status."""
        return {
            "enabled": self.enabled,
            "is_running": self.is_running,
            "frequency": self.frequency.value if self.frequency else None,
            "interval_seconds": self.interval_seconds,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "seconds_until_next": (
                (self.next_run - datetime.now()).total_seconds()
                if self.next_run else None
            )
        }
    
    async def trigger_now(self):
        """Manually trigger workflow execution now."""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        logger.info("Manually triggering workflow execution")
        await self._run_workflow()
        self._calculate_next_run()

