# E2B Sandbox Integration Guide

This guide explains how to deploy and run the Startup Intelligence Agent system in E2B sandboxes.

## Overview

E2B sandboxes provide secure, isolated cloud environments for running the orchestrator agent and all its components. The system is designed to run entirely within an E2B sandbox, with data collector agents running as Docker containers that the sandbox connects to.

## Prerequisites

1. **E2B Account**: Sign up at [https://e2b.dev](https://e2b.dev)
2. **E2B API Key**: Get your API key from the E2B dashboard
3. **Python 3.11+**: For running deployment scripts locally

## Setup

### 1. Install E2B SDK

The E2B SDK is already included in `requirements.txt`. Install it:

```bash
cd startup-intelligence-agent/backend
pip install -r requirements.txt
```

Or install directly:

```bash
pip install e2b
```

### 2. Configure Environment Variables

Add your E2B API key to `.env`:

```bash
# E2B Sandbox
E2B_API_KEY=your-e2b-api-key-here
E2B_TEMPLATE=base  # Optional: E2B template name (default: "base")
                   # Common templates: "base", "ubuntu", "python3"
                   # The system will automatically try fallback templates if the primary fails
SANDBOX_ID=  # Optional: kept for future compatibility (not currently used)
```

**Important:** 
- Get your API key from [https://e2b.dev/docs/api-key](https://e2b.dev/docs/api-key)
- Do NOT include quotes around the API key value
- Ensure there are no extra spaces before or after the key
- The API key should be a long string (typically 40+ characters)

**Template Selection:**
- If you encounter a `403: Team does not have access to the template` error, the system will automatically try fallback templates in this order:
  1. Your specified `E2B_TEMPLATE` (or "base" if not set)
  2. "base" template
  3. "python3" template
- The first accessible template will be used. If all fail, you'll get a helpful error message with troubleshooting tips.
- To use a specific template, set `E2B_TEMPLATE` in your `.env` file (e.g., `E2B_TEMPLATE=base`)

**Verify Template Access:**
Before deploying, you can verify which templates your account can access:
```bash
python scripts/verify_e2b_templates.py
```
This script will test multiple templates and show which ones are accessible with your API key.

**Verify your API key:**
```bash
python scripts/verify_e2b_key.py
```

Or test manually:
```bash
curl -X GET "https://api.e2b.dev/sandboxes" -H "X-API-Key: YOUR_API_KEY"
```

### 3. Deploy to E2B

Run the deployment script:

```bash
cd startup-intelligence-agent
python scripts/deploy_to_e2b.py
```

Or from the backend directory:

```bash
cd backend/src
python -m sandbox_integration.client  # If running as module
```

**Note:** E2B sandboxes are ephemeral - each deployment creates a new sandbox. The `SANDBOX_ID` environment variable is kept for future compatibility but is not currently used, as the E2B SDK doesn't support reconnecting to existing sandboxes.

## Deployment Process

The deployment script performs the following steps:

1. **Create/Connect Sandbox**: Creates a new sandbox or reconnects to an existing one
2. **Upload Code**: Uploads all backend Python files to `/app` in the sandbox
3. **Upload Dependencies**: Uploads `requirements.txt`
4. **Set Environment Variables**: Configures all necessary environment variables
5. **Install Dependencies**: Runs `pip install -r requirements.txt` in the sandbox
6. **Start Server**: Starts the FastAPI server on port 8080
7. **Expose Port**: Makes the server accessible via E2B's public URL

## Architecture

```
┌─────────────────────────────────────────┐
│         E2B Sandbox                     │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Orchestrator Agent                │ │
│  │  - FastAPI Server (port 8080)      │ │
│  │  - Database (SQLite)               │ │
│  │  - Enrichment Agent                │ │
│  │  - Analysis Agent                   │ │
│  │  - Summarizer Agent                 │ │
│  └───────────────────────────────────┘ │
│           │                             │
│           │ HTTP Requests               │
│           ▼                             │
└───────────┼─────────────────────────────┘
            │
            │ Calls Docker MCP Hub Agents
            │
┌───────────┼─────────────────────────────┐
│           ▼                               │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │ news-scraper    │  │ startup-api  │  │
│  │ (Docker)        │  │ (Docker)     │  │
│  └─────────────────┘  └──────────────┘  │
│  ┌─────────────────┐                    │
│  │ github-monitor  │                    │
│  │ (Docker)        │                    │
│  └─────────────────┘                    │
└──────────────────────────────────────────┘
```

## Accessing the Sandbox

Once deployed, you'll receive a sandbox URL like:

```
https://<sandbox-id>.e2b.dev
```

### Available Endpoints

- **Health Check**: `https://<sandbox-id>.e2b.dev/health`
- **Briefing**: `https://<sandbox-id>.e2b.dev/briefing`
- **Analysis**: `https://<sandbox-id>.e2b.dev/analysis`
- **Workflow Control**: `https://<sandbox-id>.e2b.dev/orchestrator/run`

## Environment Variables

The following environment variables are automatically set in the sandbox:

- `LLM_PROVIDER`: LLM provider (openai/anthropic)
- `LLM_MODEL`: Model name
- `NEWS_SCRAPER_URL`: URL to news-scraper agent
- `STARTUP_API_URL`: URL to startup-api agent
- `GITHUB_MONITOR_URL`: URL to github-monitor agent
- `PORT`: Server port (8080)
- `HOST`: Server host
- `OPENAI_API_KEY`: (if configured)
- `ANTHROPIC_API_KEY`: (if configured)

## Data Collector Agents

The data collector agents (news-scraper, startup-api, github-monitor) run as Docker containers and must be accessible from the E2B sandbox. 

### Option 1: Local Development

If running locally, ensure the agents are accessible via their Docker container URLs:
- `http://localhost:3001` (news-scraper)
- `http://localhost:3002` (startup-api)
- `http://localhost:3003` (github-monitor)

**Note**: E2B sandboxes cannot access `localhost` on your machine. You'll need to:
1. Use a tunneling service (ngrok, localtunnel, etc.)
2. Deploy agents to a public URL
3. Use E2B's network features to connect containers

### Option 2: Deploy Agents to Public URLs

Deploy the Docker agents to a public cloud service (AWS, GCP, Azure) or use Docker MCP Hub's public registry.

## Sandbox Lifecycle

### Creating a New Sandbox

```python
from sandbox_integration.client import E2BClient

client = E2BClient()
sandbox_url = await client.deploy()
```

### Sandbox Lifecycle

**Note:** E2B sandboxes are ephemeral and cannot be reconnected to. Each deployment creates a new sandbox. The `SANDBOX_ID` environment variable is kept for API compatibility but is not currently used.

```python
client = E2BClient()
sandbox_url = await client.deploy()  # Always creates a new sandbox
```

### Closing a Sandbox

```python
await client.close()
```

Or use context manager:

```python
async with E2BClient() as client:
    sandbox_url = await client.deploy()
    # Sandbox automatically closes when exiting context
```

## Troubleshooting

### "E2B_API_KEY not configured"

Make sure you've set the `E2B_API_KEY` environment variable in your `.env` file.

### "Failed to create sandbox" or "403: Team does not have access to the template"

- **Template Access Error (403)**: The system will automatically try fallback templates. If all fail:
  - Check your E2B account has access to templates (visit [E2B Dashboard](https://e2b.dev/dashboard))
  - Try setting `E2B_TEMPLATE=base` in your `.env` file (the "base" template is usually available)
  - Contact E2B support if template access issues persist
- **Other Errors**:
  - Check your E2B API key is valid: `python scripts/verify_e2b_key.py`
  - Verify you have available sandbox quota
  - Check E2B service status: [https://status.e2b.dev](https://status.e2b.dev)

### "Failed to install dependencies"

- Check internet connectivity in sandbox
- Verify `requirements.txt` is valid
- Check for package conflicts

### "Agents not accessible"

- Ensure data collector agents are running
- Verify agent URLs are correct
- Check network connectivity from sandbox

### "Port already in use"

- The sandbox may have a previous server running
- Reconnect to existing sandbox or create a new one

## Advanced Usage

### Custom Templates

Use a custom E2B template:

```python
client = E2BClient()
sandbox_url = await client.deploy(template="custom-python-template")
```

Or set it in `.env`:

```bash
E2B_TEMPLATE=custom-python-template
```

**Note:** The system will automatically try fallback templates if your specified template is not accessible. This ensures deployment succeeds even if your account doesn't have access to the primary template.

### Manual Sandbox Management

Use `SandboxManager` directly for more control:

```python
from sandbox_integration.sandbox_manager import SandboxManager

manager = SandboxManager()
await manager.create_sandbox()
await manager.upload_code(source_path=Path("./backend/src"))
await manager.set_environment_variables({"KEY": "value"})
await manager.install_dependencies()
await manager.start_server()
```

## Next Steps

1. **Deploy Data Collector Agents**: Ensure agents are accessible from E2B
2. **Test Workflow**: Run a full workflow in the sandbox
3. **Monitor Performance**: Check logs and metrics
4. **Optimize**: Tune configuration for production use

## Resources

- [E2B Documentation](https://e2b.dev/docs)
- [E2B Python SDK](https://github.com/e2b-dev/e2b-python)
- [E2B Templates](https://e2b.dev/docs/templates)

