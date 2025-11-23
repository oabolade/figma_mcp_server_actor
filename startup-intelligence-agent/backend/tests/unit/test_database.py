"""
Unit tests for Database module.
"""
import pytest
from datetime import datetime, timedelta
from database.db import Database


@pytest.mark.unit
class TestDatabase:
    """Test database operations."""
    
    def test_database_initialization(self, temp_db):
        """Test database can be initialized."""
        assert temp_db is not None
        assert temp_db.db_path is not None
        # Test connection works
        conn = temp_db.get_connection()
        assert conn is not None
        conn.close()
    
    def test_insert_news(self, temp_db, sample_news_article):
        """Test inserting news articles."""
        articles = [sample_news_article]
        inserted = temp_db.insert_news(articles)
        assert inserted == 1
        
        # Verify article was inserted
        recent_news = temp_db.get_recent_news(days=7)
        assert len(recent_news) == 1
        assert recent_news[0]['title'] == sample_news_article['title']
    
    def test_insert_funding(self, temp_db, sample_funding_round):
        """Test inserting funding rounds."""
        funding_rounds = [sample_funding_round]
        inserted = temp_db.insert_funding(funding_rounds)
        assert inserted == 1
        
        # Verify funding was inserted
        recent_funding = temp_db.get_recent_funding(days=7)
        assert len(recent_funding) == 1
        assert recent_funding[0]['company_name'] == sample_funding_round['company_name']
    
    def test_insert_launches(self, temp_db, sample_launch):
        """Test inserting product launches."""
        launches = [sample_launch]
        inserted = temp_db.insert_launches(launches)
        assert inserted == 1
        
        # Verify launch was inserted
        recent_launches = temp_db.get_recent_launches(days=7)
        assert len(recent_launches) == 1
        assert recent_launches[0]['name'] == sample_launch['name']
    
    def test_insert_github_repositories(self, temp_db, sample_github_repo):
        """Test inserting GitHub repositories."""
        repos = [sample_github_repo]
        inserted = temp_db.insert_github_repositories(repos)
        assert inserted == 1
        
        # Verify repo was inserted
        recent_repos = temp_db.get_recent_github_repos(days=7)
        assert len(recent_repos) == 1
        assert recent_repos[0]['name'] == sample_github_repo['name']
    
    def test_insert_github_signals(self, temp_db, sample_github_signal, sample_github_repo):
        """Test inserting GitHub signals."""
        from datetime import datetime, timedelta
        # First insert a repository so we have a repository_id
        temp_db.insert_github_repositories([sample_github_repo])
        repos = temp_db.get_recent_github_repos(days=7)
        assert len(repos) > 0
        repo_id = repos[0]['id']
        
        # Use recent date to ensure it's within the 7-day window
        recent_date = datetime.now() - timedelta(days=1)
        
        # Add required fields and link to repository
        signal_with_indicator = {
            **sample_github_signal,
            'repository_id': repo_id,
            'repository_name': sample_github_repo['full_name'],
            'repository_url': sample_github_repo['url'],
            'indicator': 'trending',
            'date': recent_date.strftime('%Y-%m-%d'),  # Use YYYY-MM-DD format
            'confidence': 0.8
        }
        signals = [signal_with_indicator]
        inserted = temp_db.insert_github_signals(signals)
        assert inserted == 1
        
        # Verify signal was inserted
        recent_signals = temp_db.get_recent_github_signals(days=7)
        assert len(recent_signals) == 1
        assert recent_signals[0]['signal_type'] == sample_github_signal['signal_type']
    
    def test_count_recent_news(self, temp_db, sample_news_article):
        """Test counting recent news articles."""
        from datetime import datetime
        # Insert multiple articles with unique URLs
        articles = [
            {**sample_news_article, 
             "title": f"Article {i}",
             "url": f"{sample_news_article['url']}-{i}-{datetime.now().timestamp()}"}
            for i in range(5)
        ]
        inserted = temp_db.insert_news(articles)
        assert inserted == 5  # All should be inserted
        
        count = temp_db.count_recent_news(days=7)
        assert count == 5
    
    def test_count_recent_funding(self, temp_db, sample_funding_round):
        """Test counting recent funding rounds."""
        from datetime import datetime
        # Insert multiple funding rounds with unique links
        funding_rounds = [
            {**sample_funding_round, 
             "company_name": f"Company {i}",
             "link": f"{sample_funding_round['link']}-{i}-{datetime.now().timestamp()}"}
            for i in range(3)
        ]
        inserted = temp_db.insert_funding(funding_rounds)
        assert inserted == 3  # All should be inserted
        
        count = temp_db.count_recent_funding(days=7)
        assert count == 3
    
    def test_get_recent_news_with_enriched_filter(self, temp_db, sample_news_article):
        """Test getting recent news with enriched filter."""
        # Insert article
        temp_db.insert_news([sample_news_article])
        
        # Get unenriched articles
        unenriched = temp_db.get_recent_news(days=7, enriched=False)
        assert len(unenriched) == 1
        
        # Get article ID
        article_id = unenriched[0]['id']
        
        # Enrich the article with correct signature
        enriched_data = {
            'keywords': ["test", "startup"],
            'category': "funding",
            'entities': {"companies": ["Test Startup"]},
            'sentiment': "positive"
        }
        temp_db.update_news_enrichment(article_id, enriched_data)
        
        # Get enriched articles
        enriched = temp_db.get_recent_news(days=7, enriched=True)
        assert len(enriched) == 1
        assert enriched[0]['is_enriched'] == 1
    
    def test_update_news_enrichment(self, temp_db, sample_news_article):
        """Test updating news enrichment data."""
        temp_db.insert_news([sample_news_article])
        
        # Get the article ID
        news = temp_db.get_recent_news(days=7)
        assert len(news) > 0
        article_id = news[0]['id']
        
        # Update enrichment with correct signature
        enriched_data = {
            'keywords': ["test", "startup"],
            'category': "funding",
            'entities': {"companies": ["Test Startup"]},
            'sentiment': "positive"
        }
        temp_db.update_news_enrichment(article_id, enriched_data)
        
        # Verify enrichment
        news = temp_db.get_recent_news(days=7)
        assert news[0]['is_enriched'] == 1
        assert news[0]['category'] == "funding"
        assert news[0]['sentiment'] == "positive"
    
    def test_save_analysis_result(self, temp_db):
        """Test saving analysis results."""
        from datetime import datetime, timedelta
        
        analysis_data = {
            "trends": [{"title": "Test Trend", "description": "Test"}],
            "opportunities": []
        }
        
        date_end = datetime.now().isoformat()
        date_start = (datetime.now() - timedelta(days=7)).isoformat()
        
        temp_db.save_analysis_result(
            analysis_type="trend_analysis",
            date_start=date_start,
            date_end=date_end,
            results_json=analysis_data,
            model_used="test-model"
        )
        
        # Verify analysis was saved
        latest = temp_db.get_latest_analysis()
        assert latest is not None
        assert latest['results_json'] == analysis_data
    
    def test_save_briefing(self, temp_db):
        """Test saving briefing."""
        from datetime import datetime, timedelta
        
        briefing_data = {
            "summary": "Test summary",
            "trends": [],
            "funding_rounds": []
        }
        
        briefing_date = datetime.now().strftime("%Y-%m-%d")
        data_end = datetime.now().isoformat()
        data_start = (datetime.now() - timedelta(days=7)).isoformat()
        
        temp_db.save_briefing(
            briefing_date=briefing_date,
            summary_text="Test summary",
            briefing_json=briefing_data,
            data_start_date=data_start,
            data_end_date=data_end
        )
        
        # Verify briefing was saved
        latest = temp_db.get_latest_briefing()
        assert latest is not None
        assert latest['briefing_json'] == briefing_data
    
    def test_search_articles(self, temp_db, sample_news_article):
        """Test searching articles."""
        temp_db.insert_news([sample_news_article])
        
        # Search for article
        results = temp_db.search_articles("startup")
        assert len(results) >= 1
        assert any("startup" in result['title'].lower() or 
                  "startup" in result.get('summary', '').lower() 
                  for result in results)

