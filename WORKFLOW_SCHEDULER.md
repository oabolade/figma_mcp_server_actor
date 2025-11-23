# Workflow Scheduler

## Overview

The Workflow Scheduler enables automated execution of the startup intelligence workflow. It can run the complete workflow (collect → enrich → analyze → summarize) on a schedule without manual intervention.

## Features

- **Scheduled Execution**: Run workflows automatically on hourly, daily, weekly, or custom intervals
- **Manual Trigger**: Trigger workflow execution on-demand
- **Status Monitoring**: Check scheduler status and next run time
- **Error Handling**: Automatic retry on failures
- **Resource Cleanup**: Proper cleanup on server shutdown

## API Endpoints

### POST /workflow/scheduler/start

Start the automated workflow scheduler.

**Query Parameters:**
- `frequency` (optional): `hourly`, `daily`, `weekly`, or `custom` (default: `daily`)
- `interval_seconds` (optional): Custom interval in seconds (required for `custom` frequency, minimum: 60)
- `run_immediately` (optional): Whether to run workflow immediately on start (default: `false`)

**Example:**
```bash
# Start daily scheduler
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=daily"

# Start hourly scheduler with immediate run
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=hourly&run_immediately=true"

# Start custom scheduler (every 6 hours)
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=custom&interval_seconds=21600"
```

**Response:**
```json
{
  "status": "started",
  "frequency": "daily",
  "interval_seconds": 86400,
  "next_run": "2024-11-23T09:00:00",
  "message": "Scheduler started with daily frequency"
}
```

### POST /workflow/scheduler/stop

Stop the automated workflow scheduler.

**Example:**
```bash
curl -X POST http://localhost:8080/workflow/scheduler/stop
```

**Response:**
```json
{
  "status": "stopped",
  "message": "Scheduler stopped successfully"
}
```

### GET /workflow/scheduler/status

Get current scheduler status.

**Example:**
```bash
curl http://localhost:8080/workflow/scheduler/status | python3 -m json.tool
```

**Response:**
```json
{
  "enabled": true,
  "is_running": true,
  "frequency": "daily",
  "interval_seconds": 86400,
  "last_run": "2024-11-22T09:00:00",
  "next_run": "2024-11-23T09:00:00",
  "seconds_until_next": 82800
}
```

### POST /workflow/scheduler/trigger

Manually trigger workflow execution (without waiting for next scheduled time).

**Example:**
```bash
curl -X POST http://localhost:8080/workflow/scheduler/trigger
```

**Response:**
```json
{
  "status": "triggered",
  "message": "Workflow execution triggered",
  "last_run": "2024-11-22T14:30:00",
  "next_run": "2024-11-23T09:00:00"
}
```

## Usage Examples

### Start Daily Scheduler

```bash
# Start scheduler to run daily at the same time
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=daily"

# Check status
curl http://localhost:8080/workflow/scheduler/status | python3 -m json.tool
```

### Start Hourly Scheduler

```bash
# Start scheduler to run every hour
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=hourly"

# Run immediately on start
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=hourly&run_immediately=true"
```

### Custom Interval

```bash
# Run every 6 hours (21600 seconds)
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=custom&interval_seconds=21600"

# Run every 30 minutes (1800 seconds)
curl -X POST "http://localhost:8080/workflow/scheduler/start?frequency=custom&interval_seconds=1800"
```

### Manual Trigger

```bash
# Trigger workflow execution now
curl -X POST http://localhost:8080/workflow/scheduler/trigger
```

### Stop Scheduler

```bash
# Stop the scheduler
curl -X POST http://localhost:8080/workflow/scheduler/stop
```

## Frequency Options

| Frequency | Interval | Use Case |
|-----------|----------|----------|
| `hourly` | 1 hour (3600s) | High-frequency monitoring |
| `daily` | 24 hours (86400s) | Daily briefings (recommended) |
| `weekly` | 7 days (604800s) | Weekly summaries |
| `custom` | Configurable | Specific requirements |

## Integration with Workflow

The scheduler automatically runs the full workflow:
1. **Collect** data from all agents (news, funding, launches, GitHub)
2. **Enrich** data with metadata and cross-references
3. **Analyze** trends and patterns (requires LLM API key)
4. **Summarize** into daily briefing (requires LLM API key)

## Monitoring

### Check Scheduler Status

```bash
# Get current status
curl http://localhost:8080/workflow/scheduler/status | python3 -m json.tool
```

### Monitor Workflow Health

```bash
# Check workflow health
curl http://localhost:8080/workflow/health | python3 -m json.tool

# Get daily report
curl http://localhost:8080/workflow/daily-report | python3 -m json.tool
```

## Error Handling

- **Automatic Retry**: If a workflow run fails, the scheduler will retry on the next scheduled interval
- **Error Logging**: All errors are logged for debugging
- **Status Tracking**: Last run time and errors are tracked in scheduler status

## Best Practices

1. **Start with Daily**: Use `daily` frequency for most use cases
2. **Monitor First Run**: Start with `run_immediately=true` to verify it works
3. **Check Status**: Regularly check scheduler status to ensure it's running
4. **LLM Configuration**: Ensure LLM API keys are configured for full workflow
5. **Resource Management**: Scheduler automatically cleans up on server shutdown

## Testing

Run the scheduler test suite:

```bash
cd tests
python3 test_workflow_scheduler.py
```

## Troubleshooting

### Scheduler Not Starting

**Issue**: Scheduler fails to start
**Solution**: 
- Check server logs for errors
- Verify orchestrator is initialized
- Ensure port is available

### Workflow Not Running

**Issue**: Scheduler is running but workflow doesn't execute
**Solution**:
- Check workflow status: `curl http://localhost:8080/orchestrator/status`
- Verify data collector agents are running
- Check LLM API keys if analysis/summarization is needed

### Scheduler Stops Unexpectedly

**Issue**: Scheduler stops running
**Solution**:
- Check server logs for errors
- Restart scheduler: `POST /workflow/scheduler/start`
- Verify server is not being restarted

---

**Ready for automated workflows!** 🚀

