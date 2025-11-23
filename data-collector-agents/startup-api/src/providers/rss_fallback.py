"""RSS feed provider as fallback when APIs are unavailable."""
import feedparser
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse

from ..config import TIMEOUT


def validate_url(url: Optional[str]) -> Optional[str]:
    """
    Validate URL and return it if valid, None otherwise.
    
    Args:
        url: URL string to validate
        
    Returns:
        Valid URL string or None if invalid/empty
    """
    if not url or not url.strip():
        return None
    
    url = url.strip()
    
    # Basic URL validation using urlparse
    try:
        parsed = urlparse(url)
        # Check if URL has a scheme and netloc (basic validation)
        if parsed.scheme and parsed.netloc:
            # Additional check: ensure it's http or https
            if parsed.scheme in ('http', 'https'):
                return url
    except Exception:
        pass
    
    # If validation fails, return None
    return None


async def parse_funding_from_rss(url: str, days_back: int = 7) -> List[Dict]:
    """Parse funding rounds from RSS feed."""
    try:
        # Convert TIMEOUT from milliseconds to seconds for httpx
        timeout_seconds = TIMEOUT / 1000.0
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"Error fetching RSS feed {url}: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    funding_rounds = []
    
    for entry in feed.entries:
        try:
            published = datetime(*entry.published_parsed[:6])
            if published < cutoff_date:
                continue
            
            # Extract funding information from title/description
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            content = title + " " + summary
            
            # Try to extract funding amount
            amount_match = re.search(r'\$(\d+(?:\.\d+)?)\s*([MBK]|million|billion|thousand)', content, re.IGNORECASE)
            amount = ""
            amount_numeric = None
            
            if amount_match:
                num = float(amount_match.group(1))
                unit = amount_match.group(2).upper()
                if unit in ['B', 'BILLION']:
                    amount_numeric = num * 1_000_000_000
                    amount = f"${num}B"
                elif unit in ['M', 'MILLION']:
                    amount_numeric = num * 1_000_000
                    amount = f"${num}M"
                elif unit in ['K', 'THOUSAND']:
                    amount_numeric = num * 1_000
                    amount = f"${num}K"
            
            # Extract round type
            round_type = "Unknown"
            if re.search(r'series\s+[abc]', content, re.IGNORECASE):
                match = re.search(r'series\s+([abc])', content, re.IGNORECASE)
                if match:
                    round_type = f"Series {match.group(1).upper()}"
            elif re.search(r'seed', content, re.IGNORECASE):
                round_type = "Seed"
            elif re.search(r'pre-seed', content, re.IGNORECASE):
                round_type = "Pre-Seed"
            
            # Extract company name from title
            name = title.split(" raises")[0].strip()
            if not name or len(name) > 200:
                name = title[:100]
            
            # Validate and sanitize URL before passing to Pydantic
            raw_link = entry.get("link")
            validated_link = validate_url(raw_link)
            
            funding_rounds.append({
                "name": name,
                "type": round_type,
                "amount": amount or "Undisclosed",
                "amount_numeric": amount_numeric,
                "currency": "USD",
                "date": published.strftime("%Y-%m-%d"),
                "description": summary[:500] if summary else "",
                "investors": [],
                "category": None,
                "link": validated_link,  # Validated URL or None (safe for Pydantic Optional[HttpUrl])
                "source": "techcrunch_rss"
            })
        except Exception as e:
            print(f"Error parsing RSS entry: {e}")
            continue
    
    return funding_rounds


async def parse_launches_from_rss(url: str, days_back: int = 7) -> List[Dict]:
    """Parse product launches from RSS feed."""
    try:
        # Convert TIMEOUT from milliseconds to seconds for httpx
        timeout_seconds = TIMEOUT / 1000.0
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"Error fetching RSS feed {url}: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    launches = []
    
    for entry in feed.entries:
        try:
            published = datetime(*entry.published_parsed[:6])
            if published < cutoff_date:
                continue
            
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            
            # Validate and sanitize URL before passing to Pydantic
            raw_link = entry.get("link")
            validated_link = validate_url(raw_link)
            
            launches.append({
                "name": title[:100],
                "type": "product",
                "description": summary[:500] if summary else "",
                "date": published.strftime("%Y-%m-%d"),
                "category": None,
                "link": validated_link,  # Validated URL or None (safe for Pydantic Optional[HttpUrl])
                "founders": [],
                "tagline": None,
                "source": "techcrunch_rss"
            })
        except Exception as e:
            print(f"Error parsing RSS entry: {e}")
            continue
    
    return launches

