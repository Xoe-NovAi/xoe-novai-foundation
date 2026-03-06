# XNAi Foundation: Monitoring and Observability for Modular Services

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Comprehensive monitoring and observability strategy for modular architecture

## Overview

This document outlines the monitoring and observability strategy for the XNAi Foundation modular services. Building upon the existing sophisticated infrastructure with VictoriaMetrics, Grafana, and comprehensive service mesh monitoring, this strategy extends observability to support the modular architecture while maintaining consistency with existing patterns.

## Current Monitoring Infrastructure Analysis

### Existing Monitoring Stack

#### 1. Metrics Collection (VictoriaMetrics)
- **24 services** with comprehensive metrics collection
- **Prometheus-compatible** metrics endpoint on all services
- **Custom metrics** for business logic and performance monitoring
- **Multi-tenant support** with service isolation
- **Long-term storage** with configurable retention policies

#### 2. Visualization and Dashboards (Grafana)
- **Service-specific dashboards** for each component
- **Infrastructure monitoring** for all 24 services
- **Business metrics** and SLA tracking
- **Alerting dashboards** with real-time notifications
- **Multi-environment support** (dev, staging, production)

#### 3. Service Mesh Monitoring (Consul + Caddy)
- **Service discovery** with health checks
- **Load balancer metrics** and performance monitoring
- **SSL certificate monitoring** and expiration alerts
- **Traffic distribution** and routing metrics
- **Circuit breaker** and fault tolerance monitoring

#### 4. Log Aggregation and Analysis
- **Centralized logging** across all 24 services
- **Structured logging** with consistent format
- **Log correlation** with distributed tracing
- **Real-time log streaming** and alerting
- **Log retention** and archival policies

### Current Monitoring Capabilities

#### Service Health Monitoring
```yaml
# Current service health checks
health_checks:
  consul:
    interval: "30s"
    timeout: "10s"
    retries: 3
    deregister_critical_after: "1m"
  
  caddy:
    health_uri: "/health"
    health_interval: "30s"
    health_timeout: "10s"
    health_status: 200
  
  postgres:
    check_command: "pg_isready"
    interval: "30s"
    timeout: "10s"
  
  redis:
    check_command: "redis-cli ping"
    interval: "30s"
    timeout: "10s"
```

#### Metrics Collection
```yaml
# Current metrics configuration
metrics_collection:
  prometheus:
    scrape_interval: "15s"
    evaluation_interval: "15s"
    retention: "30d"
  
  custom_metrics:
    business_metrics: true
    performance_metrics: true
    error_rates: true
    response_times: true
  
  service_metrics:
    cpu_usage: true
    memory_usage: true
    network_io: true
    disk_io: true
```

## Modular Services Monitoring Strategy

### 1. Service-Level Monitoring

#### 1.1 Health Check Implementation

```python
# Comprehensive health check implementation for modular services
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import asyncio
import time
import psutil
from datetime import datetime

router = APIRouter()

class HealthChecker:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time = time.time()
        self.dependencies = []
    
    def add_dependency(self, name: str, check_func, timeout: int = 10):
        self.dependencies.append({
            'name': name,
            'check_func': check_func,
            'timeout': timeout
        })
    
    async def check_dependency(self, dep: Dict) -> Dict[str, Any]:
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                dep['check_func'](), 
                timeout=dep['timeout']
            )
            return {
                'name': dep['name'],
                'status': 'healthy',
                'response_time': time.time() - start_time,
                'details': result
            }
        except asyncio.TimeoutError:
            return {
                'name': dep['name'],
                'status': 'unhealthy',
                'response_time': dep['timeout'],
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'name': dep['name'],
                'status': 'unhealthy',
                'response_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        # Check service status
        service_status = {
            'service_name': self.service_name,
            'status': 'healthy',
            'uptime': time.time() - self.start_time,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }
        
        # Check dependencies
        dependency_results = await asyncio.gather(*[
            self.check_dependency(dep) for dep in self.dependencies
        ])
        
        # Determine overall status
        unhealthy_deps = [dep for dep in dependency_results if dep['status'] == 'unhealthy']
        if unhealthy_deps:
            service_status['status'] = 'unhealthy'
            service_status['unhealthy_dependencies'] = [dep['name'] for dep in unhealthy_deps]
        
        # Add system metrics
        service_status['system_metrics'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()
        }
        
        # Add dependency details
        service_status['dependencies'] = dependency_results
        
        return service_status

# Usage in services
health_checker = HealthChecker('rag-core')

# Add database dependency
async def check_database():
    # Database health check implementation
    return {'connection': 'ok', 'pool_size': 10}

health_checker.add_dependency('postgres', check_database, timeout=5)

# Add vector database dependency
async def check_vector_db():
    # Vector database health check implementation
    return {'connection': 'ok', 'collections': ['documents']}

health_checker.add_dependency('qdrant', check_vector_db, timeout=5)

# Add Redis dependency
async def check_redis():
    # Redis health check implementation
    return {'connection': 'ok', 'memory_usage': '100MB'}

health_checker.add_dependency('redis', check_redis, timeout=3)

@router.get("/health")
async def health_check():
    return await health_checker.get_health_status()

@router.get("/ready")
async def readiness_check():
    # Readiness check - more comprehensive than health check
    health_status = await health_checker.get_health_status()
    
    # Service is ready if all critical dependencies are healthy
    critical_deps = ['postgres', 'qdrant']  # Define critical dependencies
    critical_healthy = all(
        dep['status'] == 'healthy' 
        for dep in health_status['dependencies'] 
        if dep['name'] in critical_deps
    )
    
    if not critical_healthy:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    # Liveness check - basic service availability
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

#### 1.2 Metrics Collection Implementation

```python
# Prometheus metrics collection for modular services
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import start_http_server
import time
from typing import Dict, Any

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
CACHE_HIT_RATE = Gauge('cache_hit_rate', 'Cache hit rate', ['cache_type'])
ERROR_COUNT = Counter('errors_total', 'Total errors', ['error_type', 'service'])
BUSINESS_METRICS = Counter('business_operations_total', 'Business operations', ['operation_type', 'status'])

# Service-specific metrics
RAG_QUERY_COUNT = Counter('rag_queries_total', 'Total RAG queries', ['model_type', 'status'])
RAG_RESPONSE_TIME = Histogram('rag_response_time_seconds', 'RAG response time')
KNOWLEDGE_PROCESSING_TIME = Histogram('knowledge_processing_time_seconds', 'Knowledge processing time')
UI_INTERACTION_COUNT = Counter('ui_interactions_total', 'UI interactions', ['interaction_type'])

class MetricsCollector:
    @staticmethod
    def record_request(method: str, endpoint: str, status: str, duration: float):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.observe(duration)
    
    @staticmethod
    def record_cache_hit(cache_type: str):
        CACHE_HIT_RATE.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_active_connections(count: int):
        ACTIVE_CONNECTIONS.set(count)
    
    @staticmethod
    def record_error(error_type: str, service: str):
        ERROR_COUNT.labels(error_type=error_type, service=service).inc()
    
    @staticmethod
    def record_business_operation(operation_type: str, status: str):
        BUSINESS_METRICS.labels(operation_type=operation_type, status=status).inc()
    
    @staticmethod
    def record_rag_query(model_type: str, status: str, response_time: float):
        RAG_QUERY_COUNT.labels(model_type=model_type, status=status).inc()
        RAG_RESPONSE_TIME.observe(response_time)
    
    @staticmethod
    def record_knowledge_processing(processing_time: float):
        KNOWLEDGE_PROCESSING_TIME.observe(processing_time)
    
    @staticmethod
    def record_ui_interaction(interaction_type: str):
        UI_INTERACTION_COUNT.labels(interaction_type=interaction_type).inc()

# Middleware for automatic metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    MetricsCollector.record_request(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code),
        duration=duration
    )
    
    return response

# Start metrics server
start_http_server(8001)  # Expose metrics on port 8001
```

### 2. Distributed Tracing Implementation

#### 2.1 OpenTelemetry Integration

```python
# OpenTelemetry tracing for modular services
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
import os

def setup_tracing(service_name: str):
    # Configure tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(service_name)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv('JAEGER_HOST', 'jaeger'),
        agent_port=int(os.getenv('JAEGER_PORT', 6831)),
    )
    
    # Configure span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument frameworks
    FastAPIInstrumentor.instrument(app)
    RedisInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    AioHttpInstrumentor().instrument()
    AsyncPGInstrumentor().instrument()
    
    return tracer

# Setup tracing for each service
tracer = setup_tracing("rag-core")

# Use tracing in service functions
@tracer.start_as_current_span("process_query")
async def process_query(query: str):
    with tracer.start_as_current_span("validate_query") as span:
        span.set_attribute("query.length", len(query))
        span.set_attribute("query.type", "text")
        if not query.strip():
            span.set_attribute("query.valid", False)
            raise ValueError("Query cannot be empty")
        span.set_attribute("query.valid", True)
    
    with tracer.start_as_current_span("search_vectors") as span:
        span.set_attribute("search.type", "vector")
        span.set_attribute("search.model", "sentence-transformers")
        
        # Add custom attributes
        span.set_attribute("search.top_k", 10)
        span.set_attribute("search.filter", "active_documents")
        
        results = await vector_search(query)
        span.set_attribute("search.results_count", len(results))
        span.set_attribute("search.recall", 0.85)
    
    with tracer.start_as_current_span("generate_response") as span:
        span.set_attribute("generation.model", "gpt-4")
        span.set_attribute("generation.temperature", 0.7)
        
        response = await generate_response(query, results)
        span.set_attribute("response.length", len(response))
        span.set_attribute("response.tokens", estimate_tokens(response))
    
    return response

# Custom span creation for complex operations
def create_span(name: str, attributes: Dict[str, Any] = None):
    span = trace.get_current_span()
    if span:
        for key, value in (attributes or {}).items():
            span.set_attribute(key, value)
    return span

# Error tracking with spans
@tracer.start_as_current_span("handle_error")
async def handle_error(error: Exception, context: Dict[str, Any]):
    span = trace.get_current_span()
    span.set_attribute("error.type", type(error).__name__)
    span.set_attribute("error.message", str(error))
    span.set_attribute("error.context", str(context))
    span.record_exception(error)
    
    # Log error details
    logger.error(f"Error occurred: {error}", extra={"context": context})
```

#### 2.2 Cross-Service Tracing

```python
# Cross-service tracing with context propagation
import aiohttp
from opentelemetry.propagate import inject
from opentelemetry.trace import get_current_span

class ServiceClient:
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
    
    async def make_request(self, endpoint: str, method: str = "GET", **kwargs):
        url = f"{self.base_url}{endpoint}"
        
        # Create span for external request
        with tracer.start_as_current_span(f"{self.service_name}.{method.lower()}") as span:
            span.set_attribute("http.url", url)
            span.set_attribute("http.method", method)
            
            # Inject tracing context into headers
            headers = kwargs.get("headers", {})
            inject(headers)
            
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.request(method, url, headers=headers, **kwargs)
                    span.set_attribute("http.status_code", response.status)
                    
                    if response.status >= 400:
                        span.set_attribute("http.error", True)
                        span.record_exception(Exception(f"HTTP {response.status}"))
                    
                    return response
                except Exception as e:
                    span.record_exception(e)
                    raise

# Usage in services
rag_core_client = ServiceClient("http://rag-core:8000", "rag-core")
knowledge_mgmt_client = ServiceClient("http://knowledge-mgmt:8001", "knowledge-mgmt")

@router.post("/query")
async def query_endpoint(query: QueryRequest):
    with tracer.start_as_current_span("query_endpoint") as span:
        span.set_attribute("query.text", query.text)
        span.set_attribute("query.user_id", query.user_id)
        
        # Call knowledge management service
        async with knowledge_mgmt_client.make_request(
            "/process", 
            method="POST", 
            json={"text": query.text}
        ) as response:
            knowledge_data = await response.json()
            span.set_attribute("knowledge.processed", True)
        
        # Call RAG core service
        async with rag_core_client.make_request(
            "/search", 
            method="POST", 
            json={"query": query.text, "context": knowledge_data}
        ) as response:
            rag_result = await response.json()
            span.set_attribute("rag.result_count", len(rag_result.get("results", [])))
        
        return rag_result
```

### 3. Log Aggregation and Analysis

#### 3.1 Structured Logging Implementation

```python
# Structured logging for modular services
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sys

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': getattr(record, 'service', 'unknown'),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'logger': record.name,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                              'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process', 'getMessage']:
                    log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging(service_name: str, log_level: str = "INFO"):
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger

# Usage in services
logger = setup_logging('rag-core', os.getenv('LOG_LEVEL', 'INFO'))

# Log with structured data
logger.info("Query processed successfully", extra={
    'query_id': '12345',
    'user_id': 'user_001',
    'response_time': 1.2,
    'result_count': 10,
    'model_used': 'gpt-4'
})

logger.error("Database connection failed", extra={
    'database': 'postgres',
    'connection_string': 'postgresql://...',
    'error_code': 'CONNECTION_TIMEOUT'
})

# Context-aware logging
class ContextLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context = {}
    
    def set_context(self, **kwargs):
        self.context.update(kwargs)
    
    def clear_context(self):
        self.context.clear()
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        extra = {**self.context, **kwargs}
        getattr(self.logger, level)(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log_with_context('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log_with_context('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_context('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_context('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_context('critical', message, **kwargs)

# Usage
context_logger = ContextLogger(logger)

async def process_query(query_id: str, user_id: str, query_text: str):
    context_logger.set_context(
        query_id=query_id,
        user_id=user_id,
        service='rag-core'
    )
    
    try:
        context_logger.info("Processing query", extra={
            'query_text': query_text[:100]  # Truncate long queries
        })
        
        # Process query
        result = await process_query_logic(query_text)
        
        context_logger.info("Query processed successfully", extra={
            'result_count': len(result),
            'processing_time': 1.5
        })
        
        return result
        
    except Exception as e:
        context_logger.error("Query processing failed", extra={
            'error_type': type(e).__name__,
            'error_message': str(e)
        })
        raise
    finally:
        context_logger.clear_context()
```

#### 3.2 Log Correlation with Traces

```python
# Log correlation with distributed tracing
from opentelemetry import trace
from opentelemetry.trace import format_trace_id, format_span_id

class TracingLogFilter(logging.Filter):
    def filter(self, record):
        span = trace.get_current_span()
        if span:
            span_context = span.get_span_context()
            record.trace_id = format_trace_id(span_context.trace_id)
            record.span_id = format_span_id(span_context.span_id)
        return True

def setup_tracing_logging(service_name: str):
    logger = setup_logging(service_name)
    
    # Add tracing filter
    tracing_filter = TracingLogFilter()
    for handler in logger.handlers:
        handler.addFilter(tracing_filter)
    
    return logger

# Usage
logger = setup_tracing_logging('rag-core')

# Logs will now include trace_id and span_id for correlation
logger.info("Processing request", extra={
    'request_id': 'req_123',
    'user_id': 'user_001'
})
# Output: {"timestamp": "...", "level": "INFO", "service": "rag-core", 
#          "trace_id": "0x1234567890abcdef", "span_id": "0xabcdef1234567890", 
#          "message": "Processing request", "request_id": "req_123", "user_id": "user_001"}
```

### 4. Alerting and Incident Management

#### 4.1 Alert Rules Configuration

```yaml
# Prometheus alert rules for modular services
groups:
- name: service_health
  rules:
  - alert: ServiceDown
    expr: up{job=~"rag-core|knowledge-mgmt|ui-service"} == 0
    for: 1m
    labels:
      severity: critical
      team: platform
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "{{ $labels.job }} has been down for more than 1 minute"
      runbook_url: "https://docs.xnai.example.com/runbooks/service-down"
  
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High error rate on {{ $labels.job }}"
      description: "Error rate is {{ $value }} errors per second on {{ $labels.job }}"
      runbook_url: "https://docs.xnai.example.com/runbooks/high-error-rate"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High response time on {{ $labels.job }}"
      description: "95th percentile response time is {{ $value }} seconds on {{ $labels.job }}"
      runbook_url: "https://docs.xnai.example.com/runbooks/high-response-time"

- name: business_metrics
  rules:
  - alert: LowQueryVolume
    expr: rate(queries_total[1h]) < 10
    for: 15m
    labels:
      severity: warning
      team: product
    annotations:
      summary: "Low query volume detected"
      description: "Query volume is {{ $value }} queries per second, below expected threshold"
  
  - alert: HighCacheMissRate
    expr: (cache_misses_total / cache_requests_total) > 0.5
    for: 10m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High cache miss rate"
      description: "Cache miss rate is {{ $value | humanizePercentage }} on {{ $labels.service }}"
  
  - alert: KnowledgeProcessingFailure
    expr: rate(knowledge_processing_errors_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
      team: platform
    annotations:
      summary: "Knowledge processing failures detected"
      description: "Knowledge processing error rate is {{ $value }} errors per second"

- name: infrastructure
  rules:
  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.8
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"
  
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"
  
  - alert: DiskSpaceLow
    expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.9
    for: 5m
    labels:
      severity: critical
      team: platform
    annotations:
      summary: "Disk space low on {{ $labels.instance }}"
      description: "Disk usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"
```

#### 4.2 Alert Manager Configuration

```yaml
# AlertManager configuration for modular services
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@xnai.example.com'
  smtp_auth_username: 'alerts@xnai.example.com'
  smtp_auth_password: '${ALERT_SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    group_wait: 5s
    repeat_interval: 5m
  - match:
      severity: warning
    receiver: 'warning-alerts'
    group_wait: 30s
    repeat_interval: 30m

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://alertmanager-webhook:5000/webhook'
    send_resolved: true

- name: 'critical-alerts'
  email_configs:
  - to: 'oncall@xnai.example.com'
    subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
    body: |
      Alert: {{ .GroupLabels.alertname }}
      Severity: {{ .CommonLabels.severity }}
      Service: {{ .CommonLabels.service }}
      
      {{ range .Alerts }}
      - {{ .Annotations.summary }}
        {{ .Annotations.description }}
      {{ end }}
  
  slack_configs:
  - api_url: '${SLACK_WEBHOOK_URL}'
    channel: '#alerts-critical'
    title: 'Critical Alert: {{ .GroupLabels.alertname }}'
    text: |
      *Alert:* {{ .GroupLabels.alertname }}
      *Severity:* {{ .CommonLabels.severity }}
      *Service:* {{ .CommonLabels.service }}
      
      {{ range .Alerts }}
      - {{ .Annotations.summary }}
        {{ .Annotations.description }}
      {{ end }}
  
  pagerduty_configs:
  - routing_key: '${PAGERDUTY_INTEGRATION_KEY}'
    description: '{{ .GroupLabels.alertname }}: {{ .CommonLabels.service }}'

- name: 'warning-alerts'
  email_configs:
  - to: 'team@xnai.example.com'
    subject: '[WARNING] {{ .GroupLabels.alertname }}'
    body: |
      Alert: {{ .GroupLabels.alertname }}
      Severity: {{ .CommonLabels.severity }}
      Service: {{ .CommonLabels.service }}
      
      {{ range .Alerts }}
      - {{ .Annotations.summary }}
        {{ .Annotations.description }}
      {{ end }}

inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'cluster', 'service']
```

### 5. Dashboard Configuration

#### 5.1 Grafana Dashboard for Modular Services

```json
{
  "dashboard": {
    "id": null,
    "title": "XNAi Foundation - Modular Services",
    "tags": ["xnai", "modular", "services"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Health Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"rag-core|knowledge-mgmt|ui-service\"}",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}} - {{method}} {{status}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Response Time Percentiles",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{job}} - {{status}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 5,
        "title": "Business Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(queries_total[5m])",
            "legendFormat": "Query Rate"
          },
          {
            "expr": "rate(knowledge_processing_total[5m])",
            "legendFormat": "Knowledge Processing Rate"
          },
          {
            "expr": "rate(ui_interactions_total[5m])",
            "legendFormat": "UI Interaction Rate"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      },
      {
        "id": 6,
        "title": "Cache Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "cache_hit_rate",
            "legendFormat": "{{cache_type}} Hit Rate"
          },
          {
            "expr": "rate(cache_requests_total[5m])",
            "legendFormat": "{{cache_type}} Request Rate"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24}
      },
      {
        "id": 7,
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "cpu_usage_percent",
            "legendFormat": "{{instance}} CPU Usage"
          },
          {
            "expr": "memory_usage_percent",
            "legendFormat": "{{instance}} Memory Usage"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 24}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

#### 5.2 Service-Specific Dashboards

```json
{
  "dashboard": {
    "id": null,
    "title": "RAG Core Service",
    "tags": ["xnai", "rag", "core"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Query Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(queries_total[5m])",
            "legendFormat": "Query Rate"
          },
          {
            "expr": "histogram_quantile(0.95, rate(query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile response time"
          }
        ]
      },
      {
        "id": 2,
        "title": "Vector Search Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(vector_search_operations_total[5m])",
            "legendFormat": "Search Rate"
          },
          {
            "expr": "histogram_quantile(0.95, rate(vector_search_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile search time"
          }
        ]
      },
      {
        "id": 3,
        "title": "Model Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(model_inference_total[5m])",
            "legendFormat": "{{model_type}} Inference Rate"
          },
          {
            "expr": "histogram_quantile(0.95, rate(model_inference_duration_seconds_bucket[5m]))",
            "legendFormat": "{{model_type}} 95th percentile inference time"
          }
        ]
      },
      {
        "id": 4,
        "title": "Cache Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "cache_hit_rate{cache_type=\"vector\"}",
            "legendFormat": "Vector Cache Hit Rate"
          },
          {
            "expr": "cache_hit_rate{cache_type=\"query\"}",
            "legendFormat": "Query Cache Hit Rate"
          }
        ]
      }
    ]
  }
}
```

### 6. Performance Monitoring

#### 6.1 SLA Monitoring

```python
# SLA monitoring implementation
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

@dataclass
class SLAMetric:
    name: str
    target: float
    current_value: float
    time_window: timedelta
    measurement_count: int
    success_count: int

class SLAMonitor:
    def __init__(self):
        self.metrics: Dict[str, SLAMetric] = {}
        self.sla_targets = {
            'service_availability': 0.999,  # 99.9%
            'response_time_p95': 1.0,      # 1 second
            'error_rate': 0.01,            # 1%
            'query_success_rate': 0.95     # 95%
        }
    
    def record_measurement(self, metric_name: str, success: bool, value: Optional[float] = None):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = SLAMetric(
                name=metric_name,
                target=self.sla_targets.get(metric_name, 0.95),
                current_value=0.0,
                time_window=timedelta(hours=1),
                measurement_count=0,
                success_count=0
            )
        
        metric = self.metrics[metric_name]
        metric.measurement_count += 1
        if success:
            metric.success_count += 1
        
        if value is not None:
            # For metrics like response time, track the actual value
            metric.current_value = value
        
        # Calculate current SLA
        if metric.measurement_count > 0:
            metric.current_value = metric.success_count / metric.measurement_count
    
    def get_sla_status(self) -> Dict[str, Dict[str, float]]:
        status = {}
        for name, metric in self.metrics.items():
            status[name] = {
                'target': metric.target,
                'current': metric.current_value,
                'compliance': metric.current_value >= metric.target,
                'success_rate': metric.success_count / metric.measurement_count if metric.measurement_count > 0 else 0
            }
        return status
    
    def check_sla_violations(self) -> List[Dict[str, any]]:
        violations = []
        for name, metric in self.metrics.items():
            if metric.current_value < metric.target:
                violations.append({
                    'metric': name,
                    'target': metric.target,
                    'current': metric.current_value,
                    'violation': metric.target - metric.current_value,
                    'timestamp': datetime.utcnow().isoformat()
                })
        return violations

# Usage in services
sla_monitor = SLAMonitor()

@router.post("/query")
async def query_endpoint(query: QueryRequest):
    start_time = time.time()
    
    try:
        # Process query
        result = await process_query(query.text)
        
        # Record successful measurement
        response_time = time.time() - start_time
        sla_monitor.record_measurement('service_availability', True)
        sla_monitor.record_measurement('response_time_p95', response_time <= 1.0, response_time)
        sla_monitor.record_measurement('query_success_rate', True)
        
        return result
        
    except Exception as e:
        # Record failed measurement
        sla_monitor.record_measurement('service_availability', False)
        sla_monitor.record_measurement('query_success_rate', False)
        sla_monitor.record_measurement('error_rate', False)
        
        raise

# SLA monitoring endpoint
@router.get("/sla")
async def get_sla_status():
    return {
        'sla_status': sla_monitor.get_sla_status(),
        'violations': sla_monitor.check_sla_violations(),
        'timestamp': datetime.utcnow().isoformat()
    }
```

#### 6.2 Performance Profiling

```python
# Performance profiling for modular services
import cProfile
import pstats
import io
from contextlib import contextmanager
from typing import Dict, Any
import time

class PerformanceProfiler:
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}
    
    @contextmanager
    def profile(self, name: str):
        pr = cProfile.Profile()
        pr.enable()
        
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            pr.disable()
            
            # Store profile data
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats()
            
            self.profiles[name] = {
                'execution_time': end_time - start_time,
                'profile_data': s.getvalue(),
                'timestamp': time.time()
            }
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        return self.profiles.get(name)
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        return self.profiles
    
    def clear_profiles(self):
        self.profiles.clear()

# Usage in services
profiler = PerformanceProfiler()

@router.post("/heavy-operation")
async def heavy_operation_endpoint(data: HeavyOperationRequest):
    with profiler.profile("heavy_operation"):
        result = await perform_heavy_operation(data)
    
    return result

# Profile endpoint for debugging
@router.get("/profiles/{operation_name}")
async def get_profile(operation_name: str):
    profile = profiler.get_profile(operation_name)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        'operation': operation_name,
        'execution_time': profile['execution_time'],
        'profile_data': profile['profile_data'],
        'timestamp': profile['timestamp']
    }
```

### 7. Implementation Roadmap

#### Phase 1: Foundation (Weeks 1-2)
- [ ] Implement health check endpoints for all modular services
- [ ] Set up Prometheus metrics collection
- [ ] Configure basic Grafana dashboards
- [ ] Implement structured logging

#### Phase 2: Advanced Monitoring (Weeks 3-4)
- [ ] Set up distributed tracing with OpenTelemetry
- [ ] Configure alert rules and AlertManager
- [ ] Implement SLA monitoring
- [ ] Create service-specific dashboards

#### Phase 3: Performance Optimization (Weeks 5-6)
- [ ] Implement performance profiling
- [ ] Set up advanced alerting rules
- [ ] Configure log aggregation and analysis
- [ ] Implement cross-service tracing

#### Phase 4: Production Readiness (Weeks 7-8)
- [ ] Fine-tune monitoring thresholds
- [ ] Implement automated incident response
- [ ] Set up monitoring for edge deployments
- [ ] Validate monitoring across all environments

## Conclusion

This comprehensive monitoring and observability strategy extends the existing sophisticated infrastructure to support the modular architecture. By building upon the current 24-service monitoring ecosystem, the strategy ensures:

- **Consistency**: Using existing monitoring patterns and tools
- **Comprehensiveness**: Covering all aspects of service health and performance
- **Scalability**: Supporting growth from development to production
- **Reliability**: Enabling proactive issue detection and resolution
- **Insight**: Providing deep visibility into service behavior and performance

The strategy leverages the existing VictoriaMetrics, Grafana, and service mesh infrastructure while extending capabilities to support the modular service architecture effectively.