# Startup Intelligence Agent System - Overview

## System Architecture

This document outlines the complete architecture and workflow for building an Agentic Startup Intelligence System using:
- **E2B Sandboxes** (agent runtime environment)
- **Docker MCP Hub** (tooling integration layer)
- **Cursor Vibe Coding** (autonomous code generation)

## Core Components

### 1. Orchestrator Agent (E2B Sandbox)
- Main coordination agent running **inside E2B sandbox**
- Manages sub-agents and workflow coordination
- Calls Data Collector Agents via Docker MCP Hub
- Runs the complete workflow loop: **collect → enrich → analyze → summarize**
- Coordinates all components and manages the pipeline

### 2. Data Collector Agents (Docker MCP Hub)
**Running inside Docker containers via Docker MCP Hub** - These are autonomous agents, not just tools:

**news-scraper Agent**
- Running in Docker container (via Docker MCP Hub)
- Scrapes: TechCrunch, HackerNews, ProductHunt
- Extracts structured article data
- Exposes HTTP/API endpoints for E2B sandbox consumption

**startup-api Agent**
- Running in Docker container (via Docker MCP Hub)
- Wrapper for multiple APIs: Crunchbase, AngelList, Dealroom, ProductHunt
- Aggregates startup activity signals (funding, launches, events)
- Provides structured startup intelligence data

**github-monitor Agent**
- Running in Docker container (via Docker MCP Hub)
- Tracks trending repositories for technical signals
- Monitors GitHub activity for startup/tech indicators
- Identifies emerging technologies and developer trends

### 3. Data Store (Local - In-Sandbox)
- **SQLite or ChromaDB** database running inside E2B sandbox
- In-memory/local persistence within the sandbox
- Stores collected items: funding news, launches, competitor updates, GitHub signals
- Provides fast access for analysis agents

### 4. Analysis Agent (LLM in E2B Sandbox)
- LLM operating **inside E2B sandbox**
- Processes collected and enriched data
- Clusters trends and identifies patterns
- Extracts insights, categories, and changes
- Identifies opportunities and competitor movements

### 5. Summarizer + Output Agent (E2B Sandbox)
- Generates daily briefing JSON
- Creates trend clusters with structured output
- Matches opportunities for founders and investors
- Produces searchable intelligence threads
- Formats output for UI consumption

### 6. UI / Frontend Prototype
- Simple HTML/JS file or minimal Next.js page
- Optional: Chat-like interface using a single API route
- Pulls from sandbox API endpoint (`/briefing`)
- Displays intelligence dashboard with all insights

## End-to-End Workflow Loop

```
┌─────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR AGENT (E2B Sandbox)                                │
│ Manages workflow: collect → enrich → analyze → summarize        │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Calls Data Collector Agents via Docker MCP Hub
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ DATA COLLECTOR AGENTS (Docker Containers via MCP Hub)           │
│                                                                  │
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐│
│ │ news-scraper    │  │ startup-api     │  │ github-monitor   ││
│ │ Agent           │  │ Agent           │  │ Agent            ││
│ │                 │  │                 │  │                  ││
│ │ • TechCrunch    │  │ • Crunchbase    │  │ • Trending repos ││
│ │ • HackerNews    │  │ • AngelList     │  │ • Tech signals   ││
│ │ • ProductHunt   │  │ • Dealroom      │  │ • Dev trends     ││
│ │                 │  │ • ProductHunt   │  │                  ││
│ └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘│
└──────────┼─────────────────────┼────────────────────┼──────────┘
           │                     │                    │
           │ Returns structured data to sandbox       │
           └─────────────────────┴────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ DATA STORE (In-Sandbox: SQLite/ChromaDB)                        │
│                                                                  │
│ • news table                                                    │
│ • funding table                                                 │
│ • launches table                                                │
│ • github_signals table                                          │
│ • competitor_updates table                                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ ENRICHMENT STEP (Optional but Recommended)                      │
│                                                                  │
│ • Add metadata and context                                      │
│ • Cross-reference data sources                                  │
│ • Enhance with additional signals                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ ANALYSIS AGENT (LLM in E2B Sandbox)                             │
│                                                                  │
│ • Cluster items into trends                                    │
│ • Detect emerging sectors                                      │
│ • Identify competitor moves                                    │
│ • Extract opportunities for founders/investors                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ SUMMARIZER + OUTPUT AGENT (E2B Sandbox)                         │
│                                                                  │
│ • Generate daily briefing JSON                                 │
│ • Create trend clusters                                        │
│ • Match opportunities                                          │
│ • Produce searchable intelligence threads                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ API ENDPOINT: /briefing (E2B Sandbox HTTP Server)               │
│                                                                  │
│ Returns structured JSON with all insights                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND UI (HTML/JS or Next.js)                                │
│                                                                  │
│ • Fetches /briefing endpoint                                   │
│ • Displays intelligence dashboard                              │
│ • Shows trends, opportunities, updates                         │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Prompts Structure

The following prompts guide the development of each component in sequence:

**Phase 1: Foundation**
1. **01-project-bootstrap.md** - Initial project setup and E2B sandbox structure

**Phase 2: Data Collector Agents (Docker MCP Hub)**
2. **02-docker-mcp-news-scraper.md** - News scraper agent (Docker container)
3. **03-docker-mcp-startup-api-wrapper.md** - Startup API agent (Docker container)
4. **04-docker-mcp-github-monitor-agent.md** - GitHub monitor agent (Docker container)

**Phase 3: Orchestration & Storage**
5. **05-orchestrator-agent.md** - Main orchestrator agent workflow
6. **06-database-setup.md** - SQLite/ChromaDB database schema and setup
7. **07-enrichment-agent.md** - Data enrichment and enhancement step

**Phase 4: Analysis & Summarization**
8. **08-analysis-agent.md** - Analysis agent with prompt templates
9. **09-summarizer-agent.md** - Summarizer + output agent implementation

**Phase 5: API & Frontend**
10. **10-api-endpoints.md** - FastAPI endpoints and HTTP server in E2B
11. **11-frontend-ui.md** - Frontend dashboard UI

**Phase 6: Integration & Deployment**
12. **12-integration-deployment.md** - Integration testing and deployment

## Technology Stack

- **Runtime**: E2B Sandboxes (Python/Node.js)
- **Data Collectors**: Docker containers (via Docker MCP Hub)
- **Database**: SQLite or ChromaDB (in-sandbox, in-memory)
- **API Framework**: FastAPI (Python) for E2B sandbox HTTP server
- **LLM Integration**: OpenAI API / Anthropic API
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript (or Next.js)
- **Tooling**: Docker MCP Hub for agent integration
- **Development**: Cursor Vibe Coding

## Expected Output Structure

```json
{
  "summary": "Daily intelligence summary text",
  "trends": [
    {
      "title": "Trend name",
      "description": "Trend description",
      "signals": ["signal1", "signal2"]
    }
  ],
  "funding_rounds": [
    {
      "name": "Company name",
      "amount": "$10M",
      "type": "Series A",
      "date": "2024-01-15",
      "link": "url"
    }
  ],
  "product_launches": [
    {
      "name": "Product name",
      "description": "Product description",
      "date": "2024-01-15",
      "link": "url"
    }
  ],
  "opportunities_for_founders": [
    {
      "title": "Opportunity title",
      "description": "Opportunity description",
      "reasoning": "Why this is an opportunity"
    }
  ],
  "opportunities_for_investors": [
    {
      "title": "Opportunity title",
      "description": "Opportunity description",
      "reasoning": "Investment thesis"
    }
  ]
}
```

## Next Steps

Follow the workflow prompts in numerical order to build the complete system. Each prompt is self-contained but builds upon previous components.
