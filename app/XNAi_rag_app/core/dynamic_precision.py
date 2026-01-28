"""
⚠️  DYNAMIC PRECISION MANAGER - DISABLED BY DEFAULT (GPU-Only Beta Feature)

WARNING: This module is DISABLED by default and requires GPU hardware.
Dynamic precision switching depends on AWQ quantization which requires NVIDIA GPU with CUDA support.

STATUS: Beta feature for advanced users only
DEPENDENCY: Requires active AWQ quantizer (GPU-only)
ENABLEMENT: Automatically enabled when AWQ_ENABLED=true and GPU hardware detected

This module provides intelligent FP16↔INT8 switching for GPU users with AWQ quantization.
CPU-only deployments use standard FP16 inference without dynamic precision switching.

For GPU users: See docs/01-getting-started/advanced-awq-setup.md
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum

from XNAi_rag_app.core.logging_config import get_logger
from XNAi_rag_app.core.metrics import metrics_collector
from XNAi_rag_app.core.awq_quantizer import CPUAWQQuantizer, QuantizationConfig

logger = get_logger(__name__)

class PrecisionLevel(Enum):
    """Supported precision levels"""
    FP16 = "fp16"
    INT8 = "int8"
    AUTO = "auto"

@dataclass
class PrecisionContext:
    """Context for precision decision making"""
    query: str
    complexity_score: float
    accessibility_context: Optional[Dict[str, Any]] = None
    historical_performance: Optional[Dict[str, float]] = None
    user_preferences: Optional[Dict[str, Any]] = None

@dataclass
class PrecisionDecision:
    """Result of precision selection"""
    selected_precision: PrecisionLevel
    confidence_score: float
    reasoning: str
    expected_latency_ms: float
    expected_accuracy: float
    accessibility_optimized: bool
    decision_time_ms: float

@dataclass
class SwitchingMetrics:
    """Metrics for precision switching performance"""
    total_switches: int = 0
    successful_switches: int = 0
    failed_switches: int = 0
    average_switch_time_ms: float = 0.0
    precision_distribution: Dict[str, int] = None

    def __post_init__(self):
        if self.precision_distribution is None:
            self.precision_distribution = {'fp16': 0, 'int8': 0}

class PrecisionSwitchError(Exception):
    """Error during precision switching operations"""
    pass

class DynamicPrecisionManager:
    """
    Intelligent precision manager for AWQ quantization systems.

    Provides dynamic FP16↔INT8 switching based on query complexity,
    accessibility needs, and performance optimization goals.
    """

    def __init__(
        self,
        awq_quantizer: CPUAWQQuantizer,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the dynamic precision manager.

        Args:
            awq_quantizer: CPU AWQ quantizer instance
            config: Optional configuration overrides
        """
        self.awq_quantizer = awq_quantizer
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Configuration with defaults
        self.config = {
            'complexity_threshold': 0.7,  # Switch to FP16 above this
            'accessibility_boost': 1.2,   # Increase complexity for accessibility
            'voice_command_reduction': 0.7,  # Reduce complexity for voice commands
            'min_decision_time_ms': 0.1,  # Minimum decision time for stability
            'max_decision_time_ms': 10.0, # Maximum decision time before fallback
            'enable_learning': True,      # Learn from performance history
            'enable_monitoring': True,    # Enable metrics collection
            'cache_decisions': True,      # Cache similar query decisions
        }
        if config:
            self.config.update(config)

        # Initialize components
        self.metrics = SwitchingMetrics()
        self._decision_cache: Dict[str, PrecisionDecision] = {}
        self._performance_history: Dict[str, List[float]] = {}
        self._accessibility_patterns: Dict[str, float] = {}

        # Setup monitoring
        if self.config['enable_monitoring']:
            self._setup_metrics()

        self.logger.info("Dynamic Precision Manager initialized", extra={
            'complexity_threshold': self.config['complexity_threshold'],
            'enable_learning': self.config['enable_learning'],
            'cache_enabled': self.config['cache_decisions']
        })

    def _setup_metrics(self) -> None:
        """Setup Prometheus metrics for precision switching"""
        try:
            # Precision selection gauge
            metrics_collector.create_gauge(
                'precision_selection_confidence',
                'Confidence score for precision selection decisions',
                ['query_type', 'selected_precision']
            )

            # Switching performance histogram
            metrics_collector.create_histogram(
                'precision_switching_duration',
                'Time taken for precision switching operations',
                ['operation_type', 'success']
            )

            # Decision cache hit ratio
            metrics_collector.create_gauge(
                'precision_cache_hit_ratio',
                'Ratio of cache hits to total decisions',
                []
            )

            # Precision distribution counter
            metrics_collector.create_counter(
                'precision_selections_total',
                'Total number of precision selections',
                ['precision', 'reason']
            )

        except Exception as e:
            self.logger.warning(f"Failed to setup metrics: {e}")

    async def select_optimal_precision(
        self,
        query: str,
        accessibility_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> PrecisionDecision:
        """
        Select optimal precision for query based on multiple factors.

        Args:
            query: Input query text
            accessibility_context: Accessibility-related context
            user_context: User preferences and context

        Returns:
            PrecisionDecision with selected precision and metadata
        """
        decision_start = time.time()

        try:
            # Check cache first for similar queries
            if self.config['cache_decisions']:
                cached_decision = self._check_cache(query)
                if cached_decision:
                    self.logger.debug("Using cached precision decision", extra={
                        'query_hash': hash(query) % 1000,
                        'cached_precision': cached_decision.selected_precision.value
                    })
                    return cached_decision

            # Create precision context
            context = PrecisionContext(
                query=query,
                complexity_score=self._calculate_query_complexity(query),
                accessibility_context=accessibility_context,
                user_context=user_context
            )

            # Adjust complexity based on accessibility
            if accessibility_context:
                context.complexity_score = self._adjust_for_accessibility(
                    context.complexity_score, accessibility_context
                )

            # Consider user preferences
            if user_context:
                context.complexity_score = self._adjust_for_user_preferences(
                    context.complexity_score, user_context
                )

            # Apply learning from historical performance
            if self.config['enable_learning']:
                context.complexity_score = self._adjust_for_history(
                    query, context.complexity_score
                )

            # Make precision decision
            decision = await self._make_precision_decision(context)

            # Cache the decision
            if self.config['cache_decisions']:
                self._cache_decision(query, decision)

            # Update metrics
            self._update_metrics(decision)

            decision_time = (time.time() - decision_start) * 1000
            decision.decision_time_ms = decision_time

            # Ensure minimum decision time for stability
            if decision_time < self.config['min_decision_time_ms']:
                await asyncio.sleep((self.config['min_decision_time_ms'] - decision_time) / 1000)

            self.logger.info("Precision decision made", extra={
                'selected_precision': decision.selected_precision.value,
                'complexity_score': context.complexity_score,
                'confidence': decision.confidence_score,
                'accessibility_optimized': decision.accessibility_optimized,
                'decision_time_ms': decision_time
            })

            return decision

        except Exception as e:
            self.logger.error(f"Precision selection failed: {e}")
            # Fallback to safe defaults
            return PrecisionDecision(
                selected_precision=PrecisionLevel.FP16,
                confidence_score=0.5,
                reasoning=f"Fallback due to error: {e}",
                expected_latency_ms=50.0,
                expected_accuracy=0.95,
                accessibility_optimized=False,
                decision_time_ms=(time.time() - decision_start) * 1000
            )

    async def execute_with_precision(
        self,
        query: str,
        inference_func: Callable,
        accessibility_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute inference with optimal precision selection.

        Args:
            query: Input query
            inference_func: Function to execute inference (should accept precision parameter)
            accessibility_context: Accessibility context
            user_context: User context

        Returns:
            Dict containing results and precision metadata
        """
        execution_start = time.time()

        try:
            # Select optimal precision
            decision = await self.select_optimal_precision(
                query, accessibility_context, user_context
            )

            # Execute inference with selected precision
            inference_start = time.time()
            result = await inference_func(decision.selected_precision.value)
            inference_time = (time.time() - inference_start) * 1000

            # Record performance for learning
            if self.config['enable_learning']:
                self._record_performance(query, decision.selected_precision, inference_time)

            total_execution_time = (time.time() - execution_start) * 1000

            result_metadata = {
                'precision_used': decision.selected_precision.value,
                'confidence_score': decision.confidence_score,
                'inference_time_ms': inference_time,
                'decision_time_ms': decision.decision_time_ms,
                'total_execution_time_ms': total_execution_time,
                'accessibility_optimized': decision.accessibility_optimized,
                'reasoning': decision.reasoning
            }

            self.logger.info("Precision execution completed", extra={
                'precision': decision.selected_precision.value,
                'inference_time_ms': inference_time,
                'total_time_ms': total_execution_time,
                'success': True
            })

            # Add metadata to result
            if isinstance(result, dict):
                result['_precision_metadata'] = result_metadata
            else:
                result = {
                    'result': result,
                    '_precision_metadata': result_metadata
                }

            return result

        except Exception as e:
            self.logger.error(f"Precision execution failed: {e}")
            # Return error result with metadata
            return {
                'error': str(e),
                'success': False,
                '_precision_metadata': {
                    'precision_used': 'error',
                    'execution_time_ms': (time.time() - execution_start) * 1000,
                    'error_type': type(e).__name__
                }
            }

    def get_metrics(self) -> SwitchingMetrics:
        """Get current switching metrics."""
        return self.metrics

    def reset_metrics(self) -> None:
        """Reset all metrics to initial state."""
        self.metrics = SwitchingMetrics()
        if self.config['enable_monitoring']:
            self._setup_metrics()

    # Private helper methods

    def _check_cache(self, query: str) -> Optional[PrecisionDecision]:
        """Check if similar query decision exists in cache."""
        # Simple hash-based caching (can be improved with more sophisticated similarity)
        query_hash = str(hash(query) % 10000)

        if query_hash in self._decision_cache:
            cached = self._decision_cache[query_hash]
            # Check if cache is still valid (within time window)
            if time.time() - cached.decision_time_ms < 3600000:  # 1 hour
                return cached

        return None

    def _cache_decision(self, query: str, decision: PrecisionDecision) -> None:
        """Cache precision decision for future use."""
        query_hash = str(hash(query) % 10000)
        self._decision_cache[query_hash] = decision

        # Limit cache size
        if len(self._decision_cache) > 1000:
            # Remove oldest entries (simple FIFO)
            oldest_key = min(self._decision_cache.keys(),
                           key=lambda k: self._decision_cache[k].decision_time_ms)
            del self._decision_cache[oldest_key]

    def _calculate_query_complexity(self, query: str) -> float:
        """
        Calculate query complexity score (0.0 to 1.0).
        Higher scores indicate need for higher precision.
        """
        # Length-based complexity
        length_score = min(len(query.split()) / 50.0, 1.0)

        # Vocabulary diversity
        words = query.lower().split()
        unique_words = set(words)
        vocab_score = len(unique_words) / len(words) if words else 0.0

        # Technical term indicators
        technical_terms = {
            'algorithm', 'quantum', 'neural', 'optimization', 'complexity',
            'analysis', 'computation', 'mathematical', 'scientific', 'research',
            'implementation', 'architecture', 'system', 'performance', 'efficiency'
        }
        technical_score = sum(1 for word in words if word in technical_terms) / max(len(words), 1)

        # Sentence structure complexity
        sentences = query.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        structure_score = min(avg_sentence_length / 20.0, 1.0)

        # Weighted combination
        complexity = (
            length_score * 0.25 +
            vocab_score * 0.20 +
            technical_score * 0.30 +
            structure_score * 0.25
        )

        return min(max(complexity, 0.0), 1.0)  # Clamp to [0, 1]

    def _adjust_for_accessibility(
        self,
        complexity_score: float,
        accessibility_context: Dict[str, Any]
    ) -> float:
        """
        Adjust complexity based on accessibility requirements.

        Voice commands: Reduce complexity (prefer faster INT8)
        Screen reader: Slightly increase complexity (prefer accurate FP16)
        Critical accessibility: Maintain or increase complexity
        """
        if accessibility_context.get('is_voice_command', False):
            # Voice commands are typically simpler but time-critical
            adjusted_score = complexity_score * self.config['voice_command_reduction']
            self.logger.debug("Accessibility adjustment: voice command reduction", extra={
                'original_score': complexity_score,
                'adjusted_score': adjusted_score
            })
            return adjusted_score

        if accessibility_context.get('screen_reader_active', False):
            # Screen readers need higher accuracy for comprehension
            adjusted_score = complexity_score * self.config['accessibility_boost']
            self.logger.debug("Accessibility adjustment: screen reader boost", extra={
                'original_score': complexity_score,
                'adjusted_score': adjusted_score
            })
            return adjusted_score

        if accessibility_context.get('critical_accessibility', False):
            # Critical accessibility functions get highest precision
            return min(complexity_score * 1.5, 1.0)

        return complexity_score

    def _adjust_for_user_preferences(
        self,
        complexity_score: float,
        user_context: Dict[str, Any]
    ) -> float:
        """Adjust complexity based on user preferences."""
        # Speed preference: reduce complexity threshold
        if user_context.get('prefers_speed', False):
            return complexity_score * 0.8

        # Accuracy preference: increase complexity threshold
        if user_context.get('prefers_accuracy', False):
            return complexity_score * 1.2

        # Power user: dynamic adjustment based on usage patterns
        if user_context.get('power_user', False):
            # Power users get more FP16 for complex queries
            return complexity_score * 1.1

        return complexity_score

    def _adjust_for_history(
        self,
        query: str,
        complexity_score: float
    ) -> float:
        """Adjust complexity based on historical performance."""
        query_type = self._categorize_query(query)

        if query_type in self._performance_history:
            recent_performance = self._performance_history[query_type][-5:]  # Last 5
            avg_performance = sum(recent_performance) / len(recent_performance)

            # If recent performance was poor with current precision, adjust
            if avg_performance < 0.8:  # Poor performance threshold
                # Increase complexity to prefer FP16
                return min(complexity_score * 1.3, 1.0)

            elif avg_performance > 0.95:  # Excellent performance
                # Decrease complexity to prefer INT8
                return complexity_score * 0.9

        return complexity_score

    async def _make_precision_decision(self, context: PrecisionContext) -> PrecisionDecision:
        """Make the final precision decision based on context."""
        complexity_threshold = self.config['complexity_threshold']

        # Determine selected precision
        if context.complexity_score >= complexity_threshold:
            selected_precision = PrecisionLevel.FP16
            confidence = min((context.complexity_score - complexity_threshold) / (1 - complexity_threshold), 1.0)
            reasoning = f"High complexity query (score: {context.complexity_score:.2f}) requires FP16 precision"
            expected_accuracy = 0.96
        else:
            selected_precision = PrecisionLevel.INT8
            confidence = min((complexity_threshold - context.complexity_score) / complexity_threshold, 1.0)
            reasoning = f"Standard complexity query (score: {context.complexity_score:.2f}) can use efficient INT8"
            expected_accuracy = 0.94

        # Adjust reasoning for accessibility
        accessibility_optimized = False
        if context.accessibility_context:
            if context.accessibility_context.get('is_voice_command'):
                reasoning += " (optimized for voice command speed)"
                accessibility_optimized = True
            elif context.accessibility_context.get('screen_reader_active'):
                reasoning += " (optimized for screen reader accuracy)"
                accessibility_optimized = True

        # Expected latency based on precision and complexity
        if selected_precision == PrecisionLevel.FP16:
            expected_latency = 45 + (context.complexity_score * 20)  # 45-65ms
        else:
            expected_latency = 25 + (context.complexity_score * 10)  # 25-35ms

        return PrecisionDecision(
            selected_precision=selected_precision,
            confidence_score=confidence,
            reasoning=reasoning,
            expected_latency_ms=expected_latency,
            expected_accuracy=expected_accuracy,
            accessibility_optimized=accessibility_optimized,
            decision_time_ms=0.0  # Will be set by caller
        )

    def _categorize_query(self, query: str) -> str:
        """Categorize query for historical performance tracking."""
        query_lower = query.lower()

        if any(term in query_lower for term in ['calculate', 'compute', 'solve', 'algorithm']):
            return 'mathematical'
        elif any(term in query_lower for term in ['explain', 'describe', 'what is', 'how does']):
            return 'explanatory'
        elif any(term in query_lower for term in ['write', 'create', 'generate', 'code']):
            return 'generative'
        elif any(term in query_lower for term in ['open', 'navigate', 'select', 'click']):
            return 'accessibility'
        else:
            return 'general'

    def _record_performance(
        self,
        query: str,
        precision: PrecisionLevel,
        inference_time_ms: float
    ) -> None:
        """Record performance for learning."""
        query_type = self._categorize_query(query)

        if query_type not in self._performance_history:
            self._performance_history[query_type] = []

        # Normalize performance score (lower time = better performance)
        # Assuming 20-100ms range, normalize to 0-1 scale
        normalized_performance = max(0, min(1, 1 - (inference_time_ms - 20) / 80))

        self._performance_history[query_type].append(normalized_performance)

        # Limit history size
        if len(self._performance_history[query_type]) > 20:
            self._performance_history[query_type] = self._performance_history[query_type][-20:]

    def _update_metrics(self, decision: PrecisionDecision) -> None:
        """Update internal metrics."""
        self.metrics.total_switches += 1

        precision_key = decision.selected_precision.value
        if precision_key in self.metrics.precision_distribution:
            self.metrics.precision_distribution[precision_key] += 1

        # Update average switch time (simplified)
        if hasattr(decision, 'decision_time_ms'):
            current_avg = self.metrics.average_switch_time_ms
            total_switches = self.metrics.total_switches
            self.metrics.average_switch_time_ms = (
                (current_avg * (total_switches - 1)) + decision.decision_time_ms
            ) / total_switches

        # Update Prometheus metrics
        if self.config['enable_monitoring']:
            try:
                metrics_collector.set_gauge(
                    'precision_selection_confidence',
                    decision.confidence_score,
                    {
                        'query_type': 'general',  # Could be more specific
                        'selected_precision': precision_key
                    }
                )

                metrics_collector.increment_counter(
                    'precision_selections_total',
                    {
                        'precision': precision_key,
                        'reason': 'complexity_analysis'
                    }
                )

                # Cache hit ratio
                cache_hits = sum(1 for d in self._decision_cache.values()
                               if time.time() - d.decision_time_ms < 3600000)
                total_decisions = len(self._decision_cache)
                if total_decisions > 0:
                    hit_ratio = cache_hits / total_decisions
                    metrics_collector.set_gauge(
                        'precision_cache_hit_ratio',
                        hit_ratio,
                        []
                    )

            except Exception as e:
                self.logger.warning(f"Failed to update Prometheus metrics: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        if exc_type:
            self.logger.error(f"Error in precision manager context: {exc_val}")
        # Cleanup if needed
        return False
