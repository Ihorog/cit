"""
Time Utilities for CIT v2.1
Consistent timestamp generation across the application.
"""
from datetime import datetime, timezone


def now_utc_iso() -> str:
    """
    Get current UTC time in ISO 8601 format.
    
    Returns:
        ISO 8601 timestamp string (e.g., "2024-01-15T10:30:45.123456+00:00")
    """
    return datetime.now(timezone.utc).isoformat()


def now_utc_formatted() -> str:
    """
    Get current UTC time in human-readable format.
    
    Returns:
        Formatted timestamp string (e.g., "2024-01-15 10:30:45")
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
