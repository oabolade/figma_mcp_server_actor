"""
Unit tests for AnalysisAgent.
"""
import pytest
from unittest.mock import AsyncMock, patch
from analysis.agent import AnalysisAgent
from database.db import Database


@pytest.mark.unit
class TestAnalysisAgent:
    """Test analysis agent operations."""
    
    @pytest.fixture
    def analysis_agent(self, temp_db):
        """Create analysis agent with test database and mocked LLM."""
        with patch('analysis.agent.Database', return_value=temp_db):
            agent = AnalysisAgent()
            agent.db = temp_db
            # Create a proper async mock for LLM client
            mock_llm = AsyncMock()
            mock_llm.complete = AsyncMock(return_value='{"trends": [], "competitor_moves": [], "opportunities_for_founders": [], "opportunities_for_investors": []}')
            agent.llm = mock_llm
            return agent
    
    def test_analysis_agent_initialization(self, analysis_agent):
        """Test analysis agent can be initialized."""
        assert analysis_agent is not None
        assert analysis_agent.db is not None
    
    @pytest.mark.asyncio
    async def test_analyze_recent_data(self, analysis_agent, temp_db, 
                                       sample_news_article, sample_funding_round):
        """Test analyzing recent data."""
        # Insert and enrich test data first
        temp_db.insert_news([sample_news_article])
        temp_db.insert_funding([sample_funding_round])
        
        # Enrich the data so it's available for analysis
        from enrichment.agent import EnrichmentAgent
        enrichment_agent = EnrichmentAgent()
        enrichment_agent.db = temp_db
        await enrichment_agent.enrich_recent_data(days_back=7)
        
        # Analyze recent data
        result = await analysis_agent.analyze_recent_data(days_back=7)
        
        assert result is not None
        assert 'status' in result
        # Should succeed with mocked LLM
        assert result.get('status') == 'success'
        assert 'results' in result
    
    @pytest.mark.asyncio
    async def test_analyze_recent_data_with_llm(self, analysis_agent, temp_db):
        """Test analyzing with LLM response."""
        # Mock LLM to return specific response
        analysis_agent.llm.complete = AsyncMock(return_value='{"trends": [{"title": "Test Trend"}], "competitor_moves": [], "opportunities_for_founders": [], "opportunities_for_investors": []}')
        
        # Insert and enrich test data
        from datetime import datetime, timedelta
        from enrichment.agent import EnrichmentAgent
        sample_article = {
            "title": "Test Article",
            "url": f"https://example.com/test-{datetime.now().timestamp()}",
            "source": "techcrunch",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "summary": "Test summary"
        }
        temp_db.insert_news([sample_article])
        enrichment_agent = EnrichmentAgent()
        enrichment_agent.db = temp_db
        await enrichment_agent.enrich_recent_data(days_back=7)
        
        result = await analysis_agent.analyze_recent_data(days_back=7)
        
        assert result is not None
        assert result.get('status') == 'success'
        # Should call LLM
        analysis_agent.llm.complete.assert_called()
    
    @pytest.mark.asyncio
    async def test_analyze_recent_data_without_data(self, analysis_agent):
        """Test analyzing when no data exists."""
        # Mock LLM to work even with no data
        analysis_agent.llm.complete = AsyncMock(return_value='{"trends": [], "competitor_moves": [], "opportunities_for_founders": [], "opportunities_for_investors": []}')
        
        result = await analysis_agent.analyze_recent_data(days_back=7)
        
        assert result is not None
        # Should still succeed (returns empty results)
        assert result.get('status') == 'success'
        assert 'results' in result
    
    def test_parse_llm_response(self, analysis_agent):
        """Test parsing LLM response."""
        # Test with JSON in markdown code block
        response = '```json\n{"trends": []}\n```'
        parsed = analysis_agent._parse_llm_response(response)
        assert parsed == {"trends": []}
        
        # Test with plain JSON
        response = '{"trends": []}'
        parsed = analysis_agent._parse_llm_response(response)
        assert parsed == {"trends": []}
        
        # Test with invalid JSON (should return default structure with empty lists)
        response = 'invalid json'
        parsed = analysis_agent._parse_llm_response(response)
        # Returns default structure, not empty dict
        assert parsed == {
            "trends": [],
            "competitor_moves": [],
            "opportunities_for_founders": [],
            "opportunities_for_investors": []
        }

