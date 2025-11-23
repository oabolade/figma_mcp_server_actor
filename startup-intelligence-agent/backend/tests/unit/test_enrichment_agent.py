"""
Unit tests for EnrichmentAgent.
"""
import pytest
from unittest.mock import AsyncMock, patch
from enrichment.agent import EnrichmentAgent
from database.db import Database


@pytest.mark.unit
class TestEnrichmentAgent:
    """Test enrichment agent operations."""
    
    @pytest.fixture
    def enrichment_agent(self, temp_db):
        """Create enrichment agent with test database."""
        with patch('enrichment.agent.Database', return_value=temp_db):
            agent = EnrichmentAgent()
            agent.db = temp_db
            return agent
    
    def test_enrichment_agent_initialization(self, enrichment_agent):
        """Test enrichment agent can be initialized."""
        assert enrichment_agent is not None
        assert enrichment_agent.db is not None
    
    def test_enrich_news_article(self, enrichment_agent, sample_news_article, temp_db):
        """Test enriching a news article."""
        # Insert article first
        temp_db.insert_news([sample_news_article])
        
        # Enrich article (NOT async)
        result = enrichment_agent.enrich_news_article(sample_news_article)
        
        assert result is not None
        assert 'keywords' in result
        assert 'category' in result
        assert 'sentiment' in result
    
    def test_enrich_funding_round(self, enrichment_agent, sample_funding_round, temp_db):
        """Test enriching a funding round."""
        # Insert funding first
        temp_db.insert_funding([sample_funding_round])
        
        # Enrich funding (NOT async)
        result = enrichment_agent.enrich_funding_round(sample_funding_round)
        
        assert result is not None
        assert 'industry' in result
        assert 'stage' in result
    
    def test_enrich_launch(self, enrichment_agent, sample_launch, temp_db):
        """Test enriching a product launch."""
        # Insert launch first
        temp_db.insert_launches([sample_launch])
        
        # Enrich launch (NOT async)
        result = enrichment_agent.enrich_launch(sample_launch)
        
        assert result is not None
        assert 'technologies' in result
        assert 'product_category' in result
    
    def test_enrich_github_repository(self, enrichment_agent, sample_github_repo, temp_db):
        """Test enriching a GitHub repository."""
        # Insert repo first
        temp_db.insert_github_repositories([sample_github_repo])
        
        # Enrich repo (NOT async)
        result = enrichment_agent.enrich_github_repository(sample_github_repo)
        
        assert result is not None
        assert 'activity_score' in result
        assert 'tech_stack' in result
    
    @pytest.mark.asyncio
    async def test_enrich_recent_data(self, enrichment_agent, temp_db, 
                                      sample_news_article, sample_funding_round):
        """Test enriching recent data."""
        # Insert test data
        temp_db.insert_news([sample_news_article])
        temp_db.insert_funding([sample_funding_round])
        
        # Enrich recent data
        result = await enrichment_agent.enrich_recent_data(days_back=7)
        
        assert result is not None
        assert result.get('status') == 'success'
        assert 'enriched' in result
        assert 'duration_seconds' in result

