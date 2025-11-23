# Prompt 10: API Endpoints (FastAPI HTTP Server)

## Objective

Create FastAPI HTTP server endpoints inside the E2B sandbox to expose the briefing, analysis results, and workflow controls. The server runs locally within the sandbox and is accessible via E2B's HTTP endpoints.

## Requirements

### API Server Responsibilities

The FastAPI server runs **inside the E2B sandbox** and:

1. **Expose Briefing Endpoint**
   - GET `/briefing` - Returns latest daily briefing JSON
   - GET `/briefing/{date}` - Returns briefing for specific date

2. **Expose Analysis Results**
   - GET `/analysis/latest` - Returns latest analysis results
   - GET `/analysis/trends` - Returns trend analysis
   - GET `/analysis/opportunities` - Returns opportunities

3. **Workflow Control**
   - POST `/orchestrator/run` - Trigger full workflow
   - POST `/orchestrator/collect` - Trigger data collection only
   - GET `/orchestrator/status` - Get workflow status

4. **Health & Info**
   - GET `/health` - Health check endpoint
   - GET `/info` - Server and system information

### Implementation

**File:** `backend/src/api/server.py`

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown."""
    logger.info("Shutting down application, cleaning up resources...")
    try:
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
        
        return {
            "last_7_days": {
                "news_articles": news_count,
                "funding_rounds": funding_count,
                "launches": launches_count,
                "github_repositories": github_repos_count
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
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
```

### Database Helper Methods

Add these methods to `database/db.py`:

```python
def get_briefing_by_date(self, date: str) -> Optional[Dict]:
    """Get briefing for a specific date."""
    conn = self.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM briefings 
        WHERE briefing_date = ?
    """, (date,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['briefing_json'] = json.loads(result['briefing_json'])
        return result
    return None

def get_latest_analysis(self) -> Optional[Dict]:
    """Get latest analysis results."""
    conn = self.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM analysis_results 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['results_json'] = json.loads(result['results_json'])
        return result
    return None

def count_recent_news(self, days: int) -> int:
    """Count recent news articles."""
    # Validate input to prevent SQL injection
    if not isinstance(days, int) or days < 1 or days > 365:
        raise ValueError("days must be an integer between 1 and 365")
    
    conn = self.get_connection()
    cursor = conn.cursor()
    
    # Use parameterized query with string concatenation for date calculation
    cursor.execute("""
        SELECT COUNT(*) FROM news 
        WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
    """, (str(days),))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_recent_funding(self, days: int) -> int:
    """Count recent funding rounds."""
    # Validate input to prevent SQL injection
    if not isinstance(days, int) or days < 1 or days > 365:
        raise ValueError("days must be an integer between 1 and 365")
    
    conn = self.get_connection()
    cursor = conn.cursor()
    
    # Use parameterized query with string concatenation for date calculation
    cursor.execute("""
        SELECT COUNT(*) FROM funding 
        WHERE date(date) >= date('now', '-' || ? || ' days')
    """, (str(days),))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_recent_launches(self, days: int) -> int:
    """Count recent launches."""
    # Validate input to prevent SQL injection
    if not isinstance(days, int) or days < 1 or days > 365:
        raise ValueError("days must be an integer between 1 and 365")
    
    conn = self.get_connection()
    cursor = conn.cursor()
    
    # Use parameterized query with string concatenation for date calculation
    cursor.execute("""
        SELECT COUNT(*) FROM launches 
        WHERE date(date) >= date('now', '-' || ? || ' days')
    """, (str(days),))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_recent_github_repos(self, days: int) -> int:
    """Count recent GitHub repositories."""
    # Validate input to prevent SQL injection
    if not isinstance(days, int) or days < 1 or days > 365:
        raise ValueError("days must be an integer between 1 and 365")
    
    conn = self.get_connection()
    cursor = conn.cursor()
    
    # Use parameterized query with string concatenation for date calculation
    cursor.execute("""
        SELECT COUNT(*) FROM github_repositories 
        WHERE datetime(updated_at) >= datetime('now', '-' || ? || ' days')
    """, (str(days),))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count
```

### API Documentation

Once the server is running, API documentation will be available at:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### Testing

**Start the server:**
```bash
cd backend
python src/api/server.py
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8080/health

# Get latest briefing
curl http://localhost:8080/briefing

# Trigger workflow
curl -X POST http://localhost:8080/orchestrator/run?days_back=7

# Get workflow status
curl http://localhost:8080/orchestrator/status

# Get trends
curl http://localhost:8080/analysis/trends
```

### E2B Sandbox Access

When running in E2B sandbox, the API will be accessible via:
- **Container URL**: `https://<containerId>.runs.apify.net/`
- **Local in sandbox**: `http://localhost:8080/`

### Deliverables

1. Complete FastAPI server implementation
2. All required endpoints (briefing, analysis, orchestrator, health)
3. CORS middleware for frontend access
4. Background task support for long-running workflows
5. Error handling and logging
6. API documentation (auto-generated by FastAPI)
7. Database helper methods for API endpoints
8. Workflow status tracking

### Next Steps

After completing the API endpoints, proceed to:
- **11-frontend-ui.md** - Build the frontend UI to consume the API
- **12-integration-deployment.md** - Integration testing and deployment guide
