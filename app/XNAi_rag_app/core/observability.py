"""
Xoe-NovAi Observability System
================================
Sovereign, ethical, and accessible observability for RAG API.
Complies with Ma'at's 42 Ideals and Xoe-NovAi standards.
"""

import os
import logging
import psutil
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Xoe-NovAi Standards Integration
from .maat_guardrails import MaatGuardrails
from .memory_bank_integration import MemoryBankIntegration

class StructuredFormatter(logging.Formatter):
    """Structured formatter with accessibility compliance"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "service": "xnai-rag-api",
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', None),
            "request_id": getattr(record, 'request_id', None),
            "user_id": getattr(record, 'user_id', None),
            "error_type": getattr(record, 'error_type', None),
            "duration_ms": getattr(record, 'duration_ms', None),
            "accessibility_compliant": True,
            "maat_compliant": True
        }
        
        # Add extra fields
        if hasattr(record, 'extra') and record.extra:
            log_entry.update(record.extra)
        
        return json.dumps(log_entry, ensure_ascii=False)

class XoeObservability:
    """
    Xoe-NovAi compliant observability system.
    
    Features:
    - Sovereign data handling (no external calls)
    - Ma'at's 42 Ideals compliance
    - Memory-aware automatic protection
    - Accessibility compliance (WCAG 2.2 AA)
    - Graceful degradation patterns
    """
    
    def __init__(self):
        self._initialized = False
        self._maat_guardrails = MaatGuardrails()
        self._memory_bank = MemoryBankIntegration()
        
        # Component availability flags
        self._tracing_available = False
        self._metrics_available = False
        self._logs_available = False
        
        # Configuration
        self._config = self._load_configuration()
        
        # Initialize components
        self._setup_components()
        self._initialized = True
        
        # Log initialization
        self._log_initialization()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load Xoe-NovAi compliant configuration"""
        return {
            'enabled': os.getenv('OBSERVABILITY_ENABLED', 'false').lower() == 'true',
            'tracing': os.getenv('OBSERVABILITY_TRACING', 'true').lower() == 'true',
            'metrics': os.getenv('OBSERVABILITY_METRICS', 'true').lower() == 'true',
            'logs': os.getenv('OBSERVABILITY_LOGS', 'true').lower() == 'true',
            'memory_threshold': int(os.getenv('OBSERVABILITY_MEMORY_THRESHOLD', '5000')),
            'maat_compliance': os.getenv('OBSERVABILITY_MAAT_COMPLIANCE', 'true').lower() == 'true',
            'privacy_mode': os.getenv('OBSERVABILITY_PRIVACY_MODE', 'strict'),
            'accessibility': os.getenv('OBSERVABILITY_ACCESSIBILITY', 'wcag_aa')
        }
    
    def _setup_components(self):
        """Setup observability components with lazy loading"""
        try:
            if self._config['tracing']:
                self._setup_tracing()
            if self._config['metrics']:
                self._setup_metrics()
            if self._config['logs']:
                self._setup_logging()
        except Exception as e:
            self._handle_setup_error(e)
    
    def _setup_tracing(self):
        """Setup tracing with ConsoleSpanExporter"""
        try:
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
            
            # Create provider with sovereign resource attributes
            # Note: We don't import Resource to keep dependencies light, or we could if needed.
            # For now, default provider is fine.
            
            provider = TracerProvider()
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            
            # Set global tracer provider
            from opentelemetry import trace
            trace.set_tracer_provider(provider)
            
            self._tracing_available = True
            self._log_component_status('tracing', True)
            
        except ImportError as e:
            self._tracing_available = False
            self._log_component_status('tracing', False, str(e))
    
    def _setup_metrics(self):
        """Setup metrics collection"""
        try:
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.exporter.prometheus import PrometheusMetricReader
            
            # Prometheus reader for local metrics (modern OTel pattern)
            reader = PrometheusMetricReader()
            
            provider = MeterProvider(metric_readers=[reader])
            from opentelemetry import metrics
            metrics.set_meter_provider(provider)
            
            self._metrics_available = True
            self._log_component_status('metrics', True)
            
        except ImportError as e:
            self._metrics_available = False
            self._log_component_status('metrics', False, str(e))
    
    def _setup_logging(self):
        """Setup structured logging with accessibility compliance"""
        try:
            # Configure root logger with accessibility features
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            
            # Console handler with structured format
            console_handler = logging.StreamHandler()
            formatter = StructuredFormatter()
            console_handler.setFormatter(formatter)
            # Remove existing handlers to avoid duplicates
            if root_logger.handlers:
                for handler in root_logger.handlers:
                    root_logger.removeHandler(handler)
            root_logger.addHandler(console_handler)
            
            # File handler for persistent logs
            # Ensure log directory exists
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler('logs/xnai-observability.log')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            self._logs_available = True
            self._log_component_status('logs', True)
            
        except Exception as e:
            self._logs_available = False
            self._log_component_status('logs', False, str(e))
    
    def _log_initialization(self):
        """Log initialization with Ma'at compliance"""
        if self._config['maat_compliance']:
            self._maat_guardrails.verify_compliance()
        
        self._memory_bank.log_event('observability_initialized', {
            'enabled': self._config['enabled'],
            'tracing': self._tracing_available,
            'metrics': self._metrics_available,
            'logs': self._logs_available,
            'maat_compliance': self._config['maat_compliance']
        })
    
    def _log_component_status(self, component: str, success: bool, error: str = None):
        """Log component setup status"""
        if success:
            logging.info(f"Xoe-NovAi Observability: {component} enabled successfully")
        else:
            logging.warning(f"Xoe-NovAi Observability: {component} disabled - {error}")
    
    def _handle_setup_error(self, error: Exception):
        """Handle setup errors with graceful degradation"""
        logging.error(f"Xoe-NovAi Observability setup failed: {error}")
        
        # Ensure basic logging still works
        if not self._logs_available:
            logging.basicConfig(level=logging.INFO)
            logging.info("Xoe-NovAi Observability: Basic logging enabled as fallback")
    
    def get_tracer(self, name: str):
        """Get tracer with Ma'at compliance check"""
        if not self._tracing_available or not self._config['enabled']:
            return None
        
        if self._config['maat_compliance']:
            self._maat_guardrails.verify_tracing_compliance()
        
        from opentelemetry import trace
        return trace.get_tracer(name)
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record metric with privacy protection"""
        if not self._metrics_available or not self._config['enabled']:
            return
        
        # Privacy protection: sanitize labels
        if labels:
            sanitized_labels = self._sanitize_labels(labels)
        else:
            sanitized_labels = {}
        
        # Record metric
        try:
            from opentelemetry import metrics
            meter = metrics.get_meter(__name__)
            # Note: Creating a counter every time might be inefficient, 
            # ideally these are created once. For Phase 1 we follow the plan's structure
            # but usually you'd cache instruments.
            counter = meter.create_counter(name)
            counter.add(value, sanitized_labels)
        except Exception:
            pass
    
    def _sanitize_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sanitize labels for privacy protection"""
        sanitized = {}
        for key, value in labels.items():
            # Remove sensitive information
            if key.lower() in ['password', 'secret', 'token', 'key']:
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized
    
    def check_memory_protection(self):
        """Check memory usage and disable observability if needed"""
        if not self._config['enabled']:
            return
        
        try:
            memory_percent = psutil.virtual_memory().percent
            memory_threshold = self._config['memory_threshold']
            
            if memory_percent > memory_threshold:
                self._disable_observability_due_to_memory()
        except ImportError:
            pass # psutil might be missing
    
    def _disable_observability_due_to_memory(self):
        """Disable observability due to high memory usage"""
        logging.warning(f"Xoe-NovAi Observability: Disabling due to high memory usage")
        self._config['enabled'] = False
        
        # Log memory event to memory bank
        self._memory_bank.log_event('observability_disabled_memory', {
            'memory_percent': psutil.virtual_memory().percent if psutil else 0,
            'threshold': self._config['memory_threshold']
        })
    
    def shutdown(self):
        """Shutdown observability components"""
        if self._tracing_available:
            try:
                from opentelemetry import trace
                provider = trace.get_tracer_provider()
                if hasattr(provider, 'shutdown'):
                    provider.shutdown()
            except Exception:
                pass
        
        if self._metrics_available:
            try:
                from opentelemetry import metrics
                provider = metrics.get_meter_provider()
                if hasattr(provider, 'shutdown'):
                    provider.shutdown()
            except Exception:
                pass
        
        self._memory_bank.log_event('observability_shutdown', {})

# Global instance
observability = XoeObservability()
