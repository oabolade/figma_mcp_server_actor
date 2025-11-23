# Prompt 12: Integration, Testing & Deployment

## Objective

Create a comprehensive guide for integrating all components, testing the complete system, and deploying to production. This includes integration testing, E2B sandbox deployment, Docker MCP Hub agent deployment, and monitoring.

## Requirements

### Integration Checklist

1. **Component Integration**
   - [ ] All data collector agents deployed and accessible
   - [ ] Orchestrator agent connects to all agents
   - [ ] Database initialized and working
   - [ ] Enrichment agent processes data correctly
   - [ ] Analysis agent generates insights
   - [ ] Summarizer creates briefings
   - [ ] API endpoints return correct data
   - [ ] Frontend displays briefing correctly

2. **End-to-End Workflow**
   - [ ] Full workflow executes: collect → enrich → analyze → summarize
   - [ ] Data flows correctly between all stages
   - [ ] Error handling works at each stage
   - [ ] Briefings are saved and retrievable

3. **Data Quality**
   - [ ] News articles are collected correctly
   - [ ] Funding rounds are parsed accurately
   - [ ] Launches are captured properly
   - [ ] GitHub signals are meaningful
   - [ ] Enrichment adds valuable context
   - [ ] Analysis produces actionable insights

### Testing Strategy

#### 1. Unit Tests

**File:** `backend/tests/test_database.py`
```python
import pytest
from database.db import Database
import tempfile
import os

@pytest.fixture
def test_db():
    # Create temporary database
    fd, path = tempfile.mkstemp(suffix='.db')
    db = Database(path)
    yield db
    os.close(fd)
    os.unlink(path)

def test_insert_news(test_db):
    articles = [{
        "title": "Test Article",
        "url": "https://example.com/test",
        "source": "techcrunch",
        "timestamp": "2024-01-15T10:00:00Z",
        "summary": "Test summary"
    }]
    inserted = test_db.insert_news(articles)
    assert inserted == 1

def test_get_recent_news(test_db):
    articles = test_db.get_recent_news(days=7)
    assert isinstance(articles, list)
```

**File:** `backend/tests/test_orchestrator.py`
```python
import pytest
from unittest.mock import AsyncMock, patch
from orchestrator.agent import OrchestratorAgent

@pytest.mark.asyncio
async def test_collect_all_data():
    agent = OrchestratorAgent()
    
    with patch('orchestrator.agent.httpx.AsyncClient') as mock_client:
        mock_client.return_value.get = AsyncMock(return_value=AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"total": 0, "sources": {}})
        ))
        
        result = await agent.collect_all_data()
        assert "news" in result
        assert "startup" in result
        assert "github" in result
```

#### 2. Integration Tests

**File:** `backend/tests/test_integration.py`
```python
import pytest
import asyncio
from orchestrator.agent import OrchestratorAgent
from database.db import Database

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_workflow():
    """Test complete workflow end-to-end."""
    agent = OrchestratorAgent()
    
    # Run data collection only (faster for testing)
    result = await agent.run_data_collection_only()
    
    assert result["status"] == "success"
    assert "data_collected" in result
    
    # Verify data was stored
    db = Database()
    news = db.get_recent_news(days=1)
    assert len(news) > 0

@pytest.mark.asyncio
@pytest.mark.integration
async def test_api_endpoints():
    """Test API endpoints."""
    from fastapi.testclient import TestClient
    from api.server import app
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Test briefing endpoint (may need data first)
    response = client.get("/briefing?days_back=1")
    assert response.status_code in [200, 404]  # 404 if no data yet
```

#### 3. End-to-End Tests

**File:** `tests/e2e/test_full_system.py`
```python
import pytest
import requests
import time

API_BASE_URL = "http://localhost:8080"

def test_e2e_workflow():
    """End-to-end test of complete system."""
    
    # 1. Trigger workflow
    response = requests.post(f"{API_BASE_URL}/orchestrator/run?days_back=1")
    assert response.status_code == 200
    
    # 2. Wait for workflow to complete
    max_wait = 300  # 5 minutes
    waited = 0
    while waited < max_wait:
        status_response = requests.get(f"{API_BASE_URL}/orchestrator/status")
        status = status_response.json()
        
        if not status["running"]:
            break
        
        time.sleep(10)
        waited += 10
    
    # 3. Verify briefing exists
    briefing_response = requests.get(f"{API_BASE_URL}/briefing")
    assert briefing_response.status_code == 200
    
    briefing = briefing_response.json()
    assert "summary" in briefing
    assert "trends" in briefing
    assert "funding_rounds" in briefing
```

### Deployment Guide

#### 1. Deploy Docker MCP Hub Agents

**news-scraper Agent:**
```bash
cd tools/news-scraper
docker build -t news-scraper:latest .
docker tag news-scraper:latest yourusername/news-scraper:latest
docker push yourusername/news-scraper:latest

# Register with Docker MCP Hub
# (Follow Docker MCP Hub documentation for registration)
```

**startup-api Agent:**
```bash
cd tools/startup-api
docker build -t startup-api:latest .
docker tag startup-api:latest yourusername/startup-api:latest
docker push yourusername/startup-api:latest
```

**github-monitor Agent:**
```bash
cd tools/github-monitor
docker build -t github-monitor:latest .
docker tag github-monitor:latest yourusername/github-monitor:latest
docker push yourusername/github-monitor:latest
```

#### 2. Deploy Orchestrator to E2B Sandbox

**E2B Sandbox Configuration:**

1. **Create E2B Sandbox:**
   ```python
   from e2b import Sandbox
   
   sandbox = Sandbox(
       template="python3",
       api_key=settings.E2B_API_KEY
   )
   ```

2. **Upload Code:**
   ```python
   # Upload backend code to sandbox
   sandbox.filesystem.write('/app/main.py', backend_code)
   ```

3. **Install Dependencies:**
   ```python
   # Install Python dependencies
   sandbox.process.start("pip install -r requirements.txt")
   ```

4. **Set Environment Variables:**
   ```python
   # Set environment variables
   sandbox.env.set("OPENAI_API_KEY", settings.OPENAI_API_KEY)
   sandbox.env.set("NEWS_SCRAPER_URL", "http://news-scraper:3001")
   sandbox.env.set("STARTUP_API_URL", "http://startup-api:3002")
   sandbox.env.set("GITHUB_MONITOR_URL", "http://github-monitor:3003")
   ```

5. **Start API Server:**
   ```python
   # Start FastAPI server
   sandbox.process.start("python main.py", ports=[8080])
   ```

#### 3. E2B Sandbox Deployment Script

**File:** `scripts/deploy_to_e2b.py`
```python
from e2b import Sandbox
import os
import shutil
from pathlib import Path

def deploy_to_e2b():
    """Deploy backend to E2B sandbox."""
    
    # Create sandbox
    sandbox = Sandbox(
        template="python3",
        api_key=os.getenv("E2B_API_KEY")
    )
    
    try:
        # Upload backend code
        backend_path = Path("backend")
        for file_path in backend_path.rglob("*.py"):
            relative_path = file_path.relative_to(backend_path)
            sandbox_path = f"/app/{relative_path}"
            
            # Create directory if needed
            sandbox.filesystem.make_dir(os.path.dirname(sandbox_path))
            
            # Upload file
            with open(file_path, "rb") as f:
                sandbox.filesystem.write(sandbox_path, f.read())
        
        # Upload requirements.txt
        with open("backend/requirements.txt", "r") as f:
            sandbox.filesystem.write("/app/requirements.txt", f.read())
        
        # Set environment variables
        env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "NEWS_SCRAPER_URL": os.getenv("NEWS_SCRAPER_URL", "http://localhost:3001"),
            "STARTUP_API_URL": os.getenv("STARTUP_API_URL", "http://localhost:3002"),
            "GITHUB_MONITOR_URL": os.getenv("GITHUB_MONITOR_URL", "http://localhost:3003"),
            "PORT": "8080"
        }
        
        for key, value in env_vars.items():
            sandbox.env.set(key, value)
        
        # Install dependencies
        print("Installing dependencies...")
        install_process = sandbox.process.start("pip install -r /app/requirements.txt")
        install_process.wait()
        
        # Start server
        print("Starting API server...")
        server_process = sandbox.process.start(
            "python /app/src/main.py",
            ports=[8080]
        )
        
        # Get sandbox URL
        sandbox_url = sandbox.get_hostname(8080)
        print(f"API server running at: https://{sandbox_url}")
        
        # Keep sandbox alive
        print("Sandbox deployed. Press Ctrl+C to stop...")
        server_process.wait()
        
    finally:
        sandbox.close()
```

#### 4. Frontend Deployment

**Option 1: Static Hosting (GitHub Pages, Netlify, Vercel)**
```bash
# Build for production
cd frontend
# If using build tools, build first

# Deploy to Netlify
netlify deploy --prod --dir=.

# Or deploy to Vercel
vercel --prod
```

**Option 2: Serve from E2B Sandbox**
```python
# Add static file serving to FastAPI
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
```

### Monitoring & Logging

#### 1. Application Logging

**File:** `backend/src/utils/logging.py`
```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """Setup application logging."""
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
```

#### 2. Health Monitoring

Add health check endpoint that verifies:
- Database connectivity
- Agent availability
- LLM API connectivity
- Recent data freshness

#### 3. Metrics Collection

Track key metrics:
- Workflow execution time
- Data collection success rate
- Analysis quality scores
- API response times
- Error rates

### Troubleshooting Guide

#### Common Issues

1. **Agents Not Accessible**
   - Check agent URLs are correct
   - Verify agents are running
   - Check network connectivity
   - Review Docker MCP Hub configuration

2. **Database Errors**
   - Verify database file permissions
   - Check disk space
   - Review database schema initialization

3. **LLM API Errors**
   - Verify API keys are set
   - Check API rate limits
   - Review API quota/usage

4. **Workflow Timeouts**
   - Increase timeout values
   - Check agent response times
   - Optimize data processing

### Performance Optimization

1. **Caching**
   - Cache LLM responses where possible
   - Cache agent responses
   - Use database indexes

2. **Parallel Processing**
   - Collect from all agents in parallel
   - Process enrichment in batches
   - Parallelize analysis where possible

3. **Data Limits**
   - Limit data processed per run
   - Use pagination for large datasets
   - Clean old data periodically

### Deliverables

1. Complete testing strategy (unit, integration, e2e)
2. Deployment scripts for all components
3. E2B sandbox deployment guide
4. Docker agent deployment instructions
5. Frontend deployment options
6. Monitoring and logging setup
7. Troubleshooting guide
8. Performance optimization recommendations

### Next Steps

After completing integration and deployment:

1. **Run Full System Test**
   - Deploy all components
   - Execute end-to-end workflow
   - Verify all outputs

2. **Monitor Production**
   - Set up logging and monitoring
   - Track metrics and errors
   - Optimize based on usage

3. **Iterate and Improve**
   - Collect feedback
   - Enhance analysis quality
   - Add new data sources
   - Improve UI/UX

## Summary

This integration guide completes the full Startup Intelligence Agent system. You now have:

✅ All data collector agents (news-scraper, startup-api, github-monitor)
✅ Orchestrator agent with full workflow
✅ Enrichment and analysis agents
✅ Summarizer and output agent
✅ FastAPI HTTP server
✅ Frontend UI dashboard
✅ Complete deployment guide

The system is ready for production deployment and use!
