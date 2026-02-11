# Xoe-NovAi Core Module
# ======================
# Central utilities for configuration, logging, metrics, and dependencies.
"""
Xoe-NovAi Core Module
Central utilities for configuration, logging, metrics, and dependencies.
"""

from .config_loader import load_config, get_config_value
from .logging_config import setup_logging, get_logger, PerformanceLogger
from .metrics import metrics_collector, start_metrics_server
from .dependencies import (
    get_llm,
    get_embeddings,
    get_vectorstore,
    get_redis_client,
    get_http_client,
    get_curator,
    get_services,
    get_rag_service,
    get_voice_interface,
    get_research_agent,
    get_awq_quantizer,
    get_dynamic_precision_manager
)
from .observability import observability
from .services_init import orchestrator

__all__ = [
    'load_config',
    'get_config_value',
    'setup_logging',
    'get_logger',
    'PerformanceLogger',
    'metrics_collector',
    'start_metrics_server',
    'get_redis_client',
    'get_http_client',
    'get_llm',
    'get_embeddings',
    'get_vectorstore',
    'get_curator',
    'get_awq_quantizer',
    'get_dynamic_precision_manager',
    'get_services',
    'get_rag_service',
    'get_voice_interface',
    'get_research_agent',
    'observability',
    'orchestrator'
]