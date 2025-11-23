# Core Workflow: Next Steps

## ✅ Completed Steps

### 1. Data Collection ✅
- **News Scraper Agent**: Collecting from TechCrunch, HackerNews, ProductHunt
- **Startup API Agent**: Collecting funding rounds and launches
- **GitHub Monitor Agent**: Tracking trending repos and technical signals
- **Status**: All agents running and collecting data

### 2. Data Storage ✅
- SQLite database with all required tables
- Data persistence working correctly
- GitHub signals field mapping fixed

### 3. Data Enrichment ✅
- Enrichment agent implemented
- Cross-referencing and metadata addition
- Enrichment tracking in database

### 4. Workflow Reporting ✅
- **WorkflowReporter** class created
- API endpoints for monitoring:
  - `/workflow/health` - Health status
  - `/workflow/report` - Workflow summary
  - `/workflow/daily-report` - Daily reports
- Data quality metrics
- Enrichment rate tracking

## 🔄 Current Status

### Working Components
- ✅ Data collection from all 3 agents
- ✅ Data storage in SQLite
- ✅ Data enrichment
- ✅ Workflow reporting and monitoring
- ✅ API endpoints for workflow control
- ✅ Frontend dashboard

### Pending/Issues
- ⚠️ LLM API endpoint (404 error) - needs configuration
- ⚠️ Analysis/Summarization - requires LLM API key
- ⚠️ Server restart needed to load new reporting endpoints

## 🚀 Next Steps

### Step 1: Restart Server (Required)
The new workflow reporting endpoints need the server to be restarted:

```bash
# Stop current server (if running)
pkill -f "python.*main.py"

# Start server
cd startup-intelligence-agent/backend/src
python3 main.py
```

### Step 2: Test Workflow Reporting
```bash
# Run test script
python3 test_workflow_reporting.py

# Or test manually
curl http://localhost:8080/workflow/health | python3 -m json.tool
curl "http://localhost:8080/workflow/report?days=7" | python3 -m json.tool
curl http://localhost:8080/workflow/daily-report | python3 -m json.tool
```

### Step 3: Configure LLM API (For Analysis/Summarization)
If you want full workflow with analysis and summarization:

1. **Get API Key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. **Configure**:
   ```bash
   cd startup-intelligence-agent
   # Edit .env file
   LLM_PROVIDER=anthropic  # or openai
   LLM_MODEL=claude-3-sonnet-20240229  # or gpt-4-turbo-preview
   ANTHROPIC_API_KEY=your_key_here  # or OPENAI_API_KEY
   ```

3. **Restart Server**:
   ```bash
   cd backend/src
   python3 main.py
   ```

### Step 4: Run Full Workflow
```bash
# Trigger full workflow
curl -X POST http://localhost:8080/orchestrator/run

# Check status
curl http://localhost:8080/workflow/health | python3 -m json.tool

# Get briefing
curl http://localhost:8080/briefing | python3 -m json.tool
```

### Step 5: Monitor Workflow
```bash
# Watch health status
watch -n 60 'curl -s http://localhost:8080/workflow/health | python3 -m json.tool'

# Get weekly report
curl "http://localhost:8080/workflow/report?days=7" | python3 -m json.tool
```

## 📊 Workflow Monitoring

### Health Check
Monitor system health:
```bash
curl http://localhost:8080/workflow/health
```

**Health Indicators:**
- `status`: "healthy" or "degraded"
- `data_collection.last_24h`: Recent data counts
- `workflow.last_briefing`: Last briefing date
- `workflow.briefing_age_hours`: Age of latest briefing

### Daily Reports
Get daily statistics:
```bash
curl http://localhost:8080/workflow/daily-report
```

**Report Includes:**
- Data collection counts
- Workflow execution status
- Data quality metrics
- Enrichment statistics

### Weekly Reports
Get weekly summary:
```bash
curl "http://localhost:8080/workflow/report?days=7"
```

**Summary Includes:**
- Total data collected
- Workflow executions
- Enrichment rates
- Performance metrics

## 🔧 Troubleshooting

### Endpoints Return 404
**Issue**: New endpoints not found
**Solution**: Restart the server to load new routes

### LLM API 404 Error
**Issue**: `Client error '404 Not Found'` from Anthropic API
**Solution**: 
1. Check API key is set correctly
2. Verify model name is correct
3. Check Anthropic API version header

### No Data in Reports
**Issue**: Reports show 0 counts
**Solution**:
1. Run data collection: `curl -X POST http://localhost:8080/orchestrator/collect`
2. Check data collector agents are running
3. Verify database has data

## 📚 Documentation

- **WORKFLOW_REPORTING.md** - Complete reporting guide
- **TESTING_GUIDE.md** - Testing instructions
- **LLM_API_SETUP.md** - LLM configuration guide

## 🎯 Workflow Flow

```
1. Collect Data
   ├─ News Scraper → News Articles
   ├─ Startup API → Funding & Launches
   └─ GitHub Monitor → Repos & Signals

2. Store Data
   └─ SQLite Database

3. Enrich Data
   └─ Add metadata, cross-reference

4. Analyze Data
   └─ LLM-based analysis (requires API key)

5. Summarize
   └─ Generate briefing (requires API key)

6. Report
   └─ Workflow statistics & monitoring
```

## ✅ Ready to Proceed

The workflow reporting system is ready! Next steps:

1. **Restart server** to load new endpoints
2. **Test reporting** endpoints
3. **Configure LLM** (optional, for full workflow)
4. **Monitor workflow** using reporting endpoints

---

**Status**: Workflow reporting system complete! 🎉

