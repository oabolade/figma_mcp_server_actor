# Prompt 7: Enrichment Agent

## Objective

Create an enrichment agent that runs inside the E2B sandbox to enhance collected data with additional context, metadata, and cross-references. This agent adds value to raw collected data before analysis.

## Requirements

### Enrichment Agent Responsibilities

The Enrichment Agent operates **inside the E2B sandbox** and:

1. **Add Metadata**
   - Extract additional metadata from articles/funding/launches
   - Add categorization and tagging
   - Identify entities (companies, people, technologies)

2. **Cross-Reference Data**
   - Link related articles across sources
   - Connect funding rounds to news articles
   - Match launches with GitHub repositories
   - Identify relationships between data points

3. **Enhance Context**
   - Add summaries and key points
   - Extract quotes and important statements
   - Identify sentiment and tone
   - Add relevance scores

4. **Fill Gaps**
   - Complete missing fields where possible
   - Normalize data formats
   - Validate and clean data

### Implementation

**File:** `backend/src/enrichment/agent.py`

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from database.db import Database
from config.settings import settings

logger = logging.getLogger(__name__)

class EnrichmentAgent:
    def __init__(self):
        self.db = Database(settings.DATABASE_PATH)
        
    def enrich_news_article(self, article: Dict) -> Dict:
        """Enrich a single news article with additional context."""
        enriched = article.copy()
        
        # Extract keywords from title and summary
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        enriched['keywords'] = self._extract_keywords(text)
        
        # Add categorization
        enriched['category'] = self._categorize_article(article)
        
        # Extract entities (companies, technologies)
        enriched['entities'] = self._extract_entities(text)
        
        # Add sentiment (simple keyword-based)
        enriched['sentiment'] = self._detect_sentiment(text)
        
        # Link to related articles (by keywords/entities)
        enriched['related_article_ids'] = self._find_related_articles(article)
        
        # Add timestamp metadata
        enriched['enriched_at'] = datetime.now().isoformat()
        
        return enriched
    
    def enrich_funding_round(self, funding: Dict) -> Dict:
        """Enrich a funding round with additional context."""
        enriched = funding.copy()
        
        # Link to news articles mentioning this company
        company_name = funding.get('company_name', '')
        enriched['related_news_ids'] = self._find_company_news(company_name)
        
        # Add industry categorization
        enriched['industry'] = self._categorize_company(company_name, funding)
        
        # Extract investor names (if in description)
        description = funding.get('description', '')
        enriched['investor_names'] = self._extract_investor_names(description)
        
        # Link to GitHub repositories (if applicable)
        enriched['related_github_repos'] = self._find_company_github(company_name)
        
        # Add funding stage classification
        enriched['stage'] = self._classify_funding_stage(funding)
        
        enriched['enriched_at'] = datetime.now().isoformat()
        
        return enriched
    
    def enrich_launch(self, launch: Dict) -> Dict:
        """Enrich a product/startup launch with additional context."""
        enriched = launch.copy()
        
        # Link to GitHub repositories
        name = launch.get('name', '')
        enriched['related_github_repos'] = self._find_product_github(name, launch)
        
        # Add product category
        enriched['product_category'] = self._categorize_product(launch)
        
        # Link to related news articles
        enriched['related_news_ids'] = self._find_launch_news(launch)
        
        # Extract technology stack mentions
        description = launch.get('description', '')
        enriched['technologies'] = self._extract_technologies(description)
        
        enriched['enriched_at'] = datetime.now().isoformat()
        
        return enriched
    
    def enrich_github_repository(self, repo: Dict) -> Dict:
        """Enrich a GitHub repository with additional context."""
        enriched = repo.copy()
        
        # Link to news articles mentioning this repo
        repo_name = repo.get('name', '')
        enriched['related_news_ids'] = self._find_repo_news(repo_name)
        
        # Add technology stack
        language = repo.get('language', '')
        enriched['tech_stack'] = [language] if language else []
        enriched['tech_stack'].extend(repo.get('topics', []))
        
        # Calculate activity score
        enriched['activity_score'] = self._calculate_activity_score(repo)
        
        # Link to related funding/launches
        enriched['related_funding_ids'] = self._find_repo_funding(repo)
        enriched['related_launch_ids'] = self._find_repo_launches(repo)
        
        enriched['enriched_at'] = datetime.now().isoformat()
        
        return enriched
    
    async def enrich_recent_data(self, days_back: int = 7) -> Dict:
        """Enrich all recently collected data."""
        logger.info(f"Starting enrichment for last {days_back} days...")
        
        enrichment_start = datetime.now()
        
        # Get recent unenriched data
        news_articles = self.db.get_recent_news(days=days_back, enriched=False)
        funding_rounds = self.db.get_recent_funding(days=days_back, enriched=False)
        launches = self.db.get_recent_launches(days=days_back, enriched=False)
        github_repos = self.db.get_recent_github_repos(days=days_back, enriched=False)
        
        # Enrich news articles
        enriched_news = []
        for article in news_articles:
            try:
                enriched = self.enrich_news_article(article)
                self.db.update_news_enrichment(article['id'], enriched)
                enriched_news.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching news article {article.get('id')}: {e}")
        
        # Enrich funding rounds
        enriched_funding = []
        for funding in funding_rounds:
            try:
                enriched = self.enrich_funding_round(funding)
                self.db.update_funding_enrichment(funding['id'], enriched)
                enriched_funding.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching funding round {funding.get('id')}: {e}")
        
        # Enrich launches
        enriched_launches = []
        for launch in launches:
            try:
                enriched = self.enrich_launch(launch)
                self.db.update_launch_enrichment(launch['id'], enriched)
                enriched_launches.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching launch {launch.get('id')}: {e}")
        
        # Enrich GitHub repositories
        enriched_repos = []
        for repo in github_repos:
            try:
                enriched = self.enrich_github_repository(repo)
                self.db.update_github_repo_enrichment(repo['id'], enriched)
                enriched_repos.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching GitHub repo {repo.get('id')}: {e}")
        
        enrichment_duration = (datetime.now() - enrichment_start).total_seconds()
        
        logger.info(f"Enriched {len(enriched_news)} news, {len(enriched_funding)} funding, "
                   f"{len(enriched_launches)} launches, {len(enriched_repos)} repos in "
                   f"{enrichment_duration:.2f} seconds")
        
        return {
            "status": "success",
            "duration_seconds": enrichment_duration,
            "enriched": {
                "news_articles": len(enriched_news),
                "funding_rounds": len(enriched_funding),
                "launches": len(enriched_launches),
                "github_repositories": len(enriched_repos)
            }
        }
    
    # Helper methods (implementations)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simple implementation)."""
        # Simple keyword extraction - can be enhanced with NLP
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in common_words]
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _categorize_article(self, article: Dict) -> str:
        """Categorize article by content (simple keyword-based)."""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        categories = {
            'funding': ['funding', 'raised', 'investment', 'series', 'seed'],
            'product_launch': ['launch', 'released', 'announced', 'product'],
            'acquisition': ['acquired', 'acquisition', 'bought'],
            'technology': ['ai', 'ml', 'blockchain', 'api', 'platform'],
            'general': []
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities (companies, technologies) from text."""
        # Simple entity extraction - can be enhanced with NLP libraries
        entities = {
            'companies': [],
            'technologies': [],
            'people': []
        }
        
        # Basic pattern matching for company names (capitalized words)
        # This is a simplified implementation
        words = text.split()
        capitalized = [w for w in words if w[0].isupper() and len(w) > 2]
        entities['companies'] = capitalized[:5]  # Top 5
        
        # Technology keywords
        tech_keywords = ['python', 'javascript', 'react', 'ai', 'ml', 'blockchain']
        entities['technologies'] = [kw for kw in tech_keywords if kw in text.lower()]
        
        return entities
    
    def _detect_sentiment(self, text: str) -> str:
        """Detect sentiment (simple keyword-based)."""
        positive_words = ['success', 'growth', 'raised', 'launch', 'innovation']
        negative_words = ['decline', 'failure', 'shutdown', 'layoff']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _find_related_articles(self, article: Dict) -> List[int]:
        """Find related articles by keywords/entities."""
        keywords = self._extract_keywords(f"{article.get('title', '')} {article.get('summary', '')}")
        related = self.db.find_articles_by_keywords(keywords, exclude_id=article.get('id'), limit=5)
        return [r['id'] for r in related]
    
    def _find_company_news(self, company_name: str) -> List[int]:
        """Find news articles mentioning a company."""
        articles = self.db.search_articles(company_name, limit=5)
        return [a['id'] for a in articles]
    
    def _find_company_github(self, company_name: str) -> List[int]:
        """Find GitHub repositories for a company."""
        repos = self.db.search_github_repos(company_name, limit=5)
        return [r['id'] for r in repos]
    
    def _categorize_company(self, company_name: str, funding: Dict) -> str:
        """Categorize company by industry."""
        description = funding.get('description', '').lower()
        category = funding.get('category', '').lower()
        
        industries = {
            'fintech': ['finance', 'payment', 'banking', 'fintech'],
            'healthtech': ['health', 'medical', 'healthcare'],
            'edtech': ['education', 'learning', 'edtech'],
            'saas': ['software', 'saas', 'platform'],
            'ai/ml': ['ai', 'ml', 'machine learning', 'artificial intelligence'],
            'other': []
        }
        
        search_text = f"{company_name} {description} {category}"
        
        for industry, keywords in industries.items():
            if any(keyword in search_text for keyword in keywords):
                return industry
        
        return 'other'
    
    def _extract_investor_names(self, description: str) -> List[str]:
        """Extract investor names from description."""
        # Simple pattern matching - can be enhanced
        investors = []
        common_investors = ['sequoia', 'a16z', 'y combinator', 'accel', 'gv']
        desc_lower = description.lower()
        
        for investor in common_investors:
            if investor in desc_lower:
                investors.append(investor.title())
        
        return investors
    
    def _classify_funding_stage(self, funding: Dict) -> str:
        """Classify funding stage."""
        funding_type = funding.get('type', '').lower()
        
        stages = {
            'pre_seed': ['pre-seed', 'pre seed'],
            'seed': ['seed'],
            'series_a': ['series a', 'series-a', 'a'],
            'series_b': ['series b', 'series-b', 'b'],
            'series_c': ['series c', 'series-c', 'c'],
            'later': ['series d', 'series e', 'ipo']
        }
        
        for stage, keywords in stages.items():
            if any(keyword in funding_type for keyword in keywords):
                return stage
        
        return 'unknown'
    
    def _find_product_github(self, name: str, launch: Dict) -> List[int]:
        """Find GitHub repositories for a product."""
        repos = self.db.search_github_repos(name, limit=5)
        return [r['id'] for r in repos]
    
    def _categorize_product(self, launch: Dict) -> str:
        """Categorize product type."""
        description = launch.get('description', '').lower()
        category = launch.get('category', '').lower()
        
        categories = {
            'saas': ['saas', 'software', 'platform'],
            'mobile': ['mobile', 'app', 'ios', 'android'],
            'developer_tools': ['api', 'sdk', 'developer', 'tool'],
            'ai_tools': ['ai', 'ml', 'automation'],
            'other': []
        }
        
        search_text = f"{description} {category}"
        
        for cat, keywords in categories.items():
            if any(keyword in search_text for keyword in keywords):
                return cat
        
        return 'other'
    
    def _find_launch_news(self, launch: Dict) -> List[int]:
        """Find news articles about a launch."""
        name = launch.get('name', '')
        articles = self.db.search_articles(name, limit=5)
        return [a['id'] for a in articles]
    
    def _extract_technologies(self, description: str) -> List[str]:
        """Extract mentioned technologies."""
        tech_keywords = [
            'python', 'javascript', 'react', 'vue', 'angular',
            'node.js', 'django', 'flask', 'fastapi',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'blockchain', 'web3', 'ai', 'ml', 'gpt', 'openai'
        ]
        
        desc_lower = description.lower()
        found_techs = [tech for tech in tech_keywords if tech in desc_lower]
        return list(set(found_techs))
    
    def _find_repo_news(self, repo_name: str) -> List[int]:
        """Find news articles mentioning a repository."""
        articles = self.db.search_articles(repo_name, limit=5)
        return [a['id'] for a in articles]
    
    def _calculate_activity_score(self, repo: Dict) -> float:
        """Calculate activity score based on stars, forks, recent commits."""
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        # Normalize score (0-1)
        score = min((stars + forks * 2) / 1000, 1.0)
        return round(score, 2)
    
    def _find_repo_funding(self, repo: Dict) -> List[int]:
        """Find related funding rounds for a repository."""
        # Match by company name or description
        name = repo.get('name', '')
        funding = self.db.search_funding(name, limit=3)
        return [f['id'] for f in funding]
    
    def _find_repo_launches(self, repo: Dict) -> List[int]:
        """Find related launches for a repository."""
        name = repo.get('name', '')
        launches = self.db.search_launches(name, limit=3)
        return [l['id'] for l in launches]
```

### Database Schema Updates

Add enrichment fields to existing tables:

**news table:**
- `keywords` (TEXT, JSON)
- `category` (TEXT)
- `entities` (TEXT, JSON)
- `sentiment` (TEXT)
- `related_article_ids` (TEXT, JSON)
- `enriched_at` (TEXT)
- `is_enriched` (INTEGER, DEFAULT 0)

**funding table:**
- `related_news_ids` (TEXT, JSON)
- `industry` (TEXT)
- `investor_names` (TEXT, JSON)
- `related_github_repos` (TEXT, JSON)
- `stage` (TEXT)
- `enriched_at` (TEXT)
- `is_enriched` (INTEGER, DEFAULT 0)

Similar fields for `launches` and `github_repositories` tables.

### Deliverables

1. Complete enrichment agent implementation
2. Enrichment methods for all data types (news, funding, launches, GitHub)
3. Cross-referencing and linking logic
4. Metadata extraction and categorization
5. Database schema updates for enrichment fields
6. Error handling and logging
7. Performance optimization for batch enrichment

### Next Steps

After completing the enrichment agent, proceed to:
- **08-analysis-agent.md** - Implement analysis agent that processes enriched data
- **09-summarizer-agent.md** - Implement summarizer agent that creates JSON briefings
