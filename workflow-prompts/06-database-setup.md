# Prompt 6: Database Setup (SQLite/ChromaDB)

## Objective

Create a database schema and data access layer for storing scraped news articles, funding rounds, launches, GitHub signals, and analysis results. The database runs **in-sandbox** within the E2B environment.

## Requirements

### Database Options

- **SQLite** (recommended for simplicity, zero-setup)
- **ChromaDB** (optional, for vector/embedding storage if needed for semantic search)

### Database Schema

**Database File:** `./storage/intelligence.db` (in-sandbox)

#### Tables to Create

1. **news** - Stores scraped news articles
2. **funding** - Stores funding round information
3. **launches** - Stores product/startup launches
4. **github_repositories** - Stores trending GitHub repositories
5. **github_signals** - Stores technical signals from GitHub
6. **analysis_results** - Stores LLM analysis outputs
7. **briefings** - Stores generated briefing summaries

### Table Schemas

#### 1. news Table

```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,  -- 'techcrunch', 'hackernews', 'producthunt'
    timestamp TEXT NOT NULL,  -- ISO format datetime
    summary TEXT,
    author TEXT,
    metadata TEXT,  -- JSON string for additional fields
    -- Enrichment fields
    keywords TEXT,  -- JSON array
    category TEXT,
    entities TEXT,  -- JSON object
    sentiment TEXT,
    related_article_ids TEXT,  -- JSON array
    enriched_at TEXT,
    is_enriched INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_news_source ON news(source);
CREATE INDEX idx_news_timestamp ON news(timestamp);
CREATE INDEX idx_news_url ON news(url);
CREATE INDEX idx_news_enriched ON news(is_enriched);
```

-- Note: For existing databases, use ALTER TABLE to add enrichment fields:
-- ALTER TABLE news ADD COLUMN keywords TEXT;
-- ALTER TABLE news ADD COLUMN category TEXT;
-- ALTER TABLE news ADD COLUMN entities TEXT;
-- ALTER TABLE news ADD COLUMN sentiment TEXT;
-- ALTER TABLE news ADD COLUMN related_article_ids TEXT;
-- ALTER TABLE news ADD COLUMN enriched_at TEXT;
-- ALTER TABLE news ADD COLUMN is_enriched INTEGER DEFAULT 0;
-- CREATE INDEX idx_news_enriched ON news(is_enriched);
```

#### 2. funding Table

```sql
CREATE TABLE funding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    funding_type TEXT,  -- 'Seed', 'Series A', etc.
    amount TEXT,  -- Human-readable: "$10M"
    amount_numeric REAL,  -- Numeric value for sorting/filtering
    currency TEXT DEFAULT 'USD',
    date TEXT NOT NULL,  -- ISO format date
    description TEXT,
    investors TEXT,  -- JSON array string
    category TEXT,
    link TEXT UNIQUE,
    source TEXT NOT NULL,
    -- Enrichment fields
    related_news_ids TEXT,  -- JSON array
    industry TEXT,
    investor_names TEXT,  -- JSON array
    related_github_repos TEXT,  -- JSON array
    stage TEXT,  -- 'pre_seed', 'seed', 'series_a', etc.
    enriched_at TEXT,
    is_enriched INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_funding_date ON funding(date);
CREATE INDEX idx_funding_type ON funding(funding_type);
CREATE INDEX idx_funding_category ON funding(category);
CREATE INDEX idx_funding_enriched ON funding(is_enriched);
```

-- Note: For existing databases, use ALTER TABLE to add enrichment fields:
-- ALTER TABLE funding ADD COLUMN related_news_ids TEXT;
-- ALTER TABLE funding ADD COLUMN industry TEXT;
-- ALTER TABLE funding ADD COLUMN investor_names TEXT;
-- ALTER TABLE funding ADD COLUMN related_github_repos TEXT;
-- ALTER TABLE funding ADD COLUMN stage TEXT;
-- ALTER TABLE funding ADD COLUMN enriched_at TEXT;
-- ALTER TABLE funding ADD COLUMN is_enriched INTEGER DEFAULT 0;
-- CREATE INDEX idx_funding_enriched ON funding(is_enriched);
```

#### 3. launches Table

```sql
CREATE TABLE launches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    launch_type TEXT,  -- 'product' or 'startup'
    description TEXT,
    date TEXT NOT NULL,  -- ISO format date
    category TEXT,
    link TEXT UNIQUE,
    founders TEXT,  -- JSON array string
    tagline TEXT,
    source TEXT NOT NULL,
    -- Enrichment fields
    related_github_repos TEXT,  -- JSON array
    product_category TEXT,
    related_news_ids TEXT,  -- JSON array
    technologies TEXT,  -- JSON array
    enriched_at TEXT,
    is_enriched INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_launches_date ON launches(date);
CREATE INDEX idx_launches_type ON launches(launch_type);
CREATE INDEX idx_launches_category ON launches(category);
CREATE INDEX idx_launches_enriched ON launches(is_enriched);
```

-- Note: For existing databases, use ALTER TABLE to add enrichment fields:
-- ALTER TABLE launches ADD COLUMN related_github_repos TEXT;
-- ALTER TABLE launches ADD COLUMN product_category TEXT;
-- ALTER TABLE launches ADD COLUMN related_news_ids TEXT;
-- ALTER TABLE launches ADD COLUMN technologies TEXT;
-- ALTER TABLE launches ADD COLUMN enriched_at TEXT;
-- ALTER TABLE launches ADD COLUMN is_enriched INTEGER DEFAULT 0;
-- CREATE INDEX idx_launches_enriched ON launches(is_enriched);
```

#### 4. github_repositories Table

```sql
CREATE TABLE github_repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    full_name TEXT UNIQUE NOT NULL,
    description TEXT,
    language TEXT,
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    watchers INTEGER DEFAULT 0,
    open_issues INTEGER DEFAULT 0,
    url TEXT NOT NULL,
    homepage TEXT,
    created_at TEXT NOT NULL,  -- ISO format datetime
    updated_at TEXT NOT NULL,
    pushed_at TEXT,
    topics TEXT,  -- JSON array string
    contributors_count INTEGER DEFAULT 0,
    metadata TEXT,  -- JSON string for additional fields
    is_enriched INTEGER DEFAULT 0,  -- Enrichment flag
    created_at_db TEXT DEFAULT (datetime('now')),
    updated_at_db TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_github_repos_stars ON github_repositories(stars);
CREATE INDEX idx_github_repos_language ON github_repositories(language);
CREATE INDEX idx_github_repos_updated ON github_repositories(updated_at);
CREATE INDEX idx_github_repos_enriched ON github_repositories(is_enriched);
```

#### 5. github_signals Table

```sql
CREATE TABLE github_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_type TEXT NOT NULL,  -- 'emerging_technology', 'startup_activity', 'tech_trend'
    repository_id INTEGER,
    repository_name TEXT,
    repository_url TEXT,
    indicator TEXT NOT NULL,
    confidence TEXT,  -- 'high', 'medium', 'low'
    date TEXT NOT NULL,  -- ISO format date
    metadata TEXT,  -- JSON string for additional fields
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (repository_id) REFERENCES github_repositories(id)
);

CREATE INDEX idx_github_signals_type ON github_signals(signal_type);
CREATE INDEX idx_github_signals_date ON github_signals(date);
CREATE INDEX idx_github_signals_confidence ON github_signals(confidence);
CREATE INDEX idx_github_signals_repo_id ON github_signals(repository_id);
```

#### 6. analysis_results Table

```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_type TEXT NOT NULL,  -- 'trends', 'opportunities', 'competitor_moves'
    data_date_range_start TEXT NOT NULL,
    data_date_range_end TEXT NOT NULL,
    results_json TEXT NOT NULL,  -- JSON string with analysis results
    model_used TEXT,  -- LLM model identifier
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_analysis_date_range ON analysis_results(data_date_range_start, data_date_range_end);
CREATE INDEX idx_analysis_type ON analysis_results(analysis_type);
```

#### 7. briefings Table

```sql
CREATE TABLE briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    briefing_date TEXT NOT NULL UNIQUE,  -- ISO format date (YYYY-MM-DD)
    summary_text TEXT NOT NULL,
    briefing_json TEXT NOT NULL,  -- Full JSON briefing
    data_start_date TEXT NOT NULL,
    data_end_date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_briefing_date ON briefings(briefing_date);
```

### Implementation

**File:** `backend/src/database/db.py`

```python
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "./storage/intelligence.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    @staticmethod
    def _validate_days(days: int) -> int:
        """Validate and sanitize days parameter to prevent SQL injection."""
        if not isinstance(days, int) or days < 1 or days > 365:
            raise ValueError("days must be an integer between 1 and 365")
        return days
    
    @staticmethod
    def _validate_limit(limit: Optional[int]) -> Optional[int]:
        """Validate and sanitize limit parameter to prevent SQL injection."""
        if limit is None:
            return None
        if not isinstance(limit, int) or limit < 1 or limit > 10000:
            raise ValueError("limit must be an integer between 1 and 10000")
        return limit
    
    def init_db(self):
        """Initialize database with all tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create all tables
        cursor.executescript("""
            -- news table (with enrichment fields)
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                summary TEXT,
                author TEXT,
                metadata TEXT,
                keywords TEXT,
                category TEXT,
                entities TEXT,
                sentiment TEXT,
                related_article_ids TEXT,
                enriched_at TEXT,
                is_enriched INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);
            CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news(timestamp);
            CREATE INDEX IF NOT EXISTS idx_news_url ON news(url);
            CREATE INDEX IF NOT EXISTS idx_news_enriched ON news(is_enriched);
            
            -- funding table (with enrichment fields)
            CREATE TABLE IF NOT EXISTS funding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                funding_type TEXT,
                amount TEXT,
                amount_numeric REAL,
                currency TEXT DEFAULT 'USD',
                date TEXT NOT NULL,
                description TEXT,
                investors TEXT,
                category TEXT,
                link TEXT UNIQUE,
                source TEXT NOT NULL,
                related_news_ids TEXT,
                industry TEXT,
                investor_names TEXT,
                related_github_repos TEXT,
                stage TEXT,
                enriched_at TEXT,
                is_enriched INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_funding_date ON funding(date);
            CREATE INDEX IF NOT EXISTS idx_funding_type ON funding(funding_type);
            CREATE INDEX IF NOT EXISTS idx_funding_category ON funding(category);
            CREATE INDEX IF NOT EXISTS idx_funding_enriched ON funding(is_enriched);
            
            -- launches table (with enrichment fields)
            CREATE TABLE IF NOT EXISTS launches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                launch_type TEXT,
                description TEXT,
                date TEXT NOT NULL,
                category TEXT,
                link TEXT UNIQUE,
                founders TEXT,
                tagline TEXT,
                source TEXT NOT NULL,
                related_github_repos TEXT,
                product_category TEXT,
                related_news_ids TEXT,
                technologies TEXT,
                enriched_at TEXT,
                is_enriched INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_launches_date ON launches(date);
            CREATE INDEX IF NOT EXISTS idx_launches_type ON launches(launch_type);
            CREATE INDEX IF NOT EXISTS idx_launches_category ON launches(category);
            CREATE INDEX IF NOT EXISTS idx_launches_enriched ON launches(is_enriched);
            
            -- github_repositories table
            CREATE TABLE IF NOT EXISTS github_repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT UNIQUE NOT NULL,
                description TEXT,
                language TEXT,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                watchers INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                url TEXT NOT NULL,
                homepage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                pushed_at TEXT,
                topics TEXT,
                contributors_count INTEGER DEFAULT 0,
                metadata TEXT,
                is_enriched INTEGER DEFAULT 0,
                created_at_db TEXT DEFAULT (datetime('now')),
                updated_at_db TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_github_repos_stars ON github_repositories(stars);
            CREATE INDEX IF NOT EXISTS idx_github_repos_language ON github_repositories(language);
            CREATE INDEX IF NOT EXISTS idx_github_repos_updated ON github_repositories(updated_at);
            CREATE INDEX IF NOT EXISTS idx_github_repos_enriched ON github_repositories(is_enriched);
            
            -- github_signals table
            CREATE TABLE IF NOT EXISTS github_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_type TEXT NOT NULL,
                repository_id INTEGER,
                repository_name TEXT,
                repository_url TEXT,
                indicator TEXT NOT NULL,
                confidence TEXT,
                date TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (repository_id) REFERENCES github_repositories(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_github_signals_type ON github_signals(signal_type);
            CREATE INDEX IF NOT EXISTS idx_github_signals_date ON github_signals(date);
            CREATE INDEX IF NOT EXISTS idx_github_signals_confidence ON github_signals(confidence);
            CREATE INDEX IF NOT EXISTS idx_github_signals_repo_id ON github_signals(repository_id);
            
            -- analysis_results table
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL,
                data_date_range_start TEXT NOT NULL,
                data_date_range_end TEXT NOT NULL,
                results_json TEXT NOT NULL,
                model_used TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_analysis_date_range ON analysis_results(data_date_range_start, data_date_range_end);
            CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);
            
            -- briefings table
            CREATE TABLE IF NOT EXISTS briefings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                briefing_date TEXT NOT NULL UNIQUE,
                summary_text TEXT NOT NULL,
                briefing_json TEXT NOT NULL,
                data_start_date TEXT NOT NULL,
                data_end_date TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE INDEX IF NOT EXISTS idx_briefing_date ON briefings(briefing_date);
        """)
        
        conn.commit()
        conn.close()
    
    # News methods
    def insert_news(self, articles: List[Dict]) -> int:
        """Insert news articles. Returns count of inserted articles."""
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        
        for article in articles:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO news 
                    (title, url, source, timestamp, summary, author, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.get('title'),
                    article.get('url'),
                    article.get('source'),
                    article.get('timestamp'),
                    article.get('summary'),
                    article.get('author'),
                    json.dumps(article.get('metadata', {}))
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                print(f"Error inserting news: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_recent_news(self, days: int = 7, source: Optional[str] = None, 
                       enriched: Optional[bool] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get recent news articles."""
        # Validate inputs to prevent SQL injection
        days = self._validate_days(days)
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        query = """
            SELECT * FROM news 
            WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
        """
        
        params = [str(days)]
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if enriched is not None:
            query += " AND is_enriched = ?"
            params.append(1 if enriched else 0)
        
        query += " ORDER BY timestamp DESC"
        
        # Validate limit before using in f-string
        if limit is not None:
            limit = self._validate_limit(limit)
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Funding methods
    def insert_funding(self, rounds: List[Dict]) -> int:
        """Insert funding rounds."""
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        
        for round_data in rounds:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO funding 
                    (company_name, funding_type, amount, amount_numeric, currency, 
                     date, description, investors, category, link, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    round_data.get('name') or round_data.get('company_name'),
                    round_data.get('type'),
                    round_data.get('amount'),
                    round_data.get('amount_numeric'),
                    round_data.get('currency', 'USD'),
                    round_data.get('date'),
                    round_data.get('description'),
                    json.dumps(round_data.get('investors', [])),
                    round_data.get('category'),
                    round_data.get('link'),
                    round_data.get('source')
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                print(f"Error inserting funding: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_recent_funding(self, days: int = 7, enriched: Optional[bool] = None, 
                          limit: Optional[int] = None) -> List[Dict]:
        """Get recent funding rounds."""
        # Validate inputs to prevent SQL injection
        days = self._validate_days(days)
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        query = """
            SELECT * FROM funding 
            WHERE date(date) >= date('now', '-' || ? || ' days')
        """
        
        params = [str(days)]
        if enriched is not None:
            query += " AND is_enriched = ?"
            params.append(1 if enriched else 0)
        
        query += " ORDER BY date DESC, amount_numeric DESC"
        
        # Validate limit before using in f-string
        if limit is not None:
            limit = self._validate_limit(limit)
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Launches methods
    def insert_launches(self, launches: List[Dict]) -> int:
        """Insert launches."""
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        
        for launch in launches:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO launches 
                    (name, launch_type, description, date, category, 
                     link, founders, tagline, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    launch.get('name'),
                    launch.get('type'),
                    launch.get('description'),
                    launch.get('date'),
                    launch.get('category'),
                    launch.get('link'),
                    json.dumps(launch.get('founders', [])),
                    launch.get('tagline'),
                    launch.get('source')
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                print(f"Error inserting launch: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_recent_launches(self, days: int = 7, enriched: Optional[bool] = None, 
                           limit: Optional[int] = None) -> List[Dict]:
        """Get recent launches."""
        # Validate inputs to prevent SQL injection
        days = self._validate_days(days)
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        query = """
            SELECT * FROM launches 
            WHERE date(date) >= date('now', '-' || ? || ' days')
        """
        
        params = [str(days)]
        if enriched is not None:
            query += " AND is_enriched = ?"
            params.append(1 if enriched else 0)
        
        query += " ORDER BY date DESC"
        
        # Validate limit before using in f-string
        if limit is not None:
            limit = self._validate_limit(limit)
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # GitHub repositories methods
    def insert_github_repositories(self, repositories: List[Dict]) -> int:
        """Insert GitHub repositories."""
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        
        for repo in repositories:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO github_repositories 
                    (name, full_name, description, language, stars, forks, watchers, 
                     open_issues, url, homepage, created_at, updated_at, pushed_at, 
                     topics, contributors_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    repo.get('name'),
                    repo.get('full_name'),
                    repo.get('description'),
                    repo.get('language'),
                    repo.get('stars', 0),
                    repo.get('forks', 0),
                    repo.get('watchers', 0),
                    repo.get('open_issues', 0),
                    repo.get('url'),
                    repo.get('homepage'),
                    repo.get('created_at'),
                    repo.get('updated_at'),
                    repo.get('pushed_at'),
                    json.dumps(repo.get('topics', [])),
                    repo.get('contributors_count', 0),
                    json.dumps(repo.get('metadata', {}))
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                print(f"Error inserting GitHub repository: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_recent_github_repos(self, days: int = 7, enriched: Optional[bool] = None, 
                                limit: Optional[int] = None) -> List[Dict]:
        """Get recent GitHub repositories."""
        # Validate inputs to prevent SQL injection
        days = self._validate_days(days)
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        query = """
            SELECT * FROM github_repositories 
            WHERE datetime(updated_at) >= datetime('now', '-' || ? || ' days')
        """
        
        params = [str(days)]
        if enriched is not None:
            query += " AND is_enriched = ?"
            params.append(1 if enriched else 0)
        
        query += " ORDER BY updated_at DESC, stars DESC"
        
        # Validate limit before using in f-string
        if limit is not None:
            limit = self._validate_limit(limit)
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # GitHub signals methods
    def insert_github_signals(self, signals: List[Dict]) -> int:
        """Insert GitHub signals."""
        conn = self.get_connection()
        cursor = conn.cursor()
        inserted = 0
        
        for signal in signals:
            try:
                # Get repository_id if repository_name is provided
                repository_id = None
                if signal.get('repository_name'):
                    cursor.execute("""
                        SELECT id FROM github_repositories 
                        WHERE full_name = ? OR name = ?
                        LIMIT 1
                    """, (signal.get('repository_name'), signal.get('repository_name')))
                    repo_row = cursor.fetchone()
                    if repo_row:
                        repository_id = repo_row[0]
                
                cursor.execute("""
                    INSERT INTO github_signals 
                    (signal_type, repository_id, repository_name, repository_url, 
                     indicator, confidence, date, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal.get('signal_type'),
                    repository_id,
                    signal.get('repository_name'),
                    signal.get('repository_url'),
                    signal.get('indicator'),
                    signal.get('confidence'),
                    signal.get('date'),
                    json.dumps(signal.get('metadata', {}))
                ))
                inserted += 1
            except sqlite3.Error as e:
                print(f"Error inserting GitHub signal: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_recent_github_signals(self, days: int = 7, limit: Optional[int] = None) -> List[Dict]:
        """Get recent GitHub signals."""
        # Validate inputs to prevent SQL injection
        days = self._validate_days(days)
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        query = """
            SELECT * FROM github_signals 
            WHERE date(date) >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """
        
        params = [str(days)]
        
        # Validate limit before using in f-string
        if limit is not None:
            limit = self._validate_limit(limit)
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Update enrichment methods
    def update_news_enrichment(self, article_id: int, enriched_data: Dict):
        """Update news article with enrichment data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE news SET
                keywords = ?,
                category = ?,
                entities = ?,
                sentiment = ?,
                related_article_ids = ?,
                enriched_at = ?,
                is_enriched = 1,
                updated_at = datetime('now')
            WHERE id = ?
        """, (
            json.dumps(enriched_data.get('keywords', [])),
            enriched_data.get('category'),
            json.dumps(enriched_data.get('entities', {})),
            enriched_data.get('sentiment'),
            json.dumps(enriched_data.get('related_article_ids', [])),
            enriched_data.get('enriched_at', datetime.now().isoformat()),
            article_id
        ))
        
        conn.commit()
        conn.close()
    
    def update_funding_enrichment(self, funding_id: int, enriched_data: Dict):
        """Update funding round with enrichment data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE funding SET
                related_news_ids = ?,
                industry = ?,
                investor_names = ?,
                related_github_repos = ?,
                stage = ?,
                enriched_at = ?,
                is_enriched = 1,
                updated_at = datetime('now')
            WHERE id = ?
        """, (
            json.dumps(enriched_data.get('related_news_ids', [])),
            enriched_data.get('industry'),
            json.dumps(enriched_data.get('investor_names', [])),
            json.dumps(enriched_data.get('related_github_repos', [])),
            enriched_data.get('stage'),
            enriched_data.get('enriched_at', datetime.now().isoformat()),
            funding_id
        ))
        
        conn.commit()
        conn.close()
    
    def update_launch_enrichment(self, launch_id: int, enriched_data: Dict):
        """Update launch with enrichment data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE launches SET
                related_github_repos = ?,
                product_category = ?,
                related_news_ids = ?,
                technologies = ?,
                enriched_at = ?,
                is_enriched = 1,
                updated_at = datetime('now')
            WHERE id = ?
        """, (
            json.dumps(enriched_data.get('related_github_repos', [])),
            enriched_data.get('product_category'),
            json.dumps(enriched_data.get('related_news_ids', [])),
            json.dumps(enriched_data.get('technologies', [])),
            enriched_data.get('enriched_at', datetime.now().isoformat()),
            launch_id
        ))
        
        conn.commit()
        conn.close()
    
    def update_github_repo_enrichment(self, repo_id: int, enriched_data: Dict):
        """Update GitHub repository with enrichment data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE github_repositories SET
                metadata = ?,
                is_enriched = 1,
                updated_at_db = datetime('now')
            WHERE id = ?
        """, (
            json.dumps(enriched_data),
            repo_id
        ))
        
        conn.commit()
        conn.close()
    
    # Count methods
    def count_recent_news(self, days: int) -> int:
        """Count recent news articles."""
        # Validate input to prevent SQL injection
        days = self._validate_days(days)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        cursor.execute("""
            SELECT COUNT(*) FROM news 
            WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
        """, (str(days),))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_recent_funding(self, days: int) -> int:
        """Count recent funding rounds."""
        # Validate input to prevent SQL injection
        days = self._validate_days(days)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        cursor.execute("""
            SELECT COUNT(*) FROM funding 
            WHERE date(date) >= date('now', '-' || ? || ' days')
        """, (str(days),))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_recent_launches(self, days: int) -> int:
        """Count recent launches."""
        # Validate input to prevent SQL injection
        days = self._validate_days(days)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        cursor.execute("""
            SELECT COUNT(*) FROM launches 
            WHERE date(date) >= date('now', '-' || ? || ' days')
        """, (str(days),))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_recent_github_repos(self, days: int) -> int:
        """Count recent GitHub repositories."""
        # Validate input to prevent SQL injection
        days = self._validate_days(days)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with string concatenation for date calculation
        cursor.execute("""
            SELECT COUNT(*) FROM github_repositories 
            WHERE datetime(updated_at) >= datetime('now', '-' || ? || ' days')
        """, (str(days),))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # Helper search methods (used by enrichment agent)
    def find_articles_by_keywords(self, keywords: List[str], exclude_id: Optional[int] = None, 
                                  limit: int = 5) -> List[Dict]:
        """Find articles by keywords."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Search for any keyword match
        results = []
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            # Build query for this keyword
            query = """
                SELECT * FROM news 
                WHERE (title LIKE ? OR summary LIKE ?)
            """
            params = [f"%{keyword}%", f"%{keyword}%"]
            
            if exclude_id:
                query += " AND id != ?"
                params.append(exclude_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            # Execute query for this keyword
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            results.extend([dict(row) for row in rows])
        
        conn.close()
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    def search_articles(self, query_text: str, limit: int = 5) -> List[Dict]:
        """Search articles by text."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM news 
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query_text}%", f"%{query_text}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_github_repos(self, query_text: str, limit: int = 5) -> List[Dict]:
        """Search GitHub repositories by text."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM github_repositories 
            WHERE name LIKE ? OR full_name LIKE ? OR description LIKE ?
            ORDER BY stars DESC
            LIMIT ?
        """, (f"%{query_text}%", f"%{query_text}%", f"%{query_text}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_funding(self, query_text: str, limit: int = 3) -> List[Dict]:
        """Search funding by company name."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM funding 
            WHERE company_name LIKE ? OR description LIKE ?
            ORDER BY date DESC
            LIMIT ?
        """, (f"%{query_text}%", f"%{query_text}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_launches(self, query_text: str, limit: int = 3) -> List[Dict]:
        """Search launches by name."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM launches 
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY date DESC
            LIMIT ?
        """, (f"%{query_text}%", f"%{query_text}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Search by keywords methods (for analysis agent)
    def search_articles_by_keywords(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Search articles by keywords list (for analysis agent)."""
        return self.find_articles_by_keywords(keywords, exclude_id=None, limit=limit)
    
    def search_funding_by_keywords(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Search funding rounds by keywords list."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        results = []
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            cursor.execute("""
                SELECT * FROM funding 
                WHERE company_name LIKE ? OR description LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", limit))
            
            rows = cursor.fetchall()
            results.extend([dict(row) for row in rows])
        
        conn.close()
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    def search_launches_by_keywords(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Search launches by keywords list."""
        # Validate limit to prevent SQL injection
        limit = self._validate_limit(limit)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        results = []
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            cursor.execute("""
                SELECT * FROM launches 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", limit))
            
            rows = cursor.fetchall()
            results.extend([dict(row) for row in rows])
        
        conn.close()
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    # Analysis methods
    def save_analysis_result(self, analysis_type: str, date_start: str, 
                            date_end: str, results_json: Dict, model_used: str):
        """Save analysis results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_results 
            (analysis_type, data_date_range_start, data_date_range_end, 
             results_json, model_used)
            VALUES (?, ?, ?, ?, ?)
        """, (
            analysis_type,
            date_start,
            date_end,
            json.dumps(results_json),
            model_used
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_analysis(self) -> Optional[Dict]:
        """Get latest analysis results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analysis_results 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            result['results_json'] = json.loads(result['results_json'])
            return result
        return None
    
    # Briefing methods
    def save_briefing(self, briefing_date: str, summary_text: str, 
                     briefing_json: Dict, data_start_date: str, data_end_date: str):
        """Save briefing."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO briefings 
            (briefing_date, summary_text, briefing_json, data_start_date, data_end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            briefing_date,
            summary_text,
            json.dumps(briefing_json),
            data_start_date,
            data_end_date
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_briefing(self) -> Optional[Dict]:
        """Get latest briefing."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM briefings 
            ORDER BY briefing_date DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            result['briefing_json'] = json.loads(result['briefing_json'])
            return result
        return None
    
    def get_briefing_by_date(self, date: str) -> Optional[Dict]:
        """Get briefing for a specific date."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM briefings 
            WHERE briefing_date = ?
        """, (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            result['briefing_json'] = json.loads(result['briefing_json'])
            return result
        return None
```

### Usage in Orchestrator

The orchestrator agent will use this database module to:
1. Store scraped news articles
2. Store funding rounds from API wrapper
3. Store launches from API wrapper
4. Retrieve recent data for analysis
5. Save analysis results
6. Save and retrieve briefings

### Testing

```python
from database.db import Database

# Initialize database
db = Database("./storage/intelligence.db")

# Test inserting news
news_articles = [
    {
        "title": "Test Article",
        "url": "https://example.com/article",
        "source": "techcrunch",
        "timestamp": "2024-01-15T10:00:00Z",
        "summary": "Test summary",
        "author": "Test Author"
    }
]
inserted = db.insert_news(news_articles)
print(f"Inserted {inserted} news articles")

# Test retrieving news
recent = db.get_recent_news(days=7)
print(f"Retrieved {len(recent)} recent articles")
```

### Deliverables

1. Complete database schema with all tables
2. Database initialization script
3. Data access layer with CRUD operations
4. Indexes for performance
5. Error handling and logging
6. Usage examples and tests

### Next Steps

After completing the database setup, integrate it with:
- **04-orchestrator-agent.md** - Use database to store collected data
- **06-analysis-agent.md** - Query database for analysis input
