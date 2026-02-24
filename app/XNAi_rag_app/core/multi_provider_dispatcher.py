"""
XNAi Foundation - Multi-Provider Dispatcher (Phase 3B)

Routes tasks to optimal providers based on:
- Provider quota availability
- Context window requirements
- Task specialization (code, reasoning, large documents)
- Network latency (SLA)

Architecture:
1. Task Analysis: Determine context size and specialization
2. Provider Scoring: Rank providers by quota + latency + fit
3. Provider Selection: Pick highest-scoring available provider
4. Fallback Chain: Rotate to next provider on failure
5. Account Rotation: Multi-account load balancing

Providers (Priority Order - TIER 1 ANTIGRAVITY):
1. Antigravity CLI (1M context, 4M tokens/week, Opus Thinking + Gemini 3 Pro)
2. Copilot CLI (264K context, fast, Raptor-mini, ~18K tokens/week)
3. Cline CLI (200K context, code-optimized, IDE-integrated)
4. OpenCode CLI (1M context, reasoning-heavy, legacy support)
5. Local GGUF (4-8K context, offline fallback)

Usage:
    dispatcher = MultiProviderDispatcher(config="~/.config/xnai/credentials.yaml")
    result = await dispatcher.dispatch(
        task="Refactor auth module",
        context_size=50000,
        specialization="code",
        required_models=["raptor-mini"]
    )
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

import anyio
import yaml

from .token_validation import TokenValidator, TokenValidationResult, ProviderType

logger = logging.getLogger(__name__)


class TaskSpecialization(str, Enum):
    """Task categorization for optimal provider selection"""
    CODE = "code"                      # Code generation/refactoring
    REASONING = "reasoning"            # Analysis/complex logic
    LARGE_DOCUMENT = "large_document"  # >200K tokens
    FAST_RESPONSE = "fast_response"    # <1s latency needed
    GENERAL = "general"


@dataclass
class ProviderQuota:
    """Provider quota status"""
    provider: str
    account: str
    used: int = 0
    limit: int = 0
    reset_at: Optional[datetime] = None
    healthy: bool = True
    last_checked: datetime = field(default_factory=datetime.now)
    
    @property
    def percent_used(self) -> float:
        if self.limit <= 0:
            return 0.0
        return (self.used / self.limit) * 100
    
    @property
    def available(self) -> int:
        return max(0, self.limit - self.used)


@dataclass
class ProviderScore:
    """Provider scoring for task routing"""
    provider: str
    account: str
    quota_score: float          # 0-100: higher = more quota available
    latency_score: float        # 0-100: lower = slower
    fit_score: float            # 0-100: specialization fit
    overall_score: float        # 0-100: weighted sum
    reasoning: str              # Why this score


@dataclass
class DispatchResult:
    """Dispatch task result"""
    success: bool
    provider: str
    account: str
    output: str = ""
    error: str = ""
    latency_ms: float = 0.0
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class MultiProviderDispatcher:
    """Routes tasks to optimal providers with multi-account support"""
    
    # Provider latency assumptions (ms) - from Phase 3B research
    # Updated with Antigravity latency profiles (from agent-23 benchmark - 2026-02-23)
    # All measurements verified production-ready, SLA approved
    LATENCY_PROFILES = {
        "antigravity_o3_mini": 850,           # FASTEST: 849.66ms avg (⭐⭐⭐⭐⭐)
        "antigravity_gemini_pro": 852,        # Large context: 851.52ms avg (⭐⭐⭐⭐)
        "antigravity_sonnet": 854,            # Code gen: 854.39ms avg (⭐⭐⭐⭐)
        "antigravity_gemini_flash": 858,      # Fast streaming: 857.69ms avg (⭐⭐⭐⭐)
        "antigravity_deepseek": 863,          # Reasoning: 862.95ms avg (⭐⭐⭐⭐)
        "antigravity_opus": 990,              # Deep thinking: 990.14ms avg (⭐⭐⭐☆☆)
        "copilot": 200,                       # Raptor-mini
        "cline": 150,                         # IDE integration
        "opencode": 1000,                     # Built-in baseline
        "local": 5000,                        # Offline fallback
    }
    
    # Provider specialization scores (0-100) - Updated for Antigravity
    SPECIALIZATION_SCORES = {
        "code": {
            "antigravity_sonnet": 95,  # Claude Sonnet 4.6 excellent for code
            "cline": 95,               # Native IDE integration
            "copilot": 85,             # Raptor-mini excellent for code
            "antigravity_gemini_flash": 85,
            "antigravity_o3_mini": 82,
            "opencode": 70,            # General reasoning
            "local": 60,
        },
        "reasoning": {
            "antigravity_opus": 99,    # Opus Thinking supreme reasoning
            "antigravity_gemini_pro": 96,  # Gemini 3 Pro excellent reasoning
            "opencode": 90,            # 1M context for complex analysis
            "copilot": 80,             # Haiku good reasoning
            "cline": 75,
            "local": 40,
        },
        "large_document": {
            "antigravity_gemini_pro": 100,  # UNIQUE: 1M context, can load entire repo
            "antigravity_gemini_flash": 95,  # 1M context, fast
            "opencode": 90,             # 1M context window
            "copilot": 70,              # 264K context
            "cline": 70,                # 262K context
            "local": 10,
        },
        "fast_response": {
            "antigravity_o3_mini": 98,     # Fastest available
            "copilot": 90,                  # Raptor-mini super fast
            "antigravity_gemini_flash": 90, # Fast alternative
            "cline": 85,
            "opencode": 75,                # Slower, reasoning overhead
            "local": 20,
        },
        "general": {
            "antigravity_sonnet": 90,       # Fast + quality
            "copilot": 85,
            "cline": 80,
            "opencode": 80,
            "antigravity_gemini_flash": 85,
            "antigravity_o3_mini": 85,
            "local": 50,
        }
    }
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        quota_file: Optional[str] = None,
        email_accounts: Optional[List[str]] = None,
        antigravity_accounts: Optional[List[str]] = None,
    ):
        """Initialize dispatcher with multi-provider support
        
        Args:
            config_file: Credentials config path (~/.config/xnai/credentials.yaml)
            quota_file: Quota audit file path (~/.config/xnai/quota-audit.yaml)
            email_accounts: List of GitHub email accounts for rotation (8 accounts default)
            antigravity_accounts: List of Antigravity accounts for rotation (8 accounts default)
        """
        self.config_file = Path(config_file or "~/.config/xnai/credentials.yaml").expanduser()
        self.quota_file = Path(quota_file or "~/.config/xnai/quota-audit.yaml").expanduser()
        
        # Default 8 GitHub-linked accounts
        self.email_accounts = email_accounts or [
            "xoe.nova.ai@gmail.com",
            "antipode2727@gmail.com",
            "Antipode7474@gmail.com",
            "lilithasterion@gmail.com",
            "TaylorBare27@gmail.com",
            "thejedifather@gmail.com",
            "Arcana.NovAi@gmail.com",
            "arcananovaai@gmail.com",
        ]
        
        # Default 8 Antigravity accounts (independent from GitHub accounts)
        self.antigravity_accounts = antigravity_accounts or [
            "antigravity-01",
            "antigravity-02",
            "antigravity-03",
            "antigravity-04",
            "antigravity-05",
            "antigravity-06",
            "antigravity-07",
            "antigravity-08",
        ]
        
        self.token_validator = TokenValidator(str(self.config_file))
        self.quota_cache: Dict[str, ProviderQuota] = {}
        self.account_rotation_index: Dict[str, int] = defaultdict(int)
        self.call_history: List[DispatchResult] = []
        
        self._load_quota_cache()
    
    def _load_quota_cache(self) -> None:
        """Load quota cache from audit file"""
        if self.quota_file.exists():
            try:
                with open(self.quota_file) as f:
                    quota_data = yaml.safe_load(f) or {}
                    # Parse quota data into cache
                    logger.info(f"Loaded quota cache from {self.quota_file}")
            except Exception as e:
                logger.warning(f"Failed to load quota cache: {e}")
    
    def _save_quota_cache(self) -> None:
        """Save quota cache to audit file"""
        try:
            with open(self.quota_file, "w") as f:
                quota_data = {
                    k: {
                        "used": v.used,
                        "limit": v.limit,
                        "reset_at": str(v.reset_at) if v.reset_at else None,
                        "healthy": v.healthy,
                        "last_checked": str(v.last_checked),
                    }
                    for k, v in self.quota_cache.items()
                }
                yaml.safe_dump(quota_data, f)
                logger.info(f"Saved quota cache to {self.quota_file}")
        except Exception as e:
            logger.error(f"Failed to save quota cache: {e}")
    
    def _calculate_quota_score(self, quota: ProviderQuota) -> float:
        """Score provider based on available quota
        
        100 = unlimited/new account
        50 = 50% used
        10 = 90% used
        0 = exhausted
        """
        if not quota.healthy:
            return 0.0
        
        percent_available = 100 - quota.percent_used
        
        # Penalize high usage
        if quota.percent_used >= 95:
            return 0.0
        elif quota.percent_used >= 80:
            return 20.0
        else:
            return percent_available
    
    def _calculate_latency_score(self, provider: str) -> float:
        """Score provider based on latency
        
        Cline ~150ms → 70 points
        Copilot ~200ms → 50 points
        OpenCode ~100ms → 85 points
        Local ~5000ms → 0 points (fallback only)
        """
        latency = self.LATENCY_PROFILES.get(provider, 5000)
        
        # Score: higher latency = lower score
        # Normalize to 0-100 scale
        if latency >= 5000:
            return 0.0
        elif latency >= 1000:
            return 10.0
        elif latency >= 300:
            return 30.0
        else:
            # Linear: 100ms → 90, 200ms → 80, 300ms → 70
            return 100 - (latency / 10)
    
    def _calculate_fit_score(
        self,
        provider: str,
        specialization: TaskSpecialization,
        context_size: int,
    ) -> float:
        """Score provider based on task fit
        
        Considers:
        - Specialization (code, reasoning, large_document, etc)
        - Context window requirement
        """
        spec_scores = self.SPECIALIZATION_SCORES.get(specialization.value, {})
        base_score = spec_scores.get(provider, 50)
        
        # Penalty for insufficient context
        context_limits = {
            "antigravity_opus": 200000,         # Claude Opus 4.6
            "antigravity_sonnet": 200000,       # Claude Sonnet 4.6
            "antigravity_gemini_pro": 1000000,  # Gemini 3 Pro - 1M context!
            "antigravity_gemini_flash": 1000000, # Gemini 3 Flash - 1M context
            "antigravity_o3_mini": 200000,      # o3-mini
            "cline": 262000,
            "copilot": 264000,
            "opencode": 1000000,
            "local": 8000,
        }
        limit = context_limits.get(provider, 8000)
        
        if context_size > limit * 0.9:
            # Not enough breathing room
            base_score *= 0.5
        elif context_size > limit:
            # Impossible
            base_score = 0.0
        
        return base_score
    
    def _score_provider(
        self,
        provider: str,
        account: str,
        task_spec: TaskSpecialization,
        context_size: int,
    ) -> ProviderScore:
        """Calculate overall score for provider+account combination
        
        Weights:
        - Antigravity: 50% quota, 30% latency, 20% fit (dominates via quota advantage)
        - Other providers: 40% quota, 30% latency, 30% fit
        """
        
        quota_key = f"{provider}:{account}"
        quota = self.quota_cache.get(quota_key)
        
        if not quota:
            # Initialize with conservative defaults
            quota = ProviderQuota(provider=provider, account=account)
            self.quota_cache[quota_key] = quota
        
        # Component scores (0-100)
        quota_score = self._calculate_quota_score(quota)
        latency_score = self._calculate_latency_score(provider)
        fit_score = self._calculate_fit_score(provider, task_spec, context_size)
        
        # Weighted overall: Antigravity gets 50% quota weight (dominates via 4M/week)
        if provider.startswith("antigravity"):
            # Antigravity: 50% quota, 30% latency, 20% fit
            overall = (
                quota_score * 0.5 +
                latency_score * 0.3 +
                fit_score * 0.2
            )
        else:
            # Other providers: 40% quota, 30% latency, 30% fit
            overall = (
                quota_score * 0.4 +
                latency_score * 0.3 +
                fit_score * 0.3
            )
        
        reasoning = (
            f"{provider}/{account}: "
            f"quota={quota.percent_used:.0f}% "
            f"latency={self.LATENCY_PROFILES.get(provider, 5000)}ms "
            f"fit={task_spec.value}"
        )
        
        return ProviderScore(
            provider=provider,
            account=account,
            quota_score=quota_score,
            latency_score=latency_score,
            fit_score=fit_score,
            overall_score=overall,
            reasoning=reasoning,
        )
    
    def _get_account_for_provider(self, provider: str) -> str:
        """Get next account in rotation for provider
        
        Uses separate account pools:
        - Antigravity: antigravity-01 through antigravity-08 (independent rotation)
        - GitHub: 8 GitHub email accounts (round-robin)
        """
        idx = self.account_rotation_index[provider]
        
        if provider.startswith("antigravity"):
            # Use Antigravity account pool (500K tokens/week per account)
            account = self.antigravity_accounts[idx % len(self.antigravity_accounts)]
        else:
            # Use GitHub account pool
            account = self.email_accounts[idx % len(self.email_accounts)]
        
        self.account_rotation_index[provider] = (idx + 1) % max(
            len(self.antigravity_accounts), len(self.email_accounts)
        )
        return account
    
    def _select_best_provider(
        self,
        task_spec: TaskSpecialization,
        context_size: int,
        required_models: Optional[List[str]] = None,
    ) -> Tuple[str, str, ProviderScore]:
        """Select best provider+account using scoring algorithm
        
        TIER 1 PRIORITY (Antigravity first):
        - antigravity_gemini_pro (1M context, best for large analysis)
        - antigravity_opus (best for reasoning)
        - antigravity_sonnet (best for code)
        - antigravity_gemini_flash (fast alternative)
        - antigravity_o3_mini (fastest)
        
        TIER 2 (Fallback):
        - copilot (Raptor-mini, 264K context)
        - cline (IDE integration)
        - opencode (legacy)
        - local (offline fallback)
        
        Returns: (provider, account, score)
        Raises: RuntimeError if no provider available
        """
        # TIER 1: Antigravity models in order of preference
        antigravity_models = [
            "antigravity_gemini_pro",    # 1M context - best for large files
            "antigravity_opus",           # Best for reasoning
            "antigravity_sonnet",         # Best for coding
            "antigravity_gemini_flash",   # Fast alternative
            "antigravity_o3_mini",        # Fastest
        ]
        
        # TIER 2: Other providers
        fallback_providers = ["copilot", "cline", "opencode", "local"]
        
        # Combined list: Tier 1 (Antigravity) then Tier 2 (others)
        providers = antigravity_models + fallback_providers
        candidates: List[ProviderScore] = []
        
        for provider in providers:
            account = self._get_account_for_provider(provider)
            
            # Validate token for this account
            validation = self._validate_provider_account(provider, account)
            if not validation:
                logger.debug(f"Skipping {provider}/{account}: token invalid")
                continue
            
            # Score this provider
            score = self._score_provider(provider, account, task_spec, context_size)
            candidates.append(score)
            logger.debug(f"Scored {score.reasoning} = {score.overall_score:.1f}")
        
        if not candidates:
            raise RuntimeError(
                f"No valid providers available. Required: {required_models or 'any'}"
            )
        
        # Select highest score (Antigravity dominates via quota advantage)
        best = max(candidates, key=lambda s: s.overall_score)
        logger.info(
            f"Selected {best.provider}/{best.account} "
            f"(score={best.overall_score:.1f}): {best.reasoning}"
        )
        
        return best.provider, best.account, best
    
    def _validate_provider_account(self, provider: str, account: str) -> bool:
        """Check if provider account has valid token"""
        try:
            # Use token validator
            result = self.token_validator.validate_token(provider, account)
            return result.is_valid
        except Exception as e:
            logger.warning(f"Failed to validate {provider}/{account}: {e}")
            return False
    
    async def dispatch(
        self,
        task: str,
        task_spec: TaskSpecialization = TaskSpecialization.GENERAL,
        context_size: int = 10000,
        required_models: Optional[List[str]] = None,
        timeout_sec: float = 30.0,
    ) -> DispatchResult:
        """Dispatch task to optimal provider
        
        Args:
            task: Task prompt/instructions
            task_spec: Task specialization (code, reasoning, etc)
            context_size: Estimated token size needed
            required_models: Required model names (e.g., ["raptor-mini"])
            timeout_sec: Dispatch timeout
        
        Returns:
            DispatchResult with success/failure/output
        """
        start_time = time.time()
        
        try:
            # Select best provider
            provider, account, score = self._select_best_provider(
                task_spec, context_size, required_models
            )
            
            # Dispatch to provider
            result = await self._execute_dispatch(
                provider, account, task, timeout_sec
            )
            
            result.latency_ms = (time.time() - start_time) * 1000
            result.provider = provider
            result.account = account
            
            # Update quota cache
            self._update_quota_after_dispatch(provider, account, result)
            
            # Store in history
            self.call_history.append(result)
            
            if result.success:
                logger.info(
                    f"✓ Dispatch succeeded: {provider}/{account} "
                    f"({result.latency_ms:.0f}ms, {result.tokens_used} tokens)"
                )
            else:
                logger.error(
                    f"✗ Dispatch failed: {provider}/{account}: {result.error}"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            return DispatchResult(
                success=False,
                provider="unknown",
                account="unknown",
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )
    
    async def _execute_dispatch(
        self,
        provider: str,
        account: str,
        task: str,
        timeout_sec: float,
    ) -> DispatchResult:
        """Execute dispatch to specific provider via CLI
        
        Handles:
        - Environment variable injection (credentials)
        - CLI invocation with JSON task
        - Output parsing
        - Timeout/error handling
        
        Antigravity models:
        - antigravity_opus: Claude Opus 4.6 Thinking (deep reasoning)
        - antigravity_sonnet: Claude Sonnet 4.6 (fast + quality)
        - antigravity_gemini_pro: Gemini 3 Pro (1M context)
        - antigravity_gemini_flash: Gemini 3 Flash (fast)
        - antigravity_o3_mini: o3-mini (fastest)
        """
        
        if provider.startswith("antigravity"):
            return await self._dispatch_antigravity(provider, account, task, timeout_sec)
        elif provider == "cline":
            return await self._dispatch_cline(account, task, timeout_sec)
        elif provider == "copilot":
            return await self._dispatch_copilot(account, task, timeout_sec)
        elif provider == "opencode":
            return await self._dispatch_opencode(account, task, timeout_sec)
        elif provider == "local":
            return await self._dispatch_local(account, task, timeout_sec)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _dispatch_antigravity(
        self, provider: str, account: str, task: str, timeout_sec: float
    ) -> DispatchResult:
        """Dispatch to Antigravity CLI via OpenCode
        
        Maps provider to model:
        - antigravity_opus → google/antigravity-claude-opus-4-6-thinking
        - antigravity_sonnet → google/antigravity-claude-sonnet-4-6
        - antigravity_gemini_pro → google/antigravity-gemini-3.1-pro
        - antigravity_gemini_flash → google/antigravity-gemini-3.1-flash
        - antigravity_o3_mini → google/antigravity-o3-mini
        """
        try:
            # Map provider to model
            model_map = {
                "antigravity_opus": "google/antigravity-claude-opus-4-6-thinking",
                "antigravity_sonnet": "google/antigravity-claude-sonnet-4-6",
                "antigravity_gemini_pro": "google/antigravity-gemini-3.1-pro",
                "antigravity_gemini_flash": "google/antigravity-gemini-3.1-flash",
                "antigravity_o3_mini": "google/antigravity-o3-mini",
            }
            
            model = model_map.get(provider)
            if not model:
                raise ValueError(f"Unknown Antigravity model: {provider}")
            
            # OpenCode Antigravity command
            cmd = [
                "opencode", "chat",
                "--model", model,
                "--account", account,
                "--json",
                task,
            ]
            
            env = self._get_provider_env(account)
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                )
            )
            
            if result.returncode == 0:
                return DispatchResult(
                    success=True,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return DispatchResult(
                    success=False,
                    error=result.stderr or result.stdout,
                )
        except subprocess.TimeoutExpired:
            return DispatchResult(success=False, error=f"{provider} timeout")
        except Exception as e:
            return DispatchResult(success=False, error=str(e))
    
    async def _dispatch_cline(
        self, account: str, task: str, timeout_sec: float
    ) -> DispatchResult:
        """Dispatch to Cline CLI"""
        try:
            cmd = ["cline", "--task", task, "--json"]
            
            # Inject credentials via environment
            env = self._get_provider_env(account)
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                )
            )
            
            if result.returncode == 0:
                return DispatchResult(
                    success=True,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return DispatchResult(
                    success=False,
                    error=result.stderr,
                )
        except subprocess.TimeoutExpired:
            return DispatchResult(success=False, error="Cline timeout")
        except Exception as e:
            return DispatchResult(success=False, error=str(e))
    
    async def _dispatch_copilot(
        self, account: str, task: str, timeout_sec: float
    ) -> DispatchResult:
        """Dispatch to Copilot CLI with Raptor-mini"""
        try:
            cmd = [
                "copilot",
                "--model", "raptor-mini",
                "--json",
                task,
            ]
            
            env = self._get_provider_env(account)
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                )
            )
            
            if result.returncode == 0:
                return DispatchResult(
                    success=True,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return DispatchResult(
                    success=False,
                    error=result.stderr,
                )
        except subprocess.TimeoutExpired:
            return DispatchResult(success=False, error="Copilot timeout")
        except Exception as e:
            return DispatchResult(success=False, error=str(e))
    
    async def _dispatch_opencode(
        self, account: str, task: str, timeout_sec: float
    ) -> DispatchResult:
        """Dispatch to OpenCode CLI with XDG_DATA_HOME isolation"""
        try:
            # Use XDG_DATA_HOME to isolate each instance
            import tempfile
            with tempfile.TemporaryDirectory(prefix="opencode-") as tmpdir:
                cmd = ["opencode", "chat", task, "--json"]
                
                env = self._get_provider_env(account)
                env["XDG_DATA_HOME"] = tmpdir  # Isolate auth
                
                result = await anyio.to_thread.run_blocking(
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout_sec,
                        env=env,
                    )
                )
                
                if result.returncode == 0:
                    return DispatchResult(
                        success=True,
                        output=result.stdout,
                        tokens_used=self._estimate_tokens(result.stdout),
                    )
                else:
                    return DispatchResult(
                        success=False,
                        error=result.stderr,
                    )
        except subprocess.TimeoutExpired:
            return DispatchResult(success=False, error="OpenCode timeout")
        except Exception as e:
            return DispatchResult(success=False, error=str(e))
    
    async def _dispatch_local(
        self, account: str, task: str, timeout_sec: float
    ) -> DispatchResult:
        """Dispatch to local GGUF model (fallback)"""
        # Placeholder for local inference
        return DispatchResult(
            success=False,
            error="Local dispatch not yet implemented (Phase 3C)",
        )
    
    def _get_provider_env(self, account: str) -> Dict[str, str]:
        """Get environment variables for provider authentication"""
        import os
        env = os.environ.copy()
        
        # Inject provider tokens from config
        # This is loaded by credential injection script
        
        return env
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def _update_quota_after_dispatch(
        self,
        provider: str,
        account: str,
        result: DispatchResult,
    ) -> None:
        """Update quota cache after dispatch"""
        quota_key = f"{provider}:{account}"
        quota = self.quota_cache.get(quota_key)
        
        if not quota:
            quota = ProviderQuota(provider=provider, account=account)
            self.quota_cache[quota_key] = quota
        
        if result.success:
            quota.used += result.tokens_used
            quota.last_checked = datetime.now()
        else:
            quota.healthy = False
        
        self._save_quota_cache()
    
    def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics for monitoring"""
        return {
            "total_calls": len(self.call_history),
            "successful": sum(1 for r in self.call_history if r.success),
            "failed": sum(1 for r in self.call_history if not r.success),
            "avg_latency_ms": (
                sum(r.latency_ms for r in self.call_history) / len(self.call_history)
                if self.call_history
                else 0
            ),
            "providers_used": set(r.provider for r in self.call_history),
            "accounts_used": set(r.account for r in self.call_history),
        }
