"""
Logging Configuration for CIT v2.1
Centralized logging setup with consistent formatting.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    logger_name: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging with consistent format.
    
    Args:
        level: Logging level (default: INFO)
        log_format: Custom format string (optional)
        logger_name: Logger name (default: __name__)
    
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    
    # Configure basic logging only once
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format=log_format,
            stream=sys.stdout
        )
    
    # Return named logger
    if logger_name:
        return logging.getLogger(logger_name)
    
    return logging.getLogger()


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get or create a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
