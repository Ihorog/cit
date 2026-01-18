"""
OpenAI Client for CIT v2.1
Autonomous client for OpenAI API interactions.
Supports intelligent routing between Responses API and Chat Completions API.
"""

import json
import os
import urllib.request
import urllib.error
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Autonomous OpenAI API client with intelligent routing.
    
    Features:
    - Primary: Responses API (simplified single-turn)
    - Fallback: Chat Completions API
    - No external dependencies (uses urllib)
    - Environment-based configuration
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to env: CIT_OPENAI_API_KEY or OPENAI_API_KEY)
            model: Model to use (defaults to env: CIT_OPENAI_MODEL or gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        self.model = model or os.getenv("CIT_OPENAI_MODEL") or os.getenv("CIT_MODEL") or "gpt-4o-mini"
        
    def set_api_key(self, api_key: str):
        """Update API key"""
        self.api_key = api_key
        
    def set_model(self, model: str):
        """Update model"""
        self.model = model
        
    def _request(self, url: str, payload: Dict) -> Dict:
        """
        Make HTTP POST request to OpenAI API.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            
        Returns:
            Response dictionary
        """
        if not self.api_key:
            logger.error("OpenAI API key not set")
            return {"error": "API key not set"}
            
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        
        try:
            logger.debug(f"OpenAI request to {url}")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            logger.error(f"OpenAI HTTP error {e.code}: {url}")
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            return {"error": f"HTTPError {e.code}", "body": body}
        except Exception as e:
            logger.error(f"OpenAI request exception: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Send chat message with intelligent API routing.
        
        Primary: Responses API (simplified) - NOTE: This endpoint may not exist in OpenAI's API.
                 The implementation maintains backward compatibility with existing CIT behavior.
        Fallback: Chat Completions API (standard, always works)
        
        In practice, the fallback is always used, but the primary attempt is maintained
        for compatibility with existing CIT architecture.
        
        Args:
            message: User message
            system_prompt: Optional system prompt (only used with Chat Completions)
            
        Returns:
            Dictionary with:
            - reply: Assistant's response text
            - api: API used ("responses" or "chat.completions")
            - raw: Raw API response
        """
        # Try Responses API first (may not be a real endpoint, but maintains compatibility)
        resp = self._request(
            "https://api.openai.com/v1/responses",
            {
                "model": self.model,
                "input": message,
            },
        )
        
        # Check if Responses API succeeded
        if isinstance(resp, dict) and "output_text" in resp and resp.get("output_text"):
            return {
                "reply": resp["output_text"],
                "api": "responses",
                "raw": resp
            }
        
        # Fallback to Chat Completions API
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        resp2 = self._request(
            "https://api.openai.com/v1/chat/completions",
            {
                "model": self.model,
                "messages": messages,
            },
        )
        
        try:
            reply = resp2["choices"][0]["message"]["content"]
            return {
                "reply": reply,
                "api": "chat.completions",
                "raw": resp2
            }
        except Exception as e:
            logger.error(f"Failed to extract reply from Chat Completions: {e}")
            return {
                "reply": "",
                "api": "chat.completions",
                "raw": resp2,
                "error": str(e)
            }
    
    def chat_stream(self, message: str, system_prompt: Optional[str] = None):
        """
        Stream chat response (future implementation).
        Currently not implemented - returns regular chat response.
        """
        return self.chat(message, system_prompt)
