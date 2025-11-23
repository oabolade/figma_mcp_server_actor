"""LLM client for OpenAI and Anthropic."""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with LLM providers (OpenAI, Anthropic)."""
    
    def __init__(self, provider: str, model: str, api_key: Optional[str]):
        """
        Initialize LLM client.
        
        Args:
            provider: 'openai' or 'anthropic'
            model: Model identifier (e.g., 'gpt-4-turbo-preview', 'claude-3-opus-20240229')
            api_key: API key for the provider (can be None if not configured)
        
        Raises:
            ValueError: If api_key is None when trying to use the client
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.http_client = httpx.AsyncClient(timeout=60.0)
    
    def _validate_api_key(self):
        """Validate that API key is configured."""
        if not self.api_key:
            raise ValueError(
                f"LLM API key not configured. Please set {self.provider.upper()}_API_KEY "
                f"environment variable. Provider: {self.provider}, Model: {self.model}"
            )
    
    async def complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Complete a prompt using the configured LLM provider."""
        # Validate API key before making requests
        self._validate_api_key()
        
        if self.provider == "openai":
            return await self._complete_openai(prompt, temperature, max_tokens)
        elif self.provider == "anthropic":
            return await self._complete_anthropic(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def _complete_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Complete using OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a startup intelligence analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.http_client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _complete_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Complete using Anthropic API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = await self.http_client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()

