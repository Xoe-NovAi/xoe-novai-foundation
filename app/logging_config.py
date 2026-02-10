#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Logging Configuration
# ============================================================================
# Purpose: Centralized logging configuration for the Xoe-NovAi system
# Guide Reference: Section 4.2 (Logging Infrastructure)
# Last Updated: 2026-01-28 (Created for logging configuration)
# ============================================================================

import logging
import json
import time
import os
from logging import Logger
from typing import Optional, Any, Dict

# Try to import OpenTelemetry for trace context
try:
    from opentelemetry import trace
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# ============================================================================
# LOGGING LEVELS
# ============================================================================

# Define custom logging levels
TRACE = 5
VERBOSE = 15

# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

class JsonFormatter(logging.Formatter):
    """
    CLAUDE STANDARD: Structured JSON formatter for observability.
    
    Research: OpenTelemetry Logging Specification 2024
    - Includes trace/span IDs if available
    - Standardized field names
    - Elastic-compatible mapping
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Add trace context if available
        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                log_data["trace_id"] = format(span.get_span_context().trace_id, '032x')
                log_data["span_id"] = format(span.get_span_context().span_id, '016x')

        # Add extra fields from 'extra' keyword or custom attributes
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        # Add any other custom attributes passed in the record
        # but avoid standard record attributes
        standard_attrs = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_data[key] = value

        return json.dumps(log_data)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    file_mode: str = "a",
    format_str: str = None,
    structured: bool = None
) -> Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
        console: Whether to log to console
        file_mode: File mode
        format_str: Custom format string
        structured: Whether to use JSON logging (defaults to env LOG_STRUCTURED)
    """
    if structured is None:
        structured = os.getenv("LOG_STRUCTURED", "false").lower() == "true"

    # Define default format
    if format_str is None:
        if structured:
            format_str = "%(message)s"
        else:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Create formatter
    if structured:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(format_str)

    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file).parent
            log_path.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, mode=file_mode)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file handler: {e}")

    return root_logger

def get_logger(name: str = "xnai") -> Logger:
    """
    Get a logger instance with the specified name.
    
    Research: Consistent logger naming for filtering.
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
    'JsonFormatter',
    'TRACE',
    'VERBOSE'
]