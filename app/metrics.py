#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Performance Metrics
# ============================================================================
# Purpose: Performance logging and metrics collection for the Xoe-NovAi system
# Guide Reference: Section 4.3 (Performance Monitoring)
# Last Updated: 2026-01-28 (Created for performance metrics)
# ============================================================================

from typing import Optional, Dict, Any
from datetime import datetime
import time
import logging

# ============================================================================
# PERFORMANCE LOGGER
# ============================================================================

class PerformanceLogger:
    """
    Performance Logger for tracking and logging performance metrics.

    Integrates with the logging system to provide structured performance data.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the PerformanceLogger.

        Args:
            logger: Optional logger instance (defaults to root logger)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, metric_name: str) -> None:
        """
        Start a timer for a specific metric.

        Args:
            metric_name: Name of the metric to track
        """
        self.start_times[metric_name] = time.perf_counter()
        self.logger.debug(f"Started timer for metric: {metric_name}")

    def stop_timer(self, metric_name: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Stop a timer for a specific metric and log the duration.

        Args:
            metric_name: Name of the metric to stop
            metadata: Optional metadata to include with the metric

        Returns:
            Duration in seconds
        """
        if metric_name not in self.start_times:
            self.logger.warning(f"Timer not started for metric: {metric_name}")
            return 0.0

        end_time = time.perf_counter()
        duration = end_time - self.start_times[metric_name]
        del self.start_times[metric_name]

        # Log the metric
        self.log_metric(metric_name, duration, metadata)

        return duration

    def log_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            metadata: Optional metadata to include
        """
        timestamp = datetime.utcnow().isoformat()
        metric_data = {
            'timestamp': timestamp,
            'metric_name': metric_name,
            'value': value,
            'metadata': metadata or {}
        }

        self.metrics[metric_name] = metric_data
        self.logger.info(f"Performance metric: {metric_name} = {value}", extra=metric_data)

    def get_metric(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a previously logged metric.

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            Metric data or None if not found
        """
        return self.metrics.get(metric_name)

    def reset_metrics(self) -> None:
        """
        Reset all collected metrics.
        """
        self.metrics = {}
        self.start_times = {}
        self.logger.info("Performance metrics reset")

    def log_performance(self, operation: str, duration: float, success: bool = True, **kwargs) -> None:
        """
        Log a complete performance record for an operation.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether the operation was successful
            **kwargs: Additional metadata
        """
        metadata = {
            'operation': operation,
            'duration': duration,
            'success': success,
            **kwargs
        }
        self.log_metric(f"performance.{operation}", duration, metadata)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'PerformanceLogger'
]