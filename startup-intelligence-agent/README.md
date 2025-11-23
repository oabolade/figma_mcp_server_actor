# Startup Intelligence Agent

An agentic system for collecting, analyzing, and summarizing startup intelligence from multiple sources (news, funding, launches, GitHub activity) using LLM-powered analysis.

## Architecture

This system runs inside an E2B sandbox and orchestrates multiple Docker MCP Hub agents to:

1. **Collect** data from news sources, startup APIs, and GitHub
2. **Enrich** collected data with metadata and cross-references
3. **Analyze** patterns and trends using LLM
4. **Summarize** insights into daily briefings

## Project Structure

```
startup-intelligence-agent/
├── backend/
│   ├── src/
│   │   ├── orchestrator/    # Main workflow orchestrator
│   │   ├── analysis/        # LLM-powered analysis agent
│   │   ├── summarizer/      # Briefing generation agent
│   │   ├── enrichment/      # Data enrichment agent
│   │   ├── database/        # SQLite database module
│   │   ├── api/            # FastAPI HTTP server
│   │   ├── config/         # Configuration management
│   │   └── llm/            # LLM client (OpenAI/Anthropic)
│   └── requirements.txt
├── tools/                   # Docker MCP Hub agents
│   ├── news-scraper/
│   ├── startup-api-wrapper/
│   └── github-monitor/
├── frontend/               # Dashboard UI (to be implemented)
└── storage/                # Local database storage

```

## Setup

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. **Create and activate a virtual environment:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

```bash
cp ../.env.example ../.env
# Edit .env with your API keys and configuration
```

4. **Set up the environment variables:**

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - Your LLM provider API key
- `LLM_PROVIDER` - Either "openai" or "anthropic"
- `LLM_MODEL` - Model identifier (e.g., "gpt-4-turbo-preview")
- `NEWS_SCRAPER_URL` - URL of news scraper agent (default: http://localhost:3001)
- `STARTUP_API_URL` - URL of startup API agent (default: http://localhost:3002)
- `GITHUB_MONITOR_URL` - URL of GitHub monitor agent (default: http://localhost:3003)
- `DATABASE_PATH` - Path to SQLite database (default: ./storage/intelligence.db)

## Running the Server

### Basic Server

```bash
cd backend/src
python main.py
```

Or using uvicorn directly:

```bash
cd backend/src
uvicorn api.server:app --host 0.0.0.0 --port 8080
```

### Test Endpoints

Once the server is running:

```bash
# Health check
curl http://localhost:8080/health

# Server info
curl http://localhost:8080/info

# Briefing (will return 404 until workflow is run)
curl http://localhost:8080/briefing
```

## Development Status

### ✅ Completed
- Project structure setup
- Configuration management
- FastAPI server with basic endpoints
- LLM client (OpenAI/Anthropic)
- Agent skeletons (orchestrator, analysis, summarizer, enrichment)

### 🚧 In Progress
- Database schema and implementation
- Orchestrator workflow implementation
- Data collector agent integration

### 📋 TODO
- Database module implementation (see `06-database-setup.md`)
- Orchestrator agent implementation (see `05-orchestrator-agent.md`)
- Enrichment agent implementation (see `07-enrichment-agent.md`)
- Analysis agent implementation (see `08-analysis-agent.md`)
- Summarizer agent implementation (see `09-summarizer-agent.md`)
- Docker MCP Hub agents (news-scraper, startup-api, github-monitor)
- Frontend dashboard UI

## Next Steps

1. **Database Setup**: Implement the database module following `workflow-prompts/06-database-setup.md`
2. **Orchestrator**: Complete the orchestrator implementation following `workflow-prompts/05-orchestrator-agent.md`
3. **Data Collector Agents**: Build the Docker MCP Hub agents:
   - News scraper (`02-docker-mcp-news-scraper.md`)
   - Startup API wrapper (`03-docker-mcp-startup-api-wrapper.md`)
   - GitHub monitor (`04-docker-mcp-github-monitor-agent.md`)

## Workflow Prompts

All detailed implementation prompts are available in the `workflow-prompts/` directory:

- `00-overview.md` - System architecture overview
- `01-project-bootstrap.md` - Project setup (this phase)
- `02-docker-mcp-news-scraper.md` - News scraper agent
- `03-docker-mcp-startup-api-wrapper.md` - Startup API agent
- `04-docker-mcp-github-monitor-agent.md` - GitHub monitor agent
- `05-orchestrator-agent.md` - Orchestrator workflow
- `06-database-setup.md` - Database schema and setup
- `07-enrichment-agent.md` - Data enrichment
- `08-analysis-agent.md` - Analysis with LLM
- `09-summarizer-agent.md` - Briefing generation
- `10-api-endpoints.md` - API endpoints
- `11-frontend-ui.md` - Frontend dashboard
- `12-integration-deployment.md` - Testing and deployment

## License

[Specify license]

## Contributing

[Contributing guidelines]

