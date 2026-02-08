"""
OpenAI Configuration for CIT v2.1
Centralized OpenAI API configuration management.
"""
import os
from typing import Optional


def get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get OpenAI API key from environment or parameter.
    
    Priority:
    1. Explicit api_key parameter
    2. CIT_OPENAI_API_KEY environment variable
    3. OPENAI_API_KEY environment variable
    4. Empty string (default)
    
    Args:
        api_key: Explicit API key (optional)
    
    Returns:
        API key string
    """
    return api_key or os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""


def get_model(model: Optional[str] = None) -> str:
    """
    Get OpenAI model from environment or parameter.
    
    Priority:
    1. Explicit model parameter
    2. CIT_OPENAI_MODEL environment variable
    3. CIT_MODEL environment variable
    4. OPENAI_MODEL environment variable
    5. "gpt-4o-mini" (default)
    
    Args:
        model: Explicit model name (optional)
    
    Returns:
        Model name string
    """
    return (
        model 
        or os.getenv("CIT_OPENAI_MODEL") 
        or os.getenv("CIT_MODEL") 
        or os.getenv("OPENAI_MODEL") 
        or "gpt-4o-mini"
    )
