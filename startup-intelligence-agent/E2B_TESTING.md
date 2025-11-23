# E2B Sandbox Testing Guide

This guide explains how to test your deployed Startup Intelligence Agent system in the E2B sandbox environment.

## ⚠️ Important: E2B Sandboxes are Ephemeral

**E2B sandboxes automatically close when:**
- The deployment script exits (Ctrl+C)
- The sandbox times out (check E2B dashboard for timeout settings)
- The connection is lost

**To keep a sandbox alive:**
- Keep the `deploy_to_e2b.py` script running
- The sandbox stays active as long as the script is running
- Copy the sandbox URL immediately after deployment

## Quick Start

After successful deployment, you'll receive a sandbox URL. **Copy it immediately** and use it to test:

```bash
# Basic testing (all endpoints)
python scripts/test_e2b_deployment.py https://your-sandbox-id.e2b.dev

# Test and trigger workflow
python scripts/test_e2b_deployment.py https://your-sandbox-id.e2b.dev --trigger-workflow

# Test, trigger workflow, and wait for completion
python scripts/test_e2b_deployment.py https://your-sandbox-id.e2b.dev --trigger-workflow --wait-for-workflow
```

## Manual Testing

### 1. Health Check

```bash
curl https://your-sandbox-id.e2b.dev/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "startup-intelligence-agent",
  "version": "1.0.0",
  "timestamp": "2025-11-22T15:30:00"
}
```

### 2. System Information

```bash
curl https://your-sandbox-id.e2b.dev/info
```

This shows:
- Service configuration
- LLM provider and model
- Database path
- Data collector agent URLs

### 3. Orchestrator Status

```bash
curl https://your-sandbox-id.e2b.dev/orchestrator/status
```

Check if workflow is running and when it last completed.

### 4. Data Statistics

```bash
curl https://your-sandbox-id.e2b.dev/data/stats
```

View counts of collected data (news, funding, launches, GitHub repos).

### 5. Get Briefing

```bash
curl https://your-sandbox-id.e2b.dev/briefing
```

If no briefing exists, you'll get a 404. Generate one first (see below).

### 6. Trigger Workflow

```bash
curl -X POST "https://your-sandbox-id.e2b.dev/orchestrator/run?days_back=7"
```

This triggers the full workflow:
- Collect data from all agents
- Enrich the data
- Analyze trends
- Generate briefing

**Note:** This runs in the background. Check status with `/orchestrator/status`.

### 7. Check Workflow Status

```bash
curl https://your-sandbox-id.e2b.dev/orchestrator/status
```

Wait until `"running": false` to see results.

### 8. View Briefing After Workflow

```bash
curl https://your-sandbox-id.e2b.dev/briefing
```

You should now see a JSON briefing with:
- Executive summary
- Top trends
- Funding rounds
- Product launches
- Opportunities
- Intelligence threads

## Testing Data Collector Agents

The data collector agents must be running locally (via Docker Compose) for the workflow to collect data.

### Start Data Collectors

```bash
cd data-collector-agents
docker compose up -d
```

### Verify Agents Are Running

```bash
curl http://localhost:3001/health  # news-scraper
curl http://localhost:3002/health  # startup-api
curl http://localhost:3003/health  # github-monitor
```

**Important:** The E2B sandbox needs to be able to reach these agents. If the sandbox is in the cloud, you'll need to:
1. Use a tunnel service (ngrok, localtunnel) to expose localhost
2. Update the agent URLs in the sandbox environment variables
3. Or deploy the agents to a publicly accessible location

## Testing Workflow

### Full Workflow Test

1. **Start data collectors** (if not already running):
   ```bash
   cd data-collector-agents
   docker compose up -d
   ```

2. **Trigger workflow**:
   ```bash
   curl -X POST "https://your-sandbox-id.e2b.dev/orchestrator/run?days_back=7"
   ```

3. **Monitor status**:
   ```bash
   watch -n 5 'curl -s https://your-sandbox-id.e2b.dev/orchestrator/status | jq'
   ```

4. **Check briefing** (after workflow completes):
   ```bash
   curl https://your-sandbox-id.e2b.dev/briefing | jq
   ```

### Data Collection Only

Test just the data collection step:

```bash
curl -X POST https://your-sandbox-id.e2b.dev/orchestrator/collect
```

## Testing Frontend

If you've deployed the frontend, access it at:

```
https://your-sandbox-id.e2b.dev/
```

The frontend will automatically fetch the briefing from `/briefing` endpoint.

## Troubleshooting

### Server Not Responding

1. **Check if server is running**:
   ```bash
   # In the sandbox (if you have access)
   ps aux | grep "python3 /app/main.py"
   ```

2. **Check server logs**:
   ```bash
   # Server logs are at /app/server.log in the sandbox
   # You can read them via E2B SDK or dashboard
   ```

3. **Verify port is exposed**:
   - Check E2B dashboard for exposed ports
   - Ensure port 8080 is exposed

### Workflow Not Starting

1. **Check orchestrator status**:
   ```bash
   curl https://your-sandbox-id.e2b.dev/orchestrator/status
   ```

2. **Check for errors**:
   - Look at the status response for `"error"` field
   - Check server logs in the sandbox

3. **Verify data collectors are accessible**:
   - The sandbox needs network access to your data collector agents
   - If agents are on localhost, use a tunnel service

### No Data Collected

1. **Verify data collector agents are running**:
   ```bash
   curl http://localhost:3001/health
   curl http://localhost:3002/health
   curl http://localhost:3003/health
   ```

2. **Check agent URLs in sandbox**:
   ```bash
   curl https://your-sandbox-id.e2b.dev/info | jq '.data_collector_agents'
   ```

3. **Test agent connectivity from sandbox**:
   - The sandbox may not be able to reach localhost agents
   - Consider using ngrok or similar to expose agents publicly

## Advanced Testing

### Test Individual Endpoints

```bash
# Analysis results
curl https://your-sandbox-id.e2b.dev/analysis

# Workflow health
curl https://your-sandbox-id.e2b.dev/workflow/health

# Workflow report
curl https://your-sandbox-id.e2b.dev/workflow/report

# Scheduler status
curl https://your-sandbox-id.e2b.dev/workflow/scheduler/status
```

### Test Scheduler

```bash
# Start scheduler (daily runs)
curl -X POST "https://your-sandbox-id.e2b.dev/workflow/scheduler/start?frequency=daily&run_immediately=true"

# Check scheduler status
curl https://your-sandbox-id.e2b.dev/workflow/scheduler/status

# Manually trigger scheduled run
curl -X POST https://your-sandbox-id.e2b.dev/workflow/scheduler/trigger

# Stop scheduler
curl -X POST https://your-sandbox-id.e2b.dev/workflow/scheduler/stop
```

## Expected Test Results

### Successful Deployment

- ✅ `/health` returns 200 OK
- ✅ `/info` shows correct configuration
- ✅ `/orchestrator/status` shows workflow status
- ✅ `/data/stats` shows data counts (may be 0 initially)
- ✅ `/briefing` returns 404 (expected if no workflow run yet)

### After Workflow Run

- ✅ `/orchestrator/status` shows `"running": false` and `"last_run"` timestamp
- ✅ `/briefing` returns JSON with intelligence data
- ✅ `/data/stats` shows non-zero counts
- ✅ `/analysis` returns analysis results

## Next Steps

After successful testing:

1. **Set up automated scheduling** for daily briefings
2. **Configure data collector agents** for production
3. **Set up monitoring** for the sandbox
4. **Customize LLM prompts** for better analysis
5. **Add more data sources** as needed

## Support

If you encounter issues:

1. Check server logs: `/app/server.log` in the sandbox
2. Review E2B dashboard for sandbox status
3. Verify all environment variables are set correctly
4. Ensure data collector agents are accessible from the sandbox

