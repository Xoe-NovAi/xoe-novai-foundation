#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 1 v0.1.1 - Prometheus Metrics Module
# ============================================================================
# Purpose: Real-time metrics collection and exposure for monitoring
# Guide Reference: Section 5.2 (Prometheus Metrics)
# Last Updated: 2025-10-11
# Features:
#   - 9 metrics (3 gauges, 2 histograms, 4 counters)
#   - Automatic background updates (30s interval)
#   - HTTP server on port 8002
#   - Multiprocess mode for Gunicorn/Uvicorn
#   - Performance targets validation
# ============================================================================

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from pathlib import Path

# Prometheus client
from prometheus_client import (
    start_http_server,
    Gauge,
    Histogram,
    Counter,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    multiprocess,
    MetricsHandler
)

# System monitoring
import psutil

# Configuration
try:
    from XNAi_rag_app.core.config_loader import load_config, get_config_value
except ImportError:
    # Fallback for testing
    def load_config():
        return {
            'performance': {
                'memory_limit_gb': 8.0,
                'memory_warning_threshold_gb': 6.0,
                'token_rate_min': 10,
                'token_rate_max': 50,
                'cpu_threads': 12,
                'f16_kv_enabled': True
            },
            'metadata': {
                'stack_version': 'v0.1.0-alpha',
                'codename': 'Sovereign Foundation',
                'architecture': 'CPU-Vulkan Hybrid',
                'phase': 1
            },
            'metrics': {
                'enabled': True,
                'port': 8002,
                'update_interval_s': 30,
                'multiproc_dir': '/prometheus_data'
            }
        }

    def get_config_value(key_path, default=None):
        config = load_config()
        keys = key_path.split('.')
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

logger = logging.getLogger(__name__)
CONFIG = load_config()

# ============================================================================
# METRICS DEFINITIONS
# ============================================================================

# Gauges (current state)
memory_usage_bytes = Gauge(
    'xnai_memory_usage_bytes',
    'Current memory usage in bytes',
    ['component']  # Labels: 'system', 'process', 'llm', 'embeddings'
)

# Keep legacy GB metric for backward compatibility
memory_usage_gb = Gauge(
    'xnai_memory_usage_gb',
    'Current memory usage in gigabytes (DEPRECATED)',
    ['component']  # Labels: 'system', 'process', 'llm', 'embeddings'
)

token_rate_tps = Gauge(
    'xnai_token_rate_tps',
    'Token generation rate in tokens per second',
    ['model']  # Labels: 'gemma-3-4b'
)

active_sessions = Gauge(
    'xnai_active_sessions',
    'Number of active user sessions'
)

# Histograms (distributions)
response_latency_ms = Histogram(
    'xnai_response_latency_ms',
    'API response latency in milliseconds',
    ['endpoint', 'method'],  # Labels: endpoint path, HTTP method
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000, 10000]  # Milliseconds
)

rag_retrieval_time_ms = Histogram(
    'xnai_rag_retrieval_time_ms',
    'RAG document retrieval time in milliseconds',
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000]
)

# Counters (cumulative)
requests_total = Counter(
    'xnai_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']  # Labels: path, method, status code
)

errors_total = Counter(
    'xnai_errors_total',
    'Total number of errors',
    ['error_type', 'component']  # Labels: error type, component name
)

tokens_generated_total = Counter(
    'xnai_tokens_generated_total',
    'Total tokens generated',
    ['model']  # Labels: model name
)

queries_processed_total = Counter(
    'xnai_queries_processed_total',
    'Total queries processed',
    ['rag_enabled']  # Labels: 'true', 'false'
)

# ============================================================================
# ENHANCED METRICS FOR HARDWARE BENCHMARKING, PERSONA TUNING & KNOWLEDGE BASES
# ============================================================================

# Hardware Benchmarking Metrics
hardware_performance = Gauge(
    'xnai_hardware_performance',
    'Hardware acceleration performance metrics',
    ['hardware_type', 'model_size', 'operation_type']
)

vulkan_memory_usage = Gauge(
    'xnai_vulkan_memory_mb',
    'Vulkan memory usage in MB',
    ['memory_type', 'gpu_model']
)

vulkan_compute_utilization = Gauge(
    'xnai_vulkan_compute_utilization',
    'Vulkan compute unit utilization (0-1)',
    ['gpu_model']
)

vulkan_kernel_launch_overhead = Histogram(
    'xnai_vulkan_kernel_launch_us',
    'Vulkan kernel launch overhead in microseconds',
    ['operation_type']
)

cpu_utilization_percent = Gauge(
    'xnai_cpu_utilization_percent',
    'CPU utilization percentage',
    ['core_count', 'operation_type']
)

cpu_memory_bandwidth_gb_s = Gauge(
    'xnai_cpu_memory_bandwidth_gb_s',
    'CPU memory bandwidth in GB/s',
    ['memory_operation']
)

end_to_end_latency_ms = Histogram(
    'xnai_end_to_end_latency_ms',
    'Complete request processing time',
    ['hardware_config', 'model_size', 'query_complexity', 'precision'],
    buckets=[50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 60000]
)

throughput_tokens_per_sec = Gauge(
    'xnai_throughput_tokens_per_sec',
    'Token generation throughput',
    ['hardware_config', 'model_size', 'precision', 'batch_size']
)

energy_efficiency_tokens_per_watt = Gauge(
    'xnai_energy_efficiency_tokens_per_watt',
    'Energy efficiency metric',
    ['hardware_config', 'workload_type', 'power_source']
)

hardware_fallback_events = Counter(
    'xnai_hardware_fallback_events_total',
    'Hardware fallback events',
    ['from_hardware', 'to_hardware', 'reason', 'component']
)

# Persona Tuning Metrics
persona_accuracy = Gauge(
    'xnai_persona_accuracy',
    'Persona-tuned model accuracy scores',
    ['persona_name', 'domain', 'query_type', 'time_window']
)

persona_response_quality = Histogram(
    'xnai_persona_response_quality',
    'Persona response quality distribution',
    ['persona_name', 'domain', 'user_satisfaction'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

persona_context_retention = Gauge(
    'xnai_persona_context_retention',
    'How well persona maintains conversation context',
    ['persona_name', 'conversation_length', 'context_type']
)

persona_adaptation_events = Counter(
    'xnai_persona_adaptation_events_total',
    'Persona adaptation and tuning events',
    ['persona_name', 'adaptation_type', 'trigger_reason']
)

persona_inference_latency = Histogram(
    'xnai_persona_inference_latency_ms',
    'Persona-specific inference latency',
    ['persona_name', 'query_complexity', 'hardware_config'],
    buckets=[25, 50, 100, 250, 500, 1000, 2500, 5000]
)

# Knowledge Base Performance Metrics
domain_expertise_accuracy = Gauge(
    'xnai_domain_expertise_accuracy',
    'Accuracy within specific knowledge domains over time',
    ['domain', 'expertise_level', 'time_window', 'query_complexity']
)

knowledge_freshness_days = Gauge(
    'xnai_knowledge_freshness_days',
    'How current the knowledge base is in days',
    ['domain', 'update_frequency', 'content_type']
)

retrieval_precision = Histogram(
    'xnai_retrieval_precision',
    'Precision of knowledge retrieval operations',
    ['domain', 'query_type', 'result_count', 'retrieval_method'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

knowledge_base_updates = Counter(
    'xnai_knowledge_base_updates_total',
    'Knowledge base update and refresh events',
    ['domain', 'update_type', 'content_volume', 'trigger_source']
)

domain_performance_trend = Gauge(
    'xnai_domain_performance_trend',
    'Performance trend for knowledge domains (-1 to 1)',
    ['domain', 'metric_type', 'time_period']
)

# Enhanced AWQ Metrics (complementing existing quantization metrics)
awq_hardware_efficiency = Gauge(
    'xnai_awq_hardware_efficiency',
    'AWQ quantization efficiency by hardware',
    ['hardware_type', 'model_size', 'quantization_level']
)

awq_adaptive_precision_switches = Counter(
    'xnai_awq_precision_switches_total',
    'Dynamic precision switching events',
    ['from_precision', 'to_precision', 'reason', 'query_complexity']
)

# Comprehensive Logging Integration Metrics
structured_log_events = Counter(
    'xnai_structured_log_events_total',
    'Structured logging events by level and component',
    ['level', 'component', 'event_type', 'severity']
)

log_aggregation_latency = Histogram(
    'xnai_log_aggregation_latency_ms',
    'Log aggregation and processing latency',
    ['log_source', 'aggregation_type'],
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)

error_context_completeness = Gauge(
    'xnai_error_context_completeness',
    'How complete error context information is (0-1)',
    ['error_type', 'component', 'has_stack_trace', 'has_request_context']
)

# System Health & Benchmarking Metrics
benchmark_run_status = Gauge(
    'xnai_benchmark_run_status',
    'Current benchmark run status (0=idle, 1=running, 2=completed, 3=failed)',
    ['benchmark_type', 'hardware_config']
)

benchmark_comparison_score = Gauge(
    'xnai_benchmark_comparison_score',
    'Relative performance comparison scores',
    ['baseline_config', 'test_config', 'metric_type', 'improvement_percentage']
)

system_resource_efficiency = Gauge(
    'xnai_system_resource_efficiency',
    'Overall system resource utilization efficiency (0-1)',
    ['resource_type', 'workload_type', 'optimization_level']
)

# Info (metadata)
stack_info = Info(
    'xnai_stack',
    'Stack version and metadata'
)

# ============================================================================
# METRICS TIMER (Context Manager)
# ============================================================================

class MetricsTimer:
    """
    Context manager for timing operations and recording to histogram.
    
    Guide Reference: Section 5.2 (Metrics Timer)
    
    Example:
        >>> with MetricsTimer(response_latency_ms, endpoint='/query', method='POST'):
        ...     # Process query
        ...     pass
        # Automatically records duration to histogram
    """
    
    def __init__(
        self,
        histogram: Histogram,
        **labels
    ):
        """
        Initialize timer.
        
        Args:
            histogram: Histogram to record to
            **labels: Label values for histogram
        """
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and record duration."""
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.histogram.labels(**self.labels).observe(duration_ms)

# ============================================================================
# METRICS UPDATE FUNCTIONS
# ============================================================================

def update_memory_metrics():
    """
    Update memory usage metrics.
    
    Guide Reference: Section 5.2 (Memory Metrics)
    
    This records:
    - System memory usage
    - Process memory usage
    - Component-specific memory (if available)
    """
    try:
        # System memory
        memory = psutil.virtual_memory()
        system_used_bytes = memory.used
        memory_usage_bytes.labels(component='system').set(system_used_bytes)
        # Keep legacy GB metric for backward compatibility
        system_used_gb = system_used_bytes / (1024 ** 3)
        memory_usage_gb.labels(component='system').set(system_used_gb)
        
        # Process memory
        process = psutil.Process()
        process_used_bytes = process.memory_info().rss  # Already in bytes
        memory_usage_bytes.labels(component='process').set(process_used_bytes)
        # Keep legacy GB metric for backward compatibility
        process_used_gb = process_used_bytes / (1024 ** 3)
        memory_usage_gb.labels(component='process').set(process_used_gb)
        
        # Log warning if approaching limit
        memory_limit = CONFIG['performance']['memory_limit_gb']
        warning_threshold = CONFIG['performance']['memory_warning_threshold_gb']
        
        if system_used_gb > warning_threshold:
            logger.warning(
                f"Memory usage high: {system_used_gb:.2f}GB / {memory_limit:.1f}GB"
            )
        
    except Exception as e:
        logger.error(f"Failed to update memory metrics: {e}")
        errors_total.labels(error_type='metrics', component='memory').inc()

def update_cpu_metrics():
    """
    Update CPU-related metrics.
    
    Guide Reference: Section 5.2 (CPU Metrics)
    
    This could record CPU usage, but we focus on token rate instead.
    """
    # CPU metrics are less critical for this stack
    # Token rate is the key performance indicator
    pass

def update_stack_info():
    """
    Update stack metadata.
    
    Guide Reference: Section 5.2 (Stack Info)
    
    This sets static information about the stack version and config.
    """
    try:
        stack_info.info({
            'version': CONFIG['metadata']['stack_version'],
            'codename': CONFIG['metadata']['codename'],
            'phase': str(CONFIG['project']['phase']),
            'architecture': CONFIG['metadata']['architecture'],
            'cpu_threads': str(CONFIG['performance']['cpu_threads']),
            'memory_limit_gb': str(CONFIG['performance']['memory_limit_gb']),
            'f16_kv_enabled': str(CONFIG['performance']['f16_kv_enabled']),
        })
    except Exception as e:
        logger.error(f"Failed to update stack info: {e}")

# ============================================================================
# BACKGROUND METRICS UPDATER
# ============================================================================

class MetricsUpdater:
    """
    Background thread for updating gauges periodically.
    
    Guide Reference: Section 5.2 (Background Updates)
    
    This runs in a daemon thread and updates metrics every 30 seconds.
    """
    
    def __init__(self, interval_s: int = 30):
        """
        Initialize updater.
        
        Args:
            interval_s: Update interval in seconds
        """
        self.interval_s = interval_s
        self.running = False
        self.thread = None
    
    def start(self):
        """Start background updater thread."""
        if self.running:
            logger.warning("Metrics updater already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"Metrics updater started (interval: {self.interval_s}s)")
    
    def stop(self):
        """Stop background updater thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Metrics updater stopped")
    
    def _update_loop(self):
        """
        Background update loop.
        
        This runs continuously, updating metrics every interval_s seconds.
        """
        # Initial update
        self._update_all()
        
        # Periodic updates
        while self.running:
            try:
                time.sleep(self.interval_s)
                if self.running:
                    self._update_all()
            except Exception as e:
                logger.error(f"Metrics update loop error: {e}")
                errors_total.labels(error_type='metrics', component='updater').inc()
    
    def _update_all(self):
        """Update all gauge metrics."""
        try:
            update_memory_metrics()
            update_cpu_metrics()
            # Stack info only needs to be set once, but safe to call multiple times
            update_stack_info()
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

# Global updater instance
_metrics_updater = None

# ============================================================================
# METRICS SERVER
# ============================================================================

def start_metrics_server(port: int | None = None):
    """
    Start Prometheus metrics HTTP server.
    
    Guide Reference: Section 5.2 (Metrics Server)
    
    This starts an HTTP server on the specified port (default: 8002)
    and begins background metrics updates.
    
    Args:
        port: HTTP port (default: from config)
        
    Example:
        >>> start_metrics_server(port=8002)
        >>> # Metrics available at http://localhost:8002/metrics
    """
    global _metrics_updater
    
    # Get port from config if not specified and validate
    port_number = get_config_value('metrics.port', 8002) if port is None else port
    if not isinstance(port_number, int):
        raise ValueError(f"Port must be an integer, got {type(port_number)}")
    
    # Check if metrics enabled
    if not get_config_value('metrics.enabled', True):
        logger.info("Metrics disabled in configuration")
        return
    
    # Start HTTP server
    try:
        start_http_server(port_number)
        logger.info(f"Prometheus metrics server started on port {port_number}")
    except OSError as e:
        if "Address already in use" in str(e):
            logger.warning(f"Metrics server already running on port {port}")
        else:
            logger.error(f"Failed to start metrics server: {e}")
            raise
    
    # Start background updater
    if _metrics_updater is None:
        interval_s = get_config_value('metrics.update_interval_s', 30)
        _metrics_updater = MetricsUpdater(interval_s=interval_s)
        _metrics_updater.start()

def stop_metrics_server():
    """
    Stop metrics server and background updater.
    
    Guide Reference: Section 5.2 (Metrics Shutdown)
    """
    global _metrics_updater
    
    if _metrics_updater:
        _metrics_updater.stop()
        _metrics_updater = None

# ============================================================================
# CONVENIENCE FUNCTIONS FOR APPLICATION CODE
# ============================================================================

def record_request(
    endpoint: str,
    method: str,
    status: int
):
    """
    Record an API request.
    
    Guide Reference: Section 5.2 (Request Recording)
    
    Args:
        endpoint: Endpoint path (e.g., '/query')
        method: HTTP method (e.g., 'POST')
        status: HTTP status code (e.g., 200)
        
    Example:
        >>> record_request('/query', 'POST', 200)
    """
    requests_total.labels(
        endpoint=endpoint,
        method=method,
        status=str(status)
    ).inc()

def record_error(
    error_type: str,
    component: str
):
    """
    Record an error.
    
    Args:
        error_type: Type of error (e.g., 'timeout', 'validation', 'llm')
        component: Component where error occurred (e.g., 'api', 'rag', 'llm')
        
    Example:
        >>> record_error('timeout', 'llm')
    """
    errors_total.labels(
        error_type=error_type,
        component=component
    ).inc()

def record_tokens_generated(
    tokens: int,
    model: str = 'gemma-3-4b'
):
    """
    Record tokens generated.
    
    Args:
        tokens: Number of tokens generated
        model: Model name
        
    Example:
        >>> record_tokens_generated(50, model='gemma-3-4b')
    """
    tokens_generated_total.labels(model=model).inc(tokens)

def record_query_processed(rag_enabled: bool):
    """
    Record a processed query.
    
    Args:
        rag_enabled: Whether RAG was used
        
    Example:
        >>> record_query_processed(rag_enabled=True)
    """
    queries_processed_total.labels(
        rag_enabled=str(rag_enabled).lower()
    ).inc()

def update_token_rate(
    tokens_per_second: float,
    model: str = 'gemma-3-4b'
):
    """
    Update token generation rate gauge.
    
    Args:
        tokens_per_second: Current token rate
        model: Model name
        
    Example:
        >>> update_token_rate(20.5)
    """
    token_rate_tps.labels(model=model).set(tokens_per_second)

def update_active_sessions(count: int):
    """
    Update active sessions count.
    
    Args:
        count: Number of active sessions
        
    Example:
        >>> update_active_sessions(5)
    """
    active_sessions.set(count)

def record_rag_retrieval(duration_ms: float):
    """
    Record RAG document retrieval time.

    Args:
        duration_ms: Retrieval time in milliseconds

    Example:
        >>> record_rag_retrieval(45.2)
    """
    rag_retrieval_time_ms.observe(duration_ms)

# ============================================================================
# ENHANCED METRICS CONVENIENCE FUNCTIONS
# ============================================================================

# Hardware Benchmarking Functions
def record_hardware_performance(
    hardware_type: str,
    model_size: str,
    operation_type: str,
    performance_value: float
):
    """Record hardware-specific performance metrics."""
    hardware_performance.labels(
        hardware_type=hardware_type,
        model_size=model_size,
        operation_type=operation_type
    ).set(performance_value)

def update_vulkan_memory_usage(memory_type: str, gpu_model: str, usage_mb: float):
    """Update Vulkan memory usage metrics."""
    vulkan_memory_usage.labels(
        memory_type=memory_type,
        gpu_model=gpu_model
    ).set(usage_mb)

def update_vulkan_compute_utilization(gpu_model: str, utilization: float):
    """Update Vulkan compute utilization (0-1)."""
    vulkan_compute_utilization.labels(gpu_model=gpu_model).set(utilization)

def record_vulkan_kernel_overhead(operation_type: str, overhead_us: float):
    """Record Vulkan kernel launch overhead."""
    vulkan_kernel_launch_overhead.labels(operation_type=operation_type).observe(overhead_us)

def update_cpu_utilization(core_count: int, operation_type: str, utilization_percent: float):
    """Update CPU utilization metrics."""
    cpu_utilization_percent.labels(
        core_count=str(core_count),
        operation_type=operation_type
    ).set(utilization_percent)

def update_cpu_memory_bandwidth(memory_operation: str, bandwidth_gb_s: float):
    """Update CPU memory bandwidth metrics."""
    cpu_memory_bandwidth_gb_s.labels(memory_operation=memory_operation).set(bandwidth_gb_s)

def record_end_to_end_latency(
    hardware_config: str,
    model_size: str,
    query_complexity: str,
    precision: str,
    latency_ms: float
):
    """Record complete request processing time."""
    end_to_end_latency_ms.labels(
        hardware_config=hardware_config,
        model_size=model_size,
        query_complexity=query_complexity,
        precision=precision
    ).observe(latency_ms)

def update_throughput_tokens_per_sec(
    hardware_config: str,
    model_size: str,
    precision: str,
    batch_size: int,
    tokens_per_sec: float
):
    """Update token generation throughput."""
    throughput_tokens_per_sec.labels(
        hardware_config=hardware_config,
        model_size=model_size,
        precision=precision,
        batch_size=str(batch_size)
    ).set(tokens_per_sec)

def update_energy_efficiency(
    hardware_config: str,
    workload_type: str,
    power_source: str,
    tokens_per_watt: float
):
    """Update energy efficiency metrics."""
    energy_efficiency_tokens_per_watt.labels(
        hardware_config=hardware_config,
        workload_type=workload_type,
        power_source=power_source
    ).set(tokens_per_watt)

def record_hardware_fallback(from_hardware: str, to_hardware: str, reason: str, component: str):
    """Record hardware fallback events."""
    hardware_fallback_events.labels(
        from_hardware=from_hardware,
        to_hardware=to_hardware,
        reason=reason,
        component=component
    ).inc()

# Persona Tuning Functions
def update_persona_accuracy(
    persona_name: str,
    domain: str,
    query_type: str,
    time_window: str,
    accuracy: float
):
    """Update persona accuracy metrics."""
    persona_accuracy.labels(
        persona_name=persona_name,
        domain=domain,
        query_type=query_type,
        time_window=time_window
    ).set(accuracy)

def record_persona_response_quality(
    persona_name: str,
    domain: str,
    user_satisfaction: float
):
    """Record persona response quality distribution."""
    persona_response_quality.labels(
        persona_name=persona_name,
        domain=domain,
        user_satisfaction=str(user_satisfaction)
    ).observe(user_satisfaction)

def update_persona_context_retention(
    persona_name: str,
    conversation_length: int,
    context_type: str,
    retention_score: float
):
    """Update persona context retention metrics."""
    persona_context_retention.labels(
        persona_name=persona_name,
        conversation_length=str(conversation_length),
        context_type=context_type
    ).set(retention_score)

def record_persona_adaptation_event(
    persona_name: str,
    adaptation_type: str,
    trigger_reason: str
):
    """Record persona adaptation events."""
    persona_adaptation_events.labels(
        persona_name=persona_name,
        adaptation_type=adaptation_type,
        trigger_reason=trigger_reason
    ).inc()

def record_persona_inference_latency(
    persona_name: str,
    query_complexity: str,
    hardware_config: str,
    latency_ms: float
):
    """Record persona-specific inference latency."""
    persona_inference_latency.labels(
        persona_name=persona_name,
        query_complexity=query_complexity,
        hardware_config=hardware_config
    ).observe(latency_ms)

# Knowledge Base Performance Functions
def update_domain_expertise_accuracy(
    domain: str,
    expertise_level: str,
    time_window: str,
    query_complexity: str,
    accuracy: float
):
    """Update domain expertise accuracy over time."""
    domain_expertise_accuracy.labels(
        domain=domain,
        expertise_level=expertise_level,
        time_window=time_window,
        query_complexity=query_complexity
    ).set(accuracy)

def update_knowledge_freshness(
    domain: str,
    update_frequency: str,
    content_type: str,
    freshness_days: float
):
    """Update knowledge base freshness metrics."""
    knowledge_freshness_days.labels(
        domain=domain,
        update_frequency=update_frequency,
        content_type=content_type
    ).set(freshness_days)

def record_retrieval_precision(
    domain: str,
    query_type: str,
    result_count: int,
    retrieval_method: str,
    precision: float
):
    """Record knowledge retrieval precision."""
    retrieval_precision.labels(
        domain=domain,
        query_type=query_type,
        result_count=str(result_count),
        retrieval_method=retrieval_method
    ).observe(precision)

def record_knowledge_base_update(
    domain: str,
    update_type: str,
    content_volume: int,
    trigger_source: str
):
    """Record knowledge base update events."""
    knowledge_base_updates.labels(
        domain=domain,
        update_type=update_type,
        content_volume=str(content_volume),
        trigger_source=trigger_source
    ).inc()

def update_domain_performance_trend(
    domain: str,
    metric_type: str,
    time_period: str,
    trend_score: float  # -1 to 1 scale
):
    """Update domain performance trend metrics."""
    domain_performance_trend.labels(
        domain=domain,
        metric_type=metric_type,
        time_period=time_period
    ).set(trend_score)

# Enhanced AWQ Functions
def update_awq_hardware_efficiency(
    hardware_type: str,
    model_size: str,
    quantization_level: str,
    efficiency: float
):
    """Update AWQ quantization efficiency by hardware."""
    awq_hardware_efficiency.labels(
        hardware_type=hardware_type,
        model_size=model_size,
        quantization_level=quantization_level
    ).set(efficiency)

def record_awq_precision_switch(
    from_precision: str,
    to_precision: str,
    reason: str,
    query_complexity: str
):
    """Record AWQ dynamic precision switching events."""
    awq_adaptive_precision_switches.labels(
        from_precision=from_precision,
        to_precision=to_precision,
        reason=reason,
        query_complexity=query_complexity
    ).inc()

# Logging Integration Functions
def record_structured_log_event(
    level: str,
    component: str,
    event_type: str,
    severity: str
):
    """Record structured logging events."""
    structured_log_events.labels(
        level=level,
        component=component,
        event_type=event_type,
        severity=severity
    ).inc()

def record_log_aggregation_latency(
    log_source: str,
    aggregation_type: str,
    latency_ms: float
):
    """Record log aggregation and processing latency."""
    log_aggregation_latency.labels(
        log_source=log_source,
        aggregation_type=aggregation_type
    ).observe(latency_ms)

def update_error_context_completeness(
    error_type: str,
    component: str,
    has_stack_trace: bool,
    has_request_context: bool,
    completeness: float
):
    """Update error context completeness metrics."""
    error_context_completeness.labels(
        error_type=error_type,
        component=component,
        has_stack_trace=str(has_stack_trace).lower(),
        has_request_context=str(has_request_context).lower()
    ).set(completeness)

# Benchmarking Functions
def update_benchmark_run_status(
    benchmark_type: str,
    hardware_config: str,
    status: int  # 0=idle, 1=running, 2=completed, 3=failed
):
    """Update benchmark run status."""
    benchmark_run_status.labels(
        benchmark_type=benchmark_type,
        hardware_config=hardware_config
    ).set(status)

def update_benchmark_comparison_score(
    baseline_config: str,
    test_config: str,
    metric_type: str,
    improvement_percentage: float
):
    """Update benchmark comparison scores."""
    benchmark_comparison_score.labels(
        baseline_config=baseline_config,
        test_config=test_config,
        metric_type=metric_type,
        improvement_percentage=str(improvement_percentage)
    ).set(improvement_percentage)

def update_system_resource_efficiency(
    resource_type: str,
    workload_type: str,
    optimization_level: str,
    efficiency: float
):
    """Update overall system resource efficiency."""
    system_resource_efficiency.labels(
        resource_type=resource_type,
        workload_type=workload_type,
        optimization_level=optimization_level
    ).set(efficiency)

# ============================================================================
# PERFORMANCE VALIDATION
# ============================================================================

def check_performance_targets() -> Dict[str, Any]:
    """
    Check if current metrics meet performance targets.
    
    Guide Reference: Section 5.2 (Performance Validation)
    
    Returns:
        Dict with validation results
        
    Example:
        >>> results = check_performance_targets()
        >>> print(results['memory']['status'])
        'OK'
    """
    results = {}
    
    # Memory check
    try:
        memory = psutil.virtual_memory()
        memory_gb = memory.used / (1024 ** 3)
        memory_limit = CONFIG['performance']['memory_limit_gb']
        
        results['memory'] = {
            'current_gb': round(memory_gb, 2),
            'limit_gb': memory_limit,
            'status': 'OK' if memory_gb < memory_limit else 'EXCEEDED',
        }
    except Exception as e:
        results['memory'] = {'status': 'ERROR', 'error': str(e)}
    
    # Token rate check (would need to track recent generations)
    # This is more complex - typically done via monitoring dashboard
    results['token_rate'] = {
        'target_min': CONFIG['performance']['token_rate_min'],
        'target_max': CONFIG['performance']['token_rate_max'],
        'status': 'UNKNOWN',  # Would need tracking
    }
    
    return results

# ============================================================================
# MULTIPROCESS MODE (for Gunicorn/Uvicorn workers)
# ============================================================================

def setup_multiprocess_metrics(multiproc_dir: str | None = None):
    """
    Setup metrics for multiprocess mode.
    
    Guide Reference: Section 5.2 (Multiprocess Metrics)
    
    This is needed when running with multiple Uvicorn workers.
    
    Args:
        multiproc_dir: Directory for shared metrics (default: from config)
        
    Example:
        >>> setup_multiprocess_metrics('/prometheus_data')
        
    Raises:
        ValueError: If multiproc_dir is None after config lookup
    """
    # Get directory from config if not specified and validate
    dir_path = multiproc_dir if multiproc_dir is not None else get_config_value('metrics.multiproc_dir', '/prometheus_data')
    
    if dir_path is None:
        raise ValueError("Multiprocess directory path cannot be None")
        
    if not isinstance(dir_path, str):
        raise ValueError(f"Multiprocess directory path must be a string, got {type(dir_path)}")
    
    # Ensure directory exists
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Set environment variable
    os.environ['prometheus_multiproc_dir'] = dir_path
    
    logger.info(f"Multiprocess metrics enabled: {dir_path}")

# ============================================================================
# METRICS COLLECTOR (Unified Interface)
# ============================================================================

class MetricsCollector:
    """
    Unified metrics collector providing a simplified interface for 
    creating and updating Prometheus metrics.
    """
    def __init__(self):
        self._metrics = {}
        self._lock = threading.Lock()

    def create_gauge(self, name: str, documentation: str, labelnames: List[str] = ()):
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Gauge(name, documentation, labelnames)
            return self._metrics[name]

    def create_counter(self, name: str, documentation: str, labelnames: List[str] = ()):
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Counter(name, documentation, labelnames)
            return self._metrics[name]

    def create_histogram(self, name: str, documentation: str, labelnames: List[str] = (), buckets=Histogram.DEFAULT_BUCKETS):
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Histogram(name, documentation, labelnames, buckets=buckets)
            return self._metrics[name]

    def set_gauge(self, name: str, value: float, **labels):
        if name in self._metrics:
            if labels:
                self._metrics[name].labels(**labels).set(value)
            else:
                self._metrics[name].set(value)

    def increment_counter(self, name: str, amount: float = 1, **labels):
        if name in self._metrics:
            if labels:
                self._metrics[name].labels(**labels).inc(amount)
            else:
                self._metrics[name].inc(amount)

    def observe_histogram(self, name: str, value: float, **labels):
        if name in self._metrics:
            if labels:
                self._metrics[name].labels(**labels).observe(value)
            else:
                self._metrics[name].observe(value)

# Global metrics collector instance
metrics_collector = MetricsCollector()

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test metrics module.
    
    Usage: python3 metrics.py
    
    This validates the metrics module and generates test data.
    """
    import sys
    
    print("=" * 70)
    print("Xoe-NovAi Metrics Module - Test Suite")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Start metrics server
    print("Test 1: Start metrics server")
    try:
        start_metrics_server(port=8002)
        print("✓ Metrics server started on port 8002")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Failed to start metrics server: {e}")
        tests_failed += 1
    
    print()
    
    # Test 2: Record sample metrics
    print("Test 2: Record sample metrics")
    try:
        # Record requests
        record_request('/query', 'POST', 200)
        record_request('/query', 'POST', 200)
        record_request('/health', 'GET', 200)
        
        # Record tokens
        record_tokens_generated(100, model='gemma-3-4b')
        record_tokens_generated(50, model='gemma-3-4b')
        
        # Update gauges
        update_token_rate(20.5)
        update_active_sessions(3)
        
        # Record query
        record_query_processed(rag_enabled=True)
        
        # Record RAG retrieval
        record_rag_retrieval(45.2)
        
        print("✓ Sample metrics recorded")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Failed to record metrics: {e}")
        tests_failed += 1
    
    print()
    
    # Test 3: Test timer context manager
    print("Test 3: Test timer context manager")
    try:
        with MetricsTimer(response_latency_ms, endpoint='/test', method='GET'):
            time.sleep(0.1)  # Simulate 100ms operation
        
        print("✓ Timer context manager works")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Timer test failed: {e}")
        tests_failed += 1
    
    print()
    
    # Test 4: Update memory metrics
    print("Test 4: Update memory metrics")
    try:
        update_memory_metrics()
        print("✓ Memory metrics updated")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Memory metrics failed: {e}")
        tests_failed += 1
    
    print()
    
    # Test 5: Check performance targets
    print("Test 5: Check performance targets")
    try:
        results = check_performance_targets()
        print(f"✓ Performance check: {results['memory']['status']}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Performance check failed: {e}")
        tests_failed += 1
    
    print()
    
    # Test 6: Generate metrics output
    print("Test 6: Generate metrics output")
    try:
        from prometheus_client import generate_latest
        metrics_output = generate_latest().decode('utf-8')
        
        # Check for expected metrics
        expected_metrics = [
            'xnai_memory_usage_gb',
            'xnai_token_rate_tps',
            'xnai_requests_total',
            'xnai_tokens_generated_total',
        ]
        
        found = [m for m in expected_metrics if m in metrics_output]
        
        print(f"✓ Found {len(found)}/{len(expected_metrics)} expected metrics")
        print(f"  Sample output (first 500 chars):")
        print(f"  {metrics_output[:500]}")
        
        if len(found) == len(expected_metrics):
            tests_passed += 1
        else:
            print(f"  Missing: {set(expected_metrics) - set(found)}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ Metrics output test failed: {e}")
        tests_failed += 1
    
    print()
    
    # Wait a bit for background updater
    print("Waiting 2s for background updater...")
    time.sleep(2)
    
    # Final summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print()
    
    if tests_failed == 0:
        print("✓ All tests passed!")
        print()
        print("Metrics server is running at http://localhost:8002/metrics")
        print("Press Ctrl+C to stop...")
        print()
        
        # Keep server running for manual testing
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping metrics server...")
            stop_metrics_server()
        
        sys.exit(0)
    else:
        print(f"✗ {tests_failed} test(s) failed")
        stop_metrics_server()
        sys.exit(1)
