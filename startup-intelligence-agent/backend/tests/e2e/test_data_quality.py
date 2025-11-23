"""
End-to-end tests for data quality validation.
"""
import pytest
import requests
from pathlib import Path
import sys

# Add src to path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings
from database.db import Database


@pytest.mark.e2e
@pytest.mark.requires_agents
class TestDataQuality:
    """Test data quality and validation."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL."""
        host = getattr(settings, 'HOST', '127.0.0.1')
        port = getattr(settings, 'PORT', 8080)
        return f"http://{host}:{port}"
    
    @pytest.fixture
    def db(self):
        """Get database instance."""
        return Database(settings.DATABASE_PATH)
    
    def test_news_articles_collected(self, db):
        """Test news articles are collected correctly."""
        news = db.get_recent_news(days=7)
        
        for article in news:
            assert 'title' in article
            assert 'url' in article
            assert 'source' in article
            assert 'timestamp' in article
            # Verify URL is valid
            assert article['url'].startswith('http')
    
    def test_funding_rounds_parsed(self, db):
        """Test funding rounds are parsed accurately."""
        funding = db.get_recent_funding(days=7)
        
        for round_data in funding:
            assert 'company_name' in round_data
            assert 'amount' in round_data
            assert 'date' in round_data
            # Verify amount format
            if round_data.get('amount'):
                assert '$' in round_data['amount'] or round_data['amount'].isdigit()
    
    def test_launches_captured(self, db):
        """Test launches are captured properly."""
        launches = db.get_recent_launches(days=7)
        
        for launch in launches:
            assert 'name' in launch
            assert 'date' in launch
            assert 'source' in launch
    
    def test_github_signals_meaningful(self, db):
        """Test GitHub signals are meaningful."""
        signals = db.get_recent_github_signals(days=7)
        
        for signal in signals:
            assert 'signal_type' in signal
            assert 'description' in signal
            assert 'detected_at' in signal
    
    def test_enrichment_adds_context(self, db):
        """Test enrichment adds valuable context."""
        enriched_news = db.get_recent_news(days=7, enriched=True)
        
        for article in enriched_news:
            # Check enrichment fields exist
            assert article.get('is_enriched') == 1
            # Should have at least some enrichment data
            assert (
                article.get('keywords') or
                article.get('category') or
                article.get('sentiment')
            )
    
    def test_analysis_produces_insights(self, db):
        """Test analysis produces actionable insights."""
        latest_analysis = db.get_latest_analysis()
        
        if latest_analysis:
            analysis_json = latest_analysis.get('analysis_json', {})
            # Should have trends or opportunities
            assert (
                analysis_json.get('trends') or
                analysis_json.get('opportunities_for_founders') or
                analysis_json.get('opportunities_for_investors')
            )

