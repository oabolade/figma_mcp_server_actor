# Prompt 1: Project Bootstrap

## Objective

Create a minimal full-stack project structure for the "Startup Intelligence Agent" system with all foundational components in place.

## Requirements

### Project Structure
```
startup-intelligence-agent/
├── backend/
│   ├── src/
│   │   ├── orchestrator/
│   │   │   └── agent.py
│   │   ├── analysis/
│   │   │   └── agent.py
│   │   ├── summarizer/
│   │   │   └── agent.py
│   │   ├── database/
│   │   │   └── db.py
│   │   ├── api/
│   │   │   └── server.py
│   │   └── config/
│   │       └── settings.py
│   ├── requirements.txt
│   └── Dockerfile (optional for E2B)
├── tools/
│   ├── news-scraper/
│   └── startup-api-wrapper/
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── .env.example
├── README.md
└── docker-compose.yml (for local MCP tools)
```

### Backend Setup

**Technology Stack:**
- Python 3.11+ (for E2B sandbox compatibility)
- FastAPI for HTTP endpoints
- SQLite for local database
- OpenAI/Anthropic SDK for LLM integration

**Initial Dependencies:**
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
httpx==0.25.1
python-dotenv==1.0.0
openai==1.3.0
anthropic==0.7.0
```

**Core Components to Create:**

1. **Configuration Manager** (`config/settings.py`)
   - Load environment variables
   - E2B sandbox configuration
   - Docker MCP Hub tool URLs
   - LLM API keys and settings

2. **Database Module** (`database/db.py`)
   - SQLite connection setup
   - Table definitions (news, funding, launches)
   - Basic CRUD operations
   - Schema initialization

3. **API Server** (`api/server.py`)
   - FastAPI app initialization
   - `/briefing` endpoint (initially returns placeholder)
   - `/health` endpoint
   - CORS configuration for frontend

4. **Orchestrator Agent** (`orchestrator/agent.py`)
   - Basic structure with workflow steps
   - Placeholder for Docker MCP tool calls
   - Data storage coordination

5. **Analysis Agent** (`analysis/agent.py`)
   - LLM client initialization
   - Basic analysis framework
   - Placeholder for analysis logic

6. **Summarizer Agent** (`summarizer/agent.py`)
   - LLM client initialization
   - JSON structure templates
   - Placeholder for summarization logic

### E2B Sandbox Configuration

**Sandbox Requirements:**
- Python 3.11+
- SQLite support
- HTTP server capabilities
- Environment variable access

**Entry Point:**
```python
# backend/src/main.py
from api.server import create_app

if __name__ == "__main__":
    app = create_app()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Docker MCP Hub Integration Points

**Agent URLs (placeholder):**
- `NEWS_SCRAPER_URL`: http://localhost:3001 (local) or Docker service URL
- `STARTUP_API_URL`: http://localhost:3002 (local) or Docker service URL
- `GITHUB_MONITOR_URL`: http://localhost:3003 (local) or Docker service URL

**HTTP Client Setup:**
- Use `httpx` for async HTTP requests
- Retry logic for tool calls
- Error handling for unavailable tools

### Environment Variables

Create `.env.example` with:
```env
# LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-4-turbo-preview  # or claude-3-opus-20240229

# Docker MCP Hub Agents
NEWS_SCRAPER_URL=http://localhost:3001
STARTUP_API_URL=http://localhost:3002
GITHUB_MONITOR_URL=http://localhost:3003

# Database
DATABASE_PATH=./storage/intelligence.db

# E2B Sandbox
E2B_API_KEY=your-e2b-key
SANDBOX_ID=your-sandbox-id

# Server
PORT=8080
HOST=0.0.0.0
```

### Initial Implementation Checklist

- [ ] Create project directory structure
- [ ] Set up Python virtual environment
- [ ] Create `requirements.txt` with all dependencies
- [ ] Implement configuration manager with env loading
- [ ] Create SQLite database module with schema
- [ ] Set up FastAPI server with `/briefing` and `/health` endpoints
- [ ] Create orchestrator agent skeleton
- [ ] Create analysis agent skeleton
- [ ] Create summarizer agent skeleton
- [ ] Add `.env.example` file
- [ ] Create README with setup instructions
- [ ] Test that server starts and endpoints respond

### Testing

**Basic Smoke Test:**
```bash
# Start the server
cd backend
python src/main.py

# In another terminal
curl http://localhost:8080/health
# Should return: {"status": "ok"}

curl http://localhost:8080/briefing
# Should return placeholder JSON structure
```

### Deliverables

1. Complete project structure as specified
2. All core modules with placeholder implementations
3. Working FastAPI server with basic endpoints
4. Database schema defined and initializable
5. Configuration system with environment variable support
6. README with setup and run instructions

### Next Steps

After completing this bootstrap, proceed to build the Data Collector Agents:
- **02-docker-mcp-news-scraper-agent.md** - Build the news scraper agent
- **03-docker-mcp-startup-api-agent.md** - Build the startup API agent
- **04-docker-mcp-github-monitor-agent.md** - Build the GitHub monitor agent

Then proceed to:
- **05-orchestrator-agent.md** - Integrate all agents and orchestrate workflow
- **06-database-setup.md** - Set up database schema including GitHub signals
