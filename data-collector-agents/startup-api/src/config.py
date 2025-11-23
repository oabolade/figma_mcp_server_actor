"""Configuration for startup-api agent."""
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "3002"))
NODE_ENV = os.getenv("NODE_ENV", "production")
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # 15 minutes in seconds
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # 30 seconds in milliseconds

# API Keys (optional, for premium APIs)
CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")
ANGEL_LIST_API_KEY = os.getenv("ANGEL_LIST_API_KEY", "")

# RSS Feeds
TECHCRUNCH_FUNDING_RSS = "https://techcrunch.com/tag/funding/feed/"
TECHCRUNCH_STARTUPS_RSS = "https://techcrunch.com/tag/startups/feed/"

# Rate limiting
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60  # seconds

