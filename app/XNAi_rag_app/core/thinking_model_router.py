"""
Thinking Model Router

Routes tasks to thinking vs regular models based on:
- Task complexity
- Quality requirements
- Latency requirements
- Available quota
"""

from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity classification"""
    SIMPLE = 0.3      # Code completion, simple Q&A
    MEDIUM = 0.6      # Refactoring, moderate reasoning
    COMPLEX = 0.9     # Architecture, debugging, novel problems


class ModelVariant(Enum):
    """Model variant selection"""
    REGULAR = "regular"
    THINKING = "thinking"


@dataclass
class RoutingDecision:
    """Decision output from router"""
    model: str
    variant: ModelVariant
    reason: str
    estimated_latency_ms: int
    estimated_tokens: int


class ThinkingModelRouter:
    """
    Routes tasks to optimal model variant
    
    Decision logic:
    1. If complexity >= 0.7 AND quality_required AND (latency_flexible OR large_context):
       -> Use thinking model
    2. Otherwise:
       -> Use regular model
    """
    
    # Model mappings: thinking_model -> regular_model
    MODEL_PAIRS = {
        "google/antigravity-claude-opus-4-6-thinking": "google/antigravity-claude-opus-4-6",
        "google/antigravity-claude-opus-4-5-thinking": "google/antigravity-claude-opus-4-5",
        "google/antigravity-claude-sonnet-4-5-thinking": "google/antigravity-claude-sonnet-4-6",
    }
    
    # Task categories with complexity scores
    TASK_SCORES = {
        # Simple tasks (<0.4)
        "code_completion": 0.2,
        "simple_qa": 0.3,
        "format_conversion": 0.25,
        "summarization": 0.35,
        
        # Medium tasks (0.4-0.7)
        "refactoring": 0.55,
        "debugging": 0.65,
        "code_review": 0.6,
        "optimization": 0.65,
        
        # Complex tasks (>0.7)
        "architecture": 0.85,
        "novel_problem": 0.8,
        "research": 0.75,
        "system_design": 0.9,
        "complex_debugging": 0.8,
    }
    
    # Latency profiles (milliseconds)
    LATENCY_PROFILES = {
        "regular": {"min": 150, "max": 500, "avg": 300},
        "thinking": {"min": 200, "max": 900, "avg": 550},  # Based on test results
    }
    
    # Token consumption ratios (thinking / regular)
    TOKEN_OVERHEAD = {
        "simple": 1.05,      # 5% overhead for simple tasks
        "medium": 1.15,      # 15% overhead for medium
        "complex": 1.25,     # 25% overhead for complex
    }
    
    def __init__(self):
        self.decision_history: List[RoutingDecision] = []
        self.thinking_usage_percent = 0.0  # Track quota allocation
    
    def route(
        self,
        task_type: str,
        complexity: Optional[float] = None,
        quality_required: bool = True,
        latency_flexible: bool = False,
        max_latency_ms: int = 1000,
        available_tokens: Optional[int] = None,
        context_size: Optional[int] = None,
    ) -> RoutingDecision:
        """
        Route task to optimal model variant
        
        Args:
            task_type: Type of task (used for complexity lookup)
            complexity: Override complexity score (0-1)
            quality_required: Is high quality essential?
            latency_flexible: Can we accept higher latency?
            max_latency_ms: Maximum acceptable latency
            available_tokens: Token budget remaining
            context_size: Size of context (tokens)
        
        Returns:
            RoutingDecision with selected model and reasoning
        """
        
        # Determine complexity
        if complexity is None:
            complexity = self.TASK_SCORES.get(task_type, 0.5)
        
        # Core routing logic
        use_thinking = self._should_use_thinking(
            complexity=complexity,
            quality_required=quality_required,
            latency_flexible=latency_flexible,
            max_latency_ms=max_latency_ms,
            context_size=context_size,
        )
        
        # Select best model based on variant
        if use_thinking:
            model = self._select_thinking_model()
            variant = ModelVariant.THINKING
            reason = self._get_thinking_reason(
                complexity, quality_required, latency_flexible
            )
        else:
            model = "google/antigravity-claude-opus-4-6"  # Default regular
            variant = ModelVariant.REGULAR
            reason = "Standard model sufficient for this task"
        
        # Estimate resources
        est_tokens = self._estimate_tokens(
            complexity, variant, available_tokens
        )
        est_latency = self._estimate_latency(variant)
        
        # Check token budget
        if available_tokens and est_tokens > available_tokens:
            logger.warning(
                f"Token budget exceeded: need {est_tokens}, have {available_tokens}"
            )
            # Fall back to regular model to save tokens
            if variant == ModelVariant.THINKING:
                model = "google/antigravity-claude-opus-4-6"
                variant = ModelVariant.REGULAR
                reason = "Switched to regular model to save tokens"
        
        # Create decision
        decision = RoutingDecision(
            model=model,
            variant=variant,
            reason=reason,
            estimated_latency_ms=est_latency,
            estimated_tokens=est_tokens,
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _should_use_thinking(
        self,
        complexity: float,
        quality_required: bool,
        latency_flexible: bool,
        max_latency_ms: int,
        context_size: Optional[int],
    ) -> bool:
        """Determine if thinking model is appropriate"""
        
        # Too simple -> use regular
        if complexity < 0.7:
            return False
        
        # Quality required but latency tight -> use regular (faster)
        if quality_required and max_latency_ms < 400:
            return False
        
        # Latency flexible -> can use thinking
        if latency_flexible:
            return True
        
        # Complex + quality + enough time -> use thinking
        if complexity > 0.7 and quality_required and max_latency_ms > 500:
            return True
        
        return False
    
    def _select_thinking_model(self) -> str:
        """Select best thinking model based on task"""
        # For now, use Opus 4.6 thinking (best quality)
        # Could be enhanced with additional logic
        return "google/antigravity-claude-opus-4-6-thinking"
    
    def _get_thinking_reason(
        self, complexity: float, quality: bool, latency: bool
    ) -> str:
        """Generate explanation for thinking model selection"""
        reasons = []
        
        if complexity > 0.8:
            reasons.append("High complexity task")
        if quality:
            reasons.append("Quality priority")
        if latency:
            reasons.append("Flexible latency")
        
        return "; ".join(reasons) if reasons else "Thinking model selected"
    
    def _estimate_tokens(
        self, complexity: float, variant: ModelVariant, available: Optional[int]
    ) -> int:
        """Estimate token consumption"""
        # Base estimate: 2000 tokens for typical task
        base = 2000
        
        # Complexity factor
        base *= (1 + complexity * 0.5)
        
        # Variant overhead
        if variant == ModelVariant.THINKING:
            complexity_category = (
                "simple" if complexity < 0.4 else
                "medium" if complexity < 0.7 else
                "complex"
            )
            base *= self.TOKEN_OVERHEAD[complexity_category]
        
        return int(base)
    
    def _estimate_latency(self, variant: ModelVariant) -> int:
        """Estimate latency in milliseconds"""
        profile = self.LATENCY_PROFILES[variant.value]
        return profile["avg"]
    
    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        if not self.decision_history:
            return {}
        
        thinking_count = sum(
            1 for d in self.decision_history
            if d.variant == ModelVariant.THINKING
        )
        
        return {
            "total_routed": len(self.decision_history),
            "thinking_count": thinking_count,
            "regular_count": len(self.decision_history) - thinking_count,
            "thinking_percent": thinking_count / len(self.decision_history) * 100,
        }


# Singleton instance
_router_instance: Optional[ThinkingModelRouter] = None


def get_thinking_router() -> ThinkingModelRouter:
    """Get or create router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ThinkingModelRouter()
    return _router_instance


# Example usage
if __name__ == "__main__":
    router = get_thinking_router()
    
    # Test cases
    test_cases = [
        {
            "task_type": "simple_qa",
            "latency_flexible": False,
            "max_latency_ms": 300,
        },
        {
            "task_type": "architecture",
            "latency_flexible": True,
            "max_latency_ms": 2000,
        },
        {
            "task_type": "code_completion",
            "latency_flexible": False,
            "max_latency_ms": 200,
        },
        {
            "task_type": "complex_debugging",
            "quality_required": True,
            "latency_flexible": True,
            "max_latency_ms": 1500,
        },
    ]
    
    print("🧠 Thinking Model Router Test\n")
    for i, test in enumerate(test_cases, 1):
        decision = router.route(**test)
        print(f"{i}. {test['task_type']}")
        print(f"   Model: {decision.model}")
        print(f"   Variant: {decision.variant.value}")
        print(f"   Reason: {decision.reason}")
        print(f"   Est. latency: {decision.estimated_latency_ms}ms")
        print(f"   Est. tokens: {decision.estimated_tokens}\n")
    
    print("Stats:", router.get_routing_stats())
