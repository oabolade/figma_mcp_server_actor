# Workflow Reporting & Monitoring

## Overview

The workflow reporting system provides comprehensive monitoring and statistics for the Startup Intelligence workflow.

## API Endpoints

### GET /workflow/health

Get workflow health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-22T09:30:00",
  "data_collection": {
    "last_24h": {
      "news_24h": 15,
      "funding_24h": 3,
      "launches_24h": 5
    },
    "has_recent_data": true
  },
  "workflow": {
    "last_briefing": "2024-11-22",
    "last_analysis": "2024-11-22T09:00:00",
    "briefing_age_hours": 0.5,
    "analysis_age_hours": 0.5
  }
}
```

### GET /workflow/report

Get workflow summary for the last N days.

**Query Parameters:**
- `days` (optional): Number of days to report (default: 7, max: 30)

**Response:**
```json
{
  "period": "Last 7 days",
  "start_date": "2024-11-15",
  "end_date": "2024-11-22",
  "data_collected": {
    "news_articles": 105,
    "funding_rounds": 21,
    "launches": 35,
    "github_repositories": 175,
    "github_signals": 42,
    "total": 378
  },
  "workflow_executions": {
    "briefings_generated": 7,
    "analyses_performed": 7,
    "last_briefing": "2024-11-22",
    "last_analysis": "2024-11-22T09:00:00"
  },
  "data_enrichment": {
    "enriched_news": 98,
    "enriched_funding": 20,
    "enriched_launches": 33,
    "enrichment_rate": 95.5
  }
}
```

### GET /workflow/daily-report

Get daily workflow report.

**Query Parameters:**
- `date` (optional): Date in YYYY-MM-DD format (default: today)

**Response:**
```json
{
  "report_date": "2024-11-22",
  "generated_at": "2024-11-22T09:30:00",
  "data_collection": {
    "news_articles": 15,
    "funding_rounds": 3,
    "launches": 5,
    "github_repositories": 25,
    "github_signals": 6,
    "total": 54
  },
  "workflow_status": {
    "briefing_available": true,
    "briefing_date": "2024-11-22",
    "analysis_available": true,
    "analysis_date": "2024-11-22T09:00:00"
  },
  "data_quality": {
    "enriched_news": 14,
    "enriched_funding": 3,
    "enriched_launches": 5
  }
}
```

## Usage Examples

### Check Workflow Health

```bash
curl http://localhost:8080/workflow/health | python3 -m json.tool
```

### Get Weekly Report

```bash
curl "http://localhost:8080/workflow/report?days=7" | python3 -m json.tool
```

### Get Daily Report

```bash
curl http://localhost:8080/workflow/daily-report | python3 -m json.tool
```

### Get Report for Specific Date

```bash
curl "http://localhost:8080/workflow/daily-report?date=2024-11-21" | python3 -m json.tool
```

## Metrics Tracked

### Data Collection Metrics
- News articles collected
- Funding rounds collected
- Product launches collected
- GitHub repositories collected
- GitHub signals collected

### Workflow Execution Metrics
- Briefings generated
- Analyses performed
- Last execution timestamps
- Execution frequency

### Data Quality Metrics
- Enrichment rate
- Enriched items count
- Data completeness

### Health Metrics
- Recent data availability
- Workflow execution status
- System health indicators

## Integration with Frontend

The frontend can use these endpoints to display:
- Dashboard statistics
- Workflow status indicators
- Data collection charts
- Health monitoring alerts

## Automated Reporting

Reports can be saved to files:

```python
from workflow.reporter import WorkflowReporter

reporter = WorkflowReporter()
report = reporter.generate_daily_report()
report_path = reporter.save_report(report)
```

Reports are saved to: `startup-intelligence-agent/reports/`

## Monitoring

Use the health endpoint for monitoring:

```bash
# Check health every 5 minutes
watch -n 300 'curl -s http://localhost:8080/workflow/health | python3 -m json.tool'
```

## Next Steps

1. Set up automated daily reports
2. Create monitoring dashboards
3. Set up alerts for workflow failures
4. Track workflow performance over time

---

**Ready for monitoring!** 📊

