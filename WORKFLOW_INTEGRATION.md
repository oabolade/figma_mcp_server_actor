# Workflow Integration Guide

## Overview

This guide covers the end-to-end workflow integration: **collect → enrich → analyze → summarize**

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│                    (E2B Sandbox)                             │
│                                                              │
│  Manages workflow: collect → enrich → analyze → summarize   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ News       │ │ Startup    │ │ GitHub     │
│ Scraper    │ │ API        │ │ Monitor    │
│ Port 3001  │ │ Port 3002  │ │ Port 3003  │
└────────────┘ └────────────┘ └────────────┘
     │               │               │
     └───────────────┴───────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    SQLite Database    │
         │   (In-Sandbox Store)  │
         └───────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Enrichment │ │  Analysis  │ │ Summarizer │
│   Agent    │ │   Agent    │ │   Agent    │
└────────────┘ └────────────┘ └────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   FastAPI Server      │
         │     Port 8080         │
         │   /briefing endpoint  │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    Frontend UI        │
         │   HTML/JS Dashboard   │
         └───────────────────────┘
```

## Workflow Steps

### Step 1: Data Collection

The orchestrator calls all three data collector agents in parallel:

```python
# News Scraper
GET http://localhost:3001/all?limit=20&hours=24

# Startup API
GET http://localhost:3002/funding?days=7
GET http://localhost:3002/launches?days=7

# GitHub Monitor
GET http://localhost:3003/trending?since=daily&limit=25
GET http://localhost:3003/signals?days=7&keywords=startup,AI,tech
```

**Expected Results:**
- News articles from TechCrunch, HackerNews, ProductHunt
- Funding rounds and product launches
- Trending repositories and technical signals

### Step 2: Data Storage

All collected data is stored in SQLite database:

- `news` table - Articles
- `funding` table - Funding rounds
- `launches` table - Product launches
- `github_repositories` table - Trending repos
- `github_signals` table - Technical signals

### Step 3: Data Enrichment

EnrichmentAgent processes stored data:

- Adds metadata (keywords, categories, entities)
- Cross-references related items
- Links articles to funding/launches
- Identifies sentiment and topics

### Step 4: Analysis

AnalysisAgent uses LLM to analyze enriched data:

- Clusters trends
- Detects patterns
- Identifies opportunities
- Extracts competitor moves

**Requirements:**
- LLM API key must be configured
- Provider: OpenAI or Anthropic
- Model: gpt-4-turbo-preview or claude-3-opus-20240229

### Step 5: Summarization

SummarizerAgent generates daily briefing:

- Executive summary
- Trend clusters
- Opportunity matches
- Intelligence threads

## Testing the Workflow

### Quick Test

```bash
# Test all data collectors
./test_data_collectors.sh

# Test data collection only
python3 test_full_workflow.py
# (Step 1 & 2)

# Test full workflow
curl -X POST "http://localhost:8080/orchestrator/run?days_back=7"
```

### Step-by-Step Testing

```bash
# 1. Test data collectors individually
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health

# 2. Test data collection
curl -X POST http://localhost:8080/orchestrator/collect

# 3. Check workflow status
curl http://localhost:8080/orchestrator/status

# 4. Test full workflow
curl -X POST "http://localhost:8080/orchestrator/run?days_back=7"

# 5. Check database stats
curl http://localhost:8080/data/stats

# 6. Get briefing
curl http://localhost:8080/briefing | python3 -m json.tool
```

## Current Status

### ✅ Working Components

1. **Data Collection**
   - All 3 agents responding correctly
   - Data being collected successfully
   - Parallel collection working

2. **Data Storage**
   - Articles stored in database
   - Funding/launches stored correctly
   - GitHub repos stored successfully

3. **Data Enrichment**
   - Enrichment process running
   - Metadata being added
   - Cross-referencing working

4. **API Server**
   - All endpoints responding
   - Health checks passing
   - Frontend serving correctly

### ⚠️  Configuration Required

1. **LLM API Key**
   - Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`
   - Required for analysis and summarization steps
   - Without it, these steps will fail gracefully

2. **LLM API Endpoint** (if using Anthropic)
   - Verify API endpoint URL is correct
   - Check anthropic-version header

## Environment Configuration

Ensure your `.env` file has:

```env
# LLM Configuration
LLM_PROVIDER=anthropic  # or openai
LLM_MODEL=claude-3-5-sonnet-20241022  # or gpt-4-turbo-preview
ANTHROPIC_API_KEY=your-api-key  # or OPENAI_API_KEY

# Data Collector Agents
NEWS_SCRAPER_URL=http://localhost:3001
STARTUP_API_URL=http://localhost:3002
GITHUB_MONITOR_URL=http://localhost:3003

# Database
DATABASE_PATH=./storage/intelligence.db

# Server
HOST=127.0.0.1
PORT=8080
```

## Troubleshooting

### Data Collectors Not Responding

```bash
# Check if containers are running
cd data-collector-agents
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Workflow Stuck

```bash
# Check workflow status
curl http://localhost:8080/orchestrator/status

# Check server logs
tail -f /tmp/server.log

# Check database
sqlite3 storage/intelligence.db "SELECT COUNT(*) FROM news;"
```

### LLM Errors

```bash
# Verify API key is set
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:10] + '...' if os.getenv('ANTHROPIC_API_KEY') else 'Not set')"

# Test LLM connection
cd startup-intelligence-agent/backend/src
python3 -c "from llm.client import LLMClient; import asyncio; client = LLMClient('anthropic', 'claude-3-5-sonnet-20241022', os.getenv('ANTHROPIC_API_KEY')); print(asyncio.run(client.complete('Hello')))"
```

## Next Steps

1. **Configure LLM API Key**
   - See `LLM_API_SETUP.md` for detailed instructions
   - Test API connection
   - Verify model availability

2. **Run Full Workflow**
   - Execute: `curl -X POST http://localhost:8080/orchestrator/run`
   - Monitor logs
   - Check database for results

3. **View Results**
   - Access briefing: http://localhost:8080/briefing
   - Open frontend: http://localhost:8080/
   - Check analysis: http://localhost:8080/analysis/latest

4. **Integration Testing**
   - Test all workflow steps
   - Verify data quality
   - Check error handling

5. **Production Deployment**
   - Deploy to E2B sandbox
   - Set up monitoring
   - Configure scheduling

---

**Ready to run!** 🚀

