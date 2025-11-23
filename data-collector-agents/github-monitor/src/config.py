"""Configuration for github-monitor agent."""
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "3003"))
NODE_ENV = os.getenv("NODE_ENV", "production")
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # 15 minutes in seconds
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # 30 seconds in milliseconds

# GitHub API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional, for higher rate limits
GITHUB_API_URL = "https://api.github.com"

# Rate limiting
RATE_LIMIT_MAX = 60  # GitHub allows 60 requests/hour without token
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

