#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Logging Configuration
# ============================================================================
# Purpose: Centralized logging configuration for the Xoe-NovAi system
# Guide Reference: Section 4.2 (Logging Infrastructure)
# Last Updated: 2026-01-28 (Created for logging configuration)
# ============================================================================

import logging
from logging import Logger
from typing import Optional

# ============================================================================
# LOGGING LEVELS
# ============================================================================

# Define custom logging levels
TRACE = 5
VERBOSE = 15

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    file_mode: str = "a",
    format_str: str = None
) -> Logger:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console
        file_mode: File mode for log file ('a' for append, 'w' for write)
        format_str: Custom log format string

    Returns:
        Configured logger instance
    """
    # Define default format
    if format_str is None:
        format_str = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=format_str,
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, mode=file_mode)
        file_handler.setFormatter(logging.Formatter(format_str))
        logging.getLogger().addHandler(file_handler)

    # Get and return the root logger
    logger = logging.getLogger()
    return logger

def get_logger(name: str = __name__) -> Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# ============================================================================
# CUSTOM LOGGING LEVELS
# ============================================================================

def add_custom_logging_levels():
    """
    Add custom logging levels to the logging module.
    """
    logging.addLevelName(TRACE, "TRACE")
    logging.addLevelName(VERBOSE, "VERBOSE")

def trace(self, message, *args, **kwargs):
    """
    Log a message at the TRACE level.
    """
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

def verbose(self, message, *args, **kwargs):
    """
    Log a message at the VERBOSE level.
    """
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)

# Add custom methods to Logger class
logging.Logger.trace = trace
logging.Logger.verbose = verbose

# Initialize custom logging levels
add_custom_logging_levels()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'setup_logging',
    'get_logger',
    'TRACE',
    'VERBOSE'
]