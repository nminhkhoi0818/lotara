"""
Centralized Logging Configuration for Travel Lotara
===================================================
Provides consistent logging across all modules with environment-based control.

Usage:
    from src.travel_lotara.config.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Info message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")

Environment Variables:
    LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Default: INFO
    LOG_FORMAT: Set log format (simple, detailed, json)
                Default: detailed
"""

import logging
import sys
import os
from typing import Optional

# Log level mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Log formats
LOG_FORMATS = {
    "simple": "%(levelname)s - %(message)s",
    "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "json": '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
}

# Global configuration
_configured = False
_log_level = None
_log_format = None


def configure_logging(
    level: Optional[str] = None,
    format_type: Optional[str] = None,
    force: bool = False
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format (simple, detailed, json)
        force: Force reconfiguration even if already configured
    """
    global _configured, _log_level, _log_format
    
    if _configured and not force:
        return
    
    # Get configuration from environment or parameters
    _log_level = (
        level or 
        os.getenv("LOG_LEVEL", "INFO")
    ).upper()
    
    _log_format = (
        format_type or 
        os.getenv("LOG_FORMAT", "detailed")
    ).lower()
    
    # Validate log level
    if _log_level not in LOG_LEVELS:
        _log_level = "INFO"
    
    # Validate log format
    if _log_format not in LOG_FORMATS:
        _log_format = "detailed"
    
    # Configure root logger
    logging.basicConfig(
        level=LOG_LEVELS[_log_level],
        format=LOG_FORMATS[_log_format],
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=force
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("pymilvus").setLevel(logging.WARNING)
    logging.getLogger("google.genai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    # Auto-configure on first use
    if not _configured:
        configure_logging()
    
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Dynamically change log level at runtime.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _log_level
    
    level = level.upper()
    if level in LOG_LEVELS:
        _log_level = level
        logging.getLogger().setLevel(LOG_LEVELS[level])


def get_current_log_level() -> str:
    """Get the current log level."""
    if not _configured:
        configure_logging()
    return _log_level


# Auto-configure on import
configure_logging()
