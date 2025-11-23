"""Workflow reporting and monitoring."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

from database.db import Database
from config.settings import settings

logger = logging.getLogger(__name__)


class WorkflowReporter:
    """Generate workflow reports and statistics."""
    
    def __init__(self):
        self.db = Database(settings.DATABASE_PATH)
        self.reports_dir = Path(__file__).parent.parent.parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(self, date: Optional[str] = None) -> Dict:
        """Generate daily workflow report."""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get data counts
        news_count = self.db.count_recent_news(days=1)
        funding_count = self.db.count_recent_funding(days=1)
        launches_count = self.db.count_recent_launches(days=1)
        github_repos_count = self.db.count_recent_github_repos(days=1)
        github_signals_count = len(self.db.get_recent_github_signals(days=1) or [])
        
        # Get latest briefing
        latest_briefing = self.db.get_latest_briefing()
        briefing_date = latest_briefing.get("briefing_date") if latest_briefing else None
        
        # Get latest analysis
        latest_analysis = self.db.get_latest_analysis()
        analysis_date = latest_analysis.get("created_at") if latest_analysis else None
        
        report = {
            "report_date": date,
            "generated_at": datetime.now().isoformat(),
            "data_collection": {
                "news_articles": news_count,
                "funding_rounds": funding_count,
                "launches": launches_count,
                "github_repositories": github_repos_count,
                "github_signals": github_signals_count,
                "total_items": news_count + funding_count + launches_count + github_repos_count + github_signals_count
            },
            "workflow_status": {
                "briefing_available": briefing_date is not None,
                "briefing_date": briefing_date,
                "analysis_available": analysis_date is not None,
                "analysis_date": analysis_date
            },
            "data_quality": {
                "enriched_news": self._count_enriched_news(days=1),
                "enriched_funding": self._count_enriched_funding(days=1),
                "enriched_launches": self._count_enriched_launches(days=1)
            }
        }
        
        return report
    
    def generate_workflow_summary(self, days: int = 7) -> Dict:
        """Generate workflow summary for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get aggregated statistics
        news_count = self.db.count_recent_news(days=days)
        funding_count = self.db.count_recent_funding(days=days)
        launches_count = self.db.count_recent_launches(days=days)
        github_repos_count = self.db.count_recent_github_repos(days=days)
        github_signals_count = len(self.db.get_recent_github_signals(days=days) or [])
        
        # Get briefings count
        briefings = self._get_briefings_in_range(days)
        
        # Get analysis count
        analyses = self._get_analyses_in_range(days)
        
        summary = {
            "period": f"Last {days} days",
            "start_date": cutoff_date.strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "data_collected": {
                "news_articles": news_count,
                "funding_rounds": funding_count,
                "launches": launches_count,
                "github_repositories": github_repos_count,
                "github_signals": github_signals_count,
                "total": news_count + funding_count + launches_count + github_repos_count + github_signals_count
            },
            "workflow_executions": {
                "briefings_generated": len(briefings),
                "analyses_performed": len(analyses),
                "last_briefing": briefings[0].get("briefing_date") if briefings else None,
                "last_analysis": analyses[0].get("created_at") if analyses else None
            },
            "data_enrichment": {
                "enriched_news": self._count_enriched_news(days=days),
                "enriched_funding": self._count_enriched_funding(days=days),
                "enriched_launches": self._count_enriched_launches(days=days),
                "enrichment_rate": self._calculate_enrichment_rate(days=days)
            }
        }
        
        return summary
    
    def _count_enriched_news(self, days: int) -> int:
        """Count enriched news articles."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM news 
            WHERE is_enriched = 1 
            AND created_at >= datetime('now', '-' || ? || ' days')
        """, (days,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _count_enriched_funding(self, days: int) -> int:
        """Count enriched funding rounds."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM funding 
            WHERE is_enriched = 1 
            AND created_at >= datetime('now', '-' || ? || ' days')
        """, (days,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _count_enriched_launches(self, days: int) -> int:
        """Count enriched launches."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM launches 
            WHERE is_enriched = 1 
            AND created_at >= datetime('now', '-' || ? || ' days')
        """, (days,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _calculate_enrichment_rate(self, days: int) -> float:
        """Calculate enrichment rate percentage."""
        total_news = self.db.count_recent_news(days=days)
        total_funding = self.db.count_recent_funding(days=days)
        total_launches = self.db.count_recent_launches(days=days)
        total = total_news + total_funding + total_launches
        
        if total == 0:
            return 0.0
        
        enriched = (
            self._count_enriched_news(days) +
            self._count_enriched_funding(days) +
            self._count_enriched_launches(days)
        )
        
        return round((enriched / total) * 100, 2) if total > 0 else 0.0
    
    def _get_briefings_in_range(self, days: int) -> List[Dict]:
        """Get briefings in date range."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM briefings 
            WHERE briefing_date >= date('now', '-' || ? || ' days')
            ORDER BY briefing_date DESC
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        
        briefings = []
        for row in rows:
            briefing = dict(row)
            if briefing.get('briefing_json'):
                try:
                    briefing['briefing_json'] = json.loads(briefing['briefing_json'])
                except:
                    pass
            briefings.append(briefing)
        
        return briefings
    
    def _get_analyses_in_range(self, days: int) -> List[Dict]:
        """Get analyses in date range."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_results 
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            analysis = dict(row)
            if analysis.get('results_json'):
                try:
                    analysis['results_json'] = json.loads(analysis['results_json'])
                except:
                    pass
            analyses.append(analysis)
        
        return analyses
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> Path:
        """Save report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_report_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to: {report_path}")
        return report_path
    
    def get_workflow_health(self) -> Dict:
        """Get workflow health status."""
        # Check data collector agents (would need to ping them)
        # For now, check database health
        
        recent_data = {
            "news_24h": self.db.count_recent_news(days=1),
            "funding_24h": self.db.count_recent_funding(days=1),
            "launches_24h": self.db.count_recent_launches(days=1)
        }
        
        latest_briefing = self.db.get_latest_briefing()
        latest_analysis = self.db.get_latest_analysis()
        
        health = {
            "status": "healthy" if recent_data["news_24h"] > 0 or recent_data["funding_24h"] > 0 else "degraded",
            "timestamp": datetime.now().isoformat(),
            "data_collection": {
                "last_24h": recent_data,
                "has_recent_data": any(recent_data.values())
            },
            "workflow": {
                "last_briefing": latest_briefing.get("briefing_date") if latest_briefing else None,
                "last_analysis": latest_analysis.get("created_at") if latest_analysis else None,
                "briefing_age_hours": self._get_briefing_age_hours(),
                "analysis_age_hours": self._get_analysis_age_hours()
            }
        }
        
        return health
    
    def _get_briefing_age_hours(self) -> Optional[float]:
        """Get age of latest briefing in hours."""
        latest_briefing = self.db.get_latest_briefing()
        if not latest_briefing:
            return None
        
        briefing_date = latest_briefing.get("briefing_date")
        if not briefing_date:
            return None
        
        try:
            # Handle date-only strings (YYYY-MM-DD) and datetime strings
            if len(briefing_date) == 10 and briefing_date.count('-') == 2:
                # Date-only format (YYYY-MM-DD) - parse as date and convert to datetime
                from datetime import date as date_type
                date_obj = date_type.fromisoformat(briefing_date)
                briefing_dt = datetime.combine(date_obj, datetime.min.time())
            else:
                # Datetime string - parse directly
                briefing_dt = datetime.fromisoformat(briefing_date.replace("Z", "+00:00"))
            
            # Get timezone-aware now datetime
            if briefing_dt.tzinfo:
                now = datetime.now(briefing_dt.tzinfo)
            else:
                now = datetime.now()
                briefing_dt = briefing_dt.replace(tzinfo=now.tzinfo)
            
            age = (now - briefing_dt).total_seconds() / 3600
            return round(age, 2)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parsing briefing date '{briefing_date}': {e}")
            return None
    
    def _get_analysis_age_hours(self) -> Optional[float]:
        """Get age of latest analysis in hours."""
        latest_analysis = self.db.get_latest_analysis()
        if not latest_analysis:
            return None
        
        analysis_date = latest_analysis.get("created_at")
        if not analysis_date:
            return None
        
        try:
            # Handle date-only strings (YYYY-MM-DD) and datetime strings
            if isinstance(analysis_date, str) and len(analysis_date) == 10 and analysis_date.count('-') == 2:
                # Date-only format (YYYY-MM-DD) - parse as date and convert to datetime
                from datetime import date as date_type
                date_obj = date_type.fromisoformat(analysis_date)
                analysis_dt = datetime.combine(date_obj, datetime.min.time())
            else:
                # Datetime string - parse directly
                analysis_dt = datetime.fromisoformat(str(analysis_date).replace("Z", "+00:00"))
            
            # Get timezone-aware now datetime
            if analysis_dt.tzinfo:
                now = datetime.now(analysis_dt.tzinfo)
            else:
                now = datetime.now()
                analysis_dt = analysis_dt.replace(tzinfo=now.tzinfo)
            
            age = (now - analysis_dt).total_seconds() / 3600
            return round(age, 2)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parsing analysis date '{analysis_date}': {e}")
            return None

