# Startup Intelligence Agent - Hackathon Submission

## 🚀 Project Overview

An **Agentic Startup Intelligence System** that automatically collects, enriches, analyzes, and summarizes startup ecosystem data using AI agents running in E2B sandboxes.

## ✨ Key Features

- **🤖 Multi-Agent Architecture**: Orchestrator coordinates data collection, enrichment, analysis, and summarization
- **📊 Real-Time Intelligence**: Collects data from news, funding rounds, product launches, and GitHub activity
- **🧠 AI-Powered Analysis**: LLM-based trend detection and opportunity identification
- **📈 Interactive Dashboard**: Beautiful web UI displaying insights, trends, and opportunities
- **☁️ Cloud-Ready**: Deployable to E2B sandboxes with Docker MCP Hub integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Orchestrator Agent (E2B Sandbox)                       │
│  Manages: collect → enrich → analyze → summarize        │
└────────────┬────────────────────────────────────────────┘
             │
             ├─→ Data Collector Agents (Docker)
             │   • news-scraper
             │   • startup-api
             │   • github-monitor
             │
             ├─→ Enrichment Agent
             │   • Metadata extraction
             │   • Entity recognition
             │   • Sentiment analysis
             │
             ├─→ Analysis Agent (LLM)
             │   • Trend clustering
             │   • Pattern detection
             │   • Opportunity extraction
             │
             └─→ Summarizer Agent (LLM)
                 • Daily briefings
                 • Intelligence threads
                 • Structured insights
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLite
- **AI/LLM**: OpenAI, Anthropic Claude
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Infrastructure**: E2B Sandboxes, Docker, Docker Compose
- **Testing**: pytest, 46/47 tests passing (98%)

## 📦 Quick Start

### Prerequisites
- Python 3.14+
- Docker & Docker Compose
- LLM API Key (OpenAI or Anthropic)

### Installation

```bash
# Clone repository
git clone https://github.com/oabolade/figma_mcp_server_actor.git
cd figma_mcp_server_actor

# Setup backend
cd startup-intelligence-agent/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys

# Start data collector agents
cd ../../data-collector-agents
docker-compose up -d

# Start main server
cd ../../startup-intelligence-agent/backend/src
python main.py
```

### Access the Dashboard

Open your browser to: **http://localhost:8080/**

## 🎯 Demo Features

1. **Real-Time Data Collection**: Automatically scrapes news, funding, launches
2. **AI Analysis**: Identifies trends and opportunities using LLM
3. **Interactive Dashboard**: Beautiful UI with trends, funding, opportunities
4. **Intelligence Threads**: Deep-dive analysis on key topics

## 📊 Test Results

- ✅ **Unit Tests**: 29/29 passing (100%)
- ✅ **Integration Tests**: 13/13 passing (100%)
- ✅ **E2E Tests**: 4/5 passing (80%)
- 📈 **Test Coverage**: 34%

## 🔗 Links

- **Repository**: https://github.com/oabolade/figma_mcp_server_actor
- **API Docs**: http://localhost:8080/docs (when running)
- **Dashboard**: http://localhost:8080/ (when running)

## 📝 Documentation

- [README.md](README.md) - Main documentation
- [TESTING.md](TESTING.md) - Testing guide
- [E2B_INTEGRATION.md](startup-intelligence-agent/E2B_INTEGRATION.md) - Deployment guide

## 🎉 Hackathon Highlights

- **Innovation**: Multi-agent AI system with autonomous workflow
- **Completeness**: Full-stack implementation with testing
- **Production-Ready**: E2B sandbox deployment, Docker integration
- **User Experience**: Beautiful, responsive dashboard

## 👤 Author

Built for hackathon submission

## 📄 License

See LICENSE file for details
