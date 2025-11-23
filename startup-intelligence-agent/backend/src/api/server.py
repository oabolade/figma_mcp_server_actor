from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import uvicorn
import asyncio

from orchestrator.agent import OrchestratorAgent
from database.db import Database
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Startup Intelligence Agent API",
    description="API for Startup Intelligence Agent System",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and database
orchestrator = OrchestratorAgent()
db = Database(settings.DATABASE_PATH)
workflow_status = {"running": False, "last_run": None, "error": None}

# Lock for atomic workflow status updates (prevents race conditions)
workflow_lock = asyncio.Lock()

# Initialize workflow scheduler (lazy initialization)
scheduler = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown."""
    logger.info("Shutting down application, cleaning up resources...")
    try:
        # Stop scheduler if running
        global scheduler
        if scheduler and scheduler.is_running:
            logger.info("Stopping workflow scheduler...")
            await scheduler.stop()
        
        # Close orchestrator's HTTP client (closes httpx.AsyncClient)
        await orchestrator.close()
        logger.info("Orchestrator resources closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {e}")
    logger.info("Shutdown complete")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "startup-intelligence-agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/info")
async def get_info():
    """Get server and system information."""
    return {
        "service": "startup-intelligence-agent",
        "version": "1.0.0",
        "environment": "e2b-sandbox",
        "database_path": settings.DATABASE_PATH,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "data_collector_agents": {
            "news_scraper": settings.NEWS_SCRAPER_URL,
            "startup_api": settings.STARTUP_API_URL,
            "github_monitor": settings.GITHUB_MONITOR_URL
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/briefing")
async def get_briefing():
    """Get latest daily briefing."""
    try:
        # Get latest briefing from database
        latest_briefing = db.get_latest_briefing()
        
        if latest_briefing:
            briefing_json = latest_briefing.get("briefing_json", {})
            briefing_json["retrieved_at"] = datetime.now().isoformat()
            return briefing_json
        else:
            # Return 404 if no briefing exists (GET requests must be safe/idempotent)
            raise HTTPException(
                status_code=404,
                detail="No briefing found. Use POST /orchestrator/run to generate a briefing first."
            )
                
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error retrieving briefing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/briefing/{date}")
async def get_briefing_by_date(date: str):
    """Get briefing for a specific date (YYYY-MM-DD format)."""
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        briefing = db.get_briefing_by_date(date)
        
        if briefing:
            briefing_json = briefing.get("briefing_json", {})
            briefing_json["retrieved_at"] = datetime.now().isoformat()
            return briefing_json
        else:
            raise HTTPException(status_code=404, detail=f"Briefing not found for date: {date}")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error retrieving briefing for date {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/latest")
async def get_latest_analysis(days_back: int = Query(default=7, ge=1, le=30)):
    """Get latest analysis results."""
    try:
        # Get latest analysis from database
        latest_analysis = db.get_latest_analysis()
        
        if latest_analysis:
            results_json = latest_analysis.get("results_json", {})
            return {
                "analysis_date": latest_analysis.get("data_date_range_end", ""),
                "model_used": latest_analysis.get("model_used", ""),
                "results": results_json
            }
        else:
            raise HTTPException(status_code=404, detail="No analysis results found")
            
    except Exception as e:
        logger.error(f"Error retrieving analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/trends")
async def get_trends(days_back: int = Query(default=7, ge=1, le=30)):
    """Get trend analysis."""
    try:
        latest_analysis = db.get_latest_analysis()
        
        if latest_analysis:
            results = latest_analysis.get("results_json", {})
            trends = results.get("trends", [])
            return {
                "count": len(trends),
                "trends": trends
            }
        else:
            return {"count": 0, "trends": []}
            
    except Exception as e:
        logger.error(f"Error retrieving trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/opportunities")
async def get_opportunities(
    type: str = Query(default="all", regex="^(all|founders|investors)$")
):
    """Get opportunities for founders or investors."""
    try:
        latest_analysis = db.get_latest_analysis()
        
        if latest_analysis:
            results = latest_analysis.get("results_json", {})
            
            if type == "founders":
                return {
                    "count": len(results.get("opportunities_for_founders", [])),
                    "opportunities": results.get("opportunities_for_founders", [])
                }
            elif type == "investors":
                return {
                    "count": len(results.get("opportunities_for_investors", [])),
                    "opportunities": results.get("opportunities_for_investors", [])
                }
            else:  # all
                return {
                    "founders": {
                        "count": len(results.get("opportunities_for_founders", [])),
                        "opportunities": results.get("opportunities_for_founders", [])
                    },
                    "investors": {
                        "count": len(results.get("opportunities_for_investors", [])),
                        "opportunities": results.get("opportunities_for_investors", [])
                    }
                }
        else:
            return {"count": 0, "opportunities": []}
            
    except Exception as e:
        logger.error(f"Error retrieving opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrator/run")
async def trigger_workflow(days_back: int = Query(default=7, ge=1, le=30)):
    """Trigger full workflow in background: collect → enrich → analyze → summarize."""
    # Use lock to make check-and-set atomic (prevents race conditions)
    async with workflow_lock:
        if workflow_status["running"]:
            raise HTTPException(
                status_code=409,
                detail="Workflow is already running"
            )
        
        workflow_status["running"] = True
        workflow_status["error"] = None
    
    async def run_workflow():
        try:
            result = await orchestrator.run_full_workflow(days_back=days_back)
            workflow_status["last_run"] = datetime.now().isoformat()
            workflow_status["running"] = False
            if result.get("status") != "success":
                workflow_status["error"] = "Workflow completed with errors"
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            workflow_status["running"] = False
            workflow_status["error"] = str(e)
    
    # Use asyncio.create_task for async background execution
    asyncio.create_task(run_workflow())
    
    return {
        "status": "started",
        "message": "Full workflow started in background",
        "workflow": "collect → enrich → analyze → summarize",
        "days_back": days_back
    }


@app.post("/orchestrator/collect")
async def trigger_collection():
    """Trigger data collection only (no enrichment/analysis)."""
    # Use lock to make check-and-set atomic (prevents race conditions)
    async with workflow_lock:
        if workflow_status["running"]:
            raise HTTPException(
                status_code=409,
                detail="Workflow is already running"
            )
        
        workflow_status["running"] = True
        workflow_status["error"] = None
    
    async def run_collection():
        try:
            result = await orchestrator.run_data_collection_only()
            workflow_status["last_run"] = datetime.now().isoformat()
            workflow_status["running"] = False
            if result.get("status") != "success":
                workflow_status["error"] = "Collection completed with errors"
        except Exception as e:
            logger.error(f"Collection error: {e}")
            workflow_status["running"] = False
            workflow_status["error"] = str(e)
    
    # Use asyncio.create_task for async background execution
    asyncio.create_task(run_collection())
    
    return {
        "status": "started",
        "message": "Data collection started in background"
    }


@app.get("/orchestrator/status")
async def get_workflow_status():
    """Get current workflow status."""
    return workflow_status


@app.get("/data/stats")
async def get_data_stats():
    """Get statistics about collected data."""
    try:
        # Get counts from database
        news_count = db.count_recent_news(days=7)
        funding_count = db.count_recent_funding(days=7)
        launches_count = db.count_recent_launches(days=7)
        github_repos_count = db.count_recent_github_repos(days=7)
        github_signals = db.get_recent_github_signals(days=7)
        github_signals_count = len(github_signals) if github_signals else 0
        
        return {
            "last_7_days": {
                "news_articles": news_count,
                "funding_rounds": funding_count,
                "launches": launches_count,
                "github_repositories": github_repos_count,
                "github_signals": github_signals_count,
                "total": news_count + funding_count + launches_count + github_repos_count + github_signals_count
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/report")
async def get_workflow_report(days: int = Query(default=7, ge=1, le=30)):
    """Get workflow report and statistics."""
    try:
        from workflow.reporter import WorkflowReporter
        reporter = WorkflowReporter()
        report = reporter.generate_workflow_summary(days=days)
        return report
    except Exception as e:
        logger.error(f"Error generating workflow report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/health")
async def get_workflow_health():
    """Get workflow health status."""
    try:
        from workflow.reporter import WorkflowReporter
        reporter = WorkflowReporter()
        health = reporter.get_workflow_health()
        return health
    except Exception as e:
        logger.error(f"Error getting workflow health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/daily-report")
async def get_daily_report(date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")):
    """Get daily workflow report."""
    try:
        from workflow.reporter import WorkflowReporter
        reporter = WorkflowReporter()
        report = reporter.generate_daily_report(date=date)
        return report
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/scheduler/start")
async def start_scheduler(
    frequency: str = Query(default="daily", regex="^(hourly|daily|weekly|custom)$"),
    interval_seconds: Optional[int] = Query(None, ge=60),
    run_immediately: bool = Query(default=False)
):
    """Start automated workflow scheduler."""
    try:
        from workflow.scheduler import WorkflowScheduler, ScheduleFrequency
        
        global scheduler
        
        # Use lock to make check-and-set atomic (prevents race conditions)
        async with workflow_lock:
            if scheduler and scheduler.is_running:
                raise HTTPException(
                    status_code=409,
                    detail="Scheduler is already running"
                )
            
            # Validate custom frequency requires interval_seconds
            if frequency == "custom" and interval_seconds is None:
                raise HTTPException(
                    status_code=400,
                    detail="interval_seconds parameter is required when frequency=custom"
                )
            
            # Parse frequency
            freq_map = {
                "hourly": ScheduleFrequency.HOURLY,
                "daily": ScheduleFrequency.DAILY,
                "weekly": ScheduleFrequency.WEEKLY,
                "custom": ScheduleFrequency.CUSTOM
            }
            freq = freq_map[frequency]
            
            # Create scheduler if needed (atomic check-and-set)
            if not scheduler:
                async def workflow_runner():
                    """Wrapper to run workflow via scheduler."""
                    result = await orchestrator.run_full_workflow(days_back=7)
                    return result
                
                scheduler = WorkflowScheduler(orchestrator, workflow_runner)
        
        # Start scheduler (outside lock to avoid blocking other operations)
        await scheduler.start(
            frequency=freq,
            interval_seconds=interval_seconds,
            run_immediately=run_immediately
        )
        
        return {
            "status": "started",
            "frequency": frequency,
            "interval_seconds": scheduler.interval_seconds,
            "next_run": scheduler.next_run.isoformat() if scheduler.next_run else None,
            "message": f"Scheduler started with {frequency} frequency"
        }
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/scheduler/stop")
async def stop_scheduler():
    """Stop automated workflow scheduler."""
    try:
        global scheduler
        
        if not scheduler or not scheduler.is_running:
            raise HTTPException(
                status_code=404,
                detail="Scheduler is not running"
            )
        
        await scheduler.stop()
        
        return {
            "status": "stopped",
            "message": "Scheduler stopped successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status."""
    try:
        global scheduler
        
        if not scheduler:
            return {
                "enabled": False,
                "is_running": False,
                "message": "Scheduler not initialized"
            }
        
        return scheduler.get_status()
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/scheduler/trigger")
async def trigger_scheduled_workflow():
    """Manually trigger scheduled workflow execution."""
    try:
        global scheduler
        
        if not scheduler or not scheduler.is_running:
            raise HTTPException(
                status_code=404,
                detail="Scheduler is not running"
            )
        
        await scheduler.trigger_now()
        
        return {
            "status": "triggered",
            "message": "Workflow execution triggered",
            "last_run": scheduler.last_run.isoformat() if scheduler.last_run else None,
            "next_run": scheduler.next_run.isoformat() if scheduler.next_run else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Mount static files for frontend (serve frontend/index.html at root)
    frontend_path = Path(__file__).parent.parent.parent.parent / "frontend"
    if frontend_path.exists():
        # Serve index.html at root
        @app.get("/")
        async def serve_frontend():
            """Serve frontend dashboard."""
            index_file = frontend_path / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            else:
                return {"message": "Frontend not found. API is running."}
        
        # Serve static files (if any CSS/JS files are added later)
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        logger.info(f"Frontend mounted from: {frontend_path}")
    else:
        logger.warning(f"Frontend directory not found at: {frontend_path}")
    
    return app


if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.PORT or 8080,
        reload=False,
        log_level="info"
    )