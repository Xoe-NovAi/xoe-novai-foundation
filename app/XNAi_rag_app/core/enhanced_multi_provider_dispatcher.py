"""
Enhanced Multi-Provider Dispatcher with Rate Limit Handling

This enhanced dispatcher integrates the rate limit handler to provide automatic
account rotation and context preservation. It addresses the critical issues
identified in the OpenCode usage scenario.

Key Improvements:
- Automatic rate limit detection and account rotation
- Context preservation across account switches
- Smart fallback strategies
- Integration with existing multi-account system
- Enhanced error handling and recovery

Author: XNAi Foundation
Version: 1.0.0
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

from .rate_limit_handler import SmartDispatcher, ContextManager, AccountRotator
from .token_validation import TokenValidator, TokenValidationResult, ProviderType
from .account_manager import AccountManager, get_account_manager

logger = logging.getLogger(__name__)


class TaskSpecialization(str, Enum):
    """Task categorization for optimal provider selection"""
    CODE = "code"                      # Code generation/refactoring
    REASONING = "reasoning"            # Analysis/complex logic
    LARGE_DOCUMENT = "large_document"  # >200K tokens
    FAST_RESPONSE = "fast_response"    # <1s latency needed
    GENERAL = "general"


@dataclass
class EnhancedDispatchResult:
    """Enhanced dispatch result with rate limit and context info"""
    success: bool
    provider: str
    account: str
    output: str = ""
    error: str = ""
    latency_ms: float = 0.0
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    rate_limit_triggered: bool = False
    context_preserved: bool = True
    fallback_used: bool = False
    session_id: Optional[str] = None


class EnhancedMultiProviderDispatcher:
    """Enhanced dispatcher with automatic rate limit handling and context preservation"""
    
    # Provider latency assumptions (ms) - from Phase 3B research
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
        enable_rate_limit_handling: bool = True,
        enable_context_preservation: bool = True,
    ):
        """Initialize enhanced dispatcher with rate limit handling
        
        Args:
            config_file: Credentials config path (~/.config/xnai/credentials.yaml)
            quota_file: Quota audit file path (~/.config/xnai/quota-audit.yaml)
            email_accounts: List of GitHub email accounts for rotation (8 accounts default)
            antigravity_accounts: List of Antigravity accounts for rotation (8 accounts default)
            enable_rate_limit_handling: Enable automatic rate limit detection and rotation
            enable_context_preservation: Enable context preservation across account switches
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
        self.quota_cache: Dict[str, Any] = {}
        self.account_rotation_index: Dict[str, int] = defaultdict(int)
        self.call_history: List[EnhancedDispatchResult] = []
        
        # Rate limit and context handling
        self.enable_rate_limit_handling = enable_rate_limit_handling
        self.enable_context_preservation = enable_context_preservation
        
        # Initialize rate limit handler components
        if self.enable_rate_limit_handling:
            self._initialize_rate_limit_handling()
        
        self._load_quota_cache()
    
    def _initialize_rate_limit_handling(self):
        """Initialize rate limit handling components"""
        # Create account list for rate limit handler
        accounts = []
        
        # Add GitHub accounts
        for email in self.email_accounts:
            accounts.append({
                "account_id": email,
                "provider": "github",
                "api_key": self._get_api_key_for_account(email)
            })
        
        # Add Antigravity accounts
        for account_id in self.antigravity_accounts:
            accounts.append({
                "account_id": account_id,
                "provider": "antigravity",
                "api_key": self._get_api_key_for_account(account_id)
            })
        
        # Initialize context manager
        self.context_manager = ContextManager()
        
        # Initialize smart dispatcher
        self.smart_dispatcher = SmartDispatcher(accounts, self.context_manager)
        
        logger.info(f"Rate limit handling initialized with {len(accounts)} accounts")
    
    def _get_api_key_for_account(self, account_id: str) -> str:
        """Get API key for account from config"""
        try:
            if not self.config_file.exists():
                return ""
            
            with open(self.config_file) as f:
                config = yaml.safe_load(f) or {}
            
            # Look for API key in config
            for provider, provider_config in config.items():
                if isinstance(provider_config, dict):
                    if account_id in provider_config:
                        return provider_config[account_id].get("api_key", "")
                    elif "accounts" in provider_config:
                        for account in provider_config["accounts"]:
                            if account.get("id") == account_id:
                                return account.get("api_key", "")
            
            return ""
        except Exception as e:
            logger.warning(f"Failed to get API key for {account_id}: {e}")
            return ""
    
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
                        "used": v.get("used", 0),
                        "limit": v.get("limit", 0),
                        "reset_at": str(v.get("reset_at")),
                        "healthy": v.get("healthy", True),
                        "last_checked": str(v.get("last_checked")),
                    }
                    for k, v in self.quota_cache.items()
                }
                yaml.safe_dump(quota_data, f)
                logger.info(f"Saved quota cache to {self.quota_file}")
        except Exception as e:
            logger.error(f"Failed to save quota cache: {e}")
    
    def _calculate_quota_score(self, quota: Any) -> float:
        """Score provider based on available quota"""
        if not quota.get("healthy", True):
            return 0.0
        
        used = quota.get("used", 0)
        limit = quota.get("limit", 1000000)
        
        if limit <= 0:
            return 0.0
        
        percent_used = (used / limit) * 100
        percent_available = 100 - percent_used
        
        # Penalize high usage
        if percent_used >= 95:
            return 0.0
        elif percent_used >= 80:
            return 20.0
        else:
            return percent_available
    
    def _calculate_latency_score(self, provider: str) -> float:
        """Score provider based on latency"""
        latency = self.LATENCY_PROFILES.get(provider, 5000)
        
        # Score: higher latency = lower score
        if latency >= 5000:
            return 0.0
        elif latency >= 1000:
            return 10.0
        elif latency >= 300:
            return 30.0
        else:
            return 100 - (latency / 10)
    
    def _calculate_fit_score(
        self,
        provider: str,
        specialization: TaskSpecialization,
        context_size: int,
    ) -> float:
        """Score provider based on task fit"""
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
            base_score *= 0.5
        elif context_size > limit:
            base_score = 0.0
        
        return base_score
    
    def _score_provider(
        self,
        provider: str,
        account: str,
        task_spec: TaskSpecialization,
        context_size: int,
    ) -> float:
        """Calculate overall score for provider+account combination"""
        quota_key = f"{provider}:{account}"
        quota = self.quota_cache.get(quota_key, {})
        
        # Component scores (0-100)
        quota_score = self._calculate_quota_score(quota)
        latency_score = self._calculate_latency_score(provider)
        fit_score = self._calculate_fit_score(provider, task_spec, context_size)
        
        # Weighted overall: Antigravity gets 50% quota weight (dominates via 4M/week)
        if provider.startswith("antigravity"):
            overall = quota_score * 0.5 + latency_score * 0.3 + fit_score * 0.2
        else:
            overall = quota_score * 0.4 + latency_score * 0.3 + fit_score * 0.3
        
        return overall
    
    def _get_account_for_provider(self, provider: str) -> str:
        """Get next account in rotation for provider"""
        idx = self.account_rotation_index[provider]
        
        if provider.startswith("antigravity"):
            account = self.antigravity_accounts[idx % len(self.antigravity_accounts)]
        else:
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
    ) -> Tuple[str, str, float]:
        """Select best provider+account using scoring algorithm"""
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
        candidates: List[Tuple[str, str, float]] = []
        
        for provider in providers:
            account = self._get_account_for_provider(provider)
            
            # Validate token for this account
            validation = self._validate_provider_account(provider, account)
            if not validation:
                logger.debug(f"Skipping {provider}/{account}: token invalid")
                continue
            
            # Score this provider
            score = self._score_provider(provider, account, task_spec, context_size)
            candidates.append((provider, account, score))
            logger.debug(f"Scored {provider}/{account} = {score:.1f}")
        
        if not candidates:
            raise RuntimeError(
                f"No valid providers available. Required: {required_models or 'any'}"
            )
        
        # Select highest score (Antigravity dominates via quota advantage)
        best_provider, best_account, best_score = max(candidates, key=lambda x: x[2])
        logger.info(
            f"Selected {best_provider}/{best_account} "
            f"(score={best_score:.1f})"
        )
        
        return best_provider, best_account, best_score
    
    def _validate_provider_account(self, provider: str, account: str) -> bool:
        """Check if provider account has valid token"""
        try:
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
        session_id: Optional[str] = None,
        preferred_account: Optional[str] = None,
    ) -> EnhancedDispatchResult:
        """Dispatch task with enhanced rate limit handling and context preservation
        
        Args:
            task: Task prompt/instructions
            task_spec: Task specialization (code, reasoning, etc)
            context_size: Estimated token size needed
            required_models: Required model names (e.g., ["raptor-mini"])
            timeout_sec: Dispatch timeout
            session_id: Session ID for context preservation
            preferred_account: Preferred account to use first
        
        Returns:
            EnhancedDispatchResult with success/failure/output and rate limit info
        """
        start_time = time.time()
        
        try:
            # Use enhanced rate limit handling if enabled
            if self.enable_rate_limit_handling and self.enable_context_preservation:
                return await self._dispatch_with_rate_limit_handling(
                    task, task_spec, context_size, timeout_sec, session_id, preferred_account
                )
            else:
                # Fallback to original dispatch logic
                return await self._dispatch_original(
                    task, task_spec, context_size, required_models, timeout_sec
                )
            
        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            return EnhancedDispatchResult(
                success=False,
                provider="unknown",
                account="unknown",
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )
    
    async def _dispatch_with_rate_limit_handling(
        self,
        task: str,
        task_spec: TaskSpecialization,
        context_size: int,
        timeout_sec: float,
        session_id: Optional[str],
        preferred_account: Optional[str],
    ) -> EnhancedDispatchResult:
        """Dispatch with rate limit handling and context preservation"""
        
        # Prepare context window from session
        context_window = []
        if session_id and self.enable_context_preservation:
            try:
                context = self.context_manager.load_context(session_id)
                if context and "messages" in context:
                    # Use last 5 messages as context
                    context_window = context["messages"][-5:]
            except Exception as e:
                logger.warning(f"Failed to load context for session {session_id}: {e}")
        
        # Use smart dispatcher for rate limit handling
        result = await self.smart_dispatcher.dispatch_with_rotation(
            task=task,
            session_id=session_id,
            preferred_account=preferred_account,
            context_window=context_window,
            timeout_sec=timeout_sec
        )
        
        # Convert to EnhancedDispatchResult
        dispatch_result = EnhancedDispatchResult(
            success=result["success"],
            provider="opencode",  # Smart dispatcher uses opencode primarily
            account=result.get("account_used", "unknown"),
            output=result.get("output", ""),
            error=result.get("error", ""),
            latency_ms=(time.time() - time.time()) * 1000,  # Would need actual timing
            tokens_used=self._estimate_tokens(result.get("output", "")),
            timestamp=datetime.now(),
            rate_limit_triggered=not result["success"] and "rate limit" in result.get("error", "").lower(),
            context_preserved=result.get("context_preserved", False),
            fallback_used=result.get("attempt", 1) > 1,
            session_id=result.get("session_id")
        )
        
        # Store in history
        self.call_history.append(dispatch_result)
        
        if dispatch_result.success:
            logger.info(
                f"✓ Enhanced dispatch succeeded: {dispatch_result.provider}/{dispatch_result.account} "
                f"({dispatch_result.latency_ms:.0f}ms, {dispatch_result.tokens_used} tokens)"
            )
        else:
            logger.error(
                f"✗ Enhanced dispatch failed: {dispatch_result.provider}/{dispatch_result.account}: {dispatch_result.error}"
            )
        
        return dispatch_result
    
    async def _dispatch_original(
        self,
        task: str,
        task_spec: TaskSpecialization,
        context_size: int,
        required_models: Optional[List[str]],
        timeout_sec: float,
    ) -> EnhancedDispatchResult:
        """Original dispatch logic without rate limit handling"""
        
        # Select best provider
        provider, account, score = self._select_best_provider(
            task_spec, context_size, required_models
        )
        
        # Dispatch to provider
        result = await self._execute_dispatch(
            provider, account, task, timeout_sec
        )
        
        result.latency_ms = (time.time() - time.time()) * 1000  # Would need actual timing
        result.provider = provider
        result.account = account
        
        # Update quota cache
        self._update_quota_after_dispatch(provider, account, result)
        
        # Store in history
        self.call_history.append(result)
        
        if result.success:
            logger.info(
                f"✓ Original dispatch succeeded: {provider}/{account} "
                f"({result.latency_ms:.0f}ms, {result.tokens_used} tokens)"
            )
        else:
            logger.error(
                f"✗ Original dispatch failed: {provider}/{account}: {result.error}"
            )
        
        return result
    
    async def _execute_dispatch(
        self,
        provider: str,
        account: str,
        task: str,
        timeout_sec: float,
    ) -> EnhancedDispatchResult:
        """Execute dispatch to specific provider via CLI"""
        
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
    ) -> EnhancedDispatchResult:
        """Dispatch to Antigravity CLI via OpenCode"""
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
                return EnhancedDispatchResult(
                    success=True,
                    provider="opencode",
                    account=account,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return EnhancedDispatchResult(
                    success=False,
                    provider="opencode",
                    account=account,
                    error=result.stderr or result.stdout,
                )
        except subprocess.TimeoutExpired:
            return EnhancedDispatchResult(success=False, provider="opencode", account=account, error="opencode timeout")
        except Exception as e:
            return EnhancedDispatchResult(success=False, provider="opencode", account=account, error=str(e))
    
    async def _dispatch_cline(
        self, account: str, task: str, timeout_sec: float
    ) -> EnhancedDispatchResult:
        """Dispatch to Cline CLI"""
        try:
            cmd = ["cline", "--task", task, "--json"]
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
                return EnhancedDispatchResult(
                    success=True,
                    provider="cline",
                    account=account,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return EnhancedDispatchResult(
                    success=False,
                    provider="cline",
                    account=account,
                    error=result.stderr,
                )
        except subprocess.TimeoutExpired:
            return EnhancedDispatchResult(success=False, provider="cline", account=account, error="Cline timeout")
        except Exception as e:
            return EnhancedDispatchResult(success=False, provider="cline", account=account, error=str(e))
    
    async def _dispatch_copilot(
        self, account: str, task: str, timeout_sec: float
    ) -> EnhancedDispatchResult:
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
                return EnhancedDispatchResult(
                    success=True,
                    provider="copilot",
                    account=account,
                    output=result.stdout,
                    tokens_used=self._estimate_tokens(result.stdout),
                )
            else:
                return EnhancedDispatchResult(
                    success=False,
                    provider="copilot",
                    account=account,
                    error=result.stderr,
                )
        except subprocess.TimeoutExpired:
            return EnhancedDispatchResult(success=False, provider="copilot", account=account, error="Copilot timeout")
        except Exception as e:
            return EnhancedDispatchResult(success=False, provider="copilot", account=account, error=str(e))
    
    async def _dispatch_opencode(
        self, account: str, task: str, timeout_sec: float
    ) -> EnhancedDispatchResult:
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
                    return EnhancedDispatchResult(
                        success=True,
                        provider="opencode",
                        account=account,
                        output=result.stdout,
                        tokens_used=self._estimate_tokens(result.stdout),
                    )
                else:
                    return EnhancedDispatchResult(
                        success=False,
                        provider="opencode",
                        account=account,
                        error=result.stderr,
                    )
        except subprocess.TimeoutExpired:
            return EnhancedDispatchResult(success=False, provider="opencode", account=account, error="OpenCode timeout")
        except Exception as e:
            return EnhancedDispatchResult(success=False, provider="opencode", account=account, error=str(e))
    
    async def _dispatch_local(
        self, account: str, task: str, timeout_sec: float
    ) -> EnhancedDispatchResult:
        """Dispatch to local GGUF model (fallback)"""
        return EnhancedDispatchResult(
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
        result: EnhancedDispatchResult,
    ) -> None:
        """Update quota cache after dispatch"""
        quota_key = f"{provider}:{account}"
        quota = self.quota_cache.get(quota_key, {})
        
        if not quota:
            quota = {"used": 0, "limit": 1000000, "healthy": True}
            self.quota_cache[quota_key] = quota
        
        if result.success:
            quota["used"] += result.tokens_used
            quota["last_checked"] = datetime.now()
        else:
            quota["healthy"] = False
        
        self._save_quota_cache()
    
    def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics for monitoring"""
        stats = {
            "total_calls": len(self.call_history),
            "successful": sum(1 for r in self.call_history if r.success),
            "failed": sum(1 for r in self.call_history if not r.success),
            "rate_limit_triggered": sum(1 for r in self.call_history if r.rate_limit_triggered),
            "context_preserved": sum(1 for r in self.call_history if r.context_preserved),
            "fallback_used": sum(1 for r in self.call_history if r.fallback_used),
            "avg_latency_ms": (
                sum(r.latency_ms for r in self.call_history) / len(self.call_history)
                if self.call_history
                else 0
            ),
            "providers_used": set(r.provider for r in self.call_history),
            "accounts_used": set(r.account for r in self.call_history),
        }
        
        # Add rate limit handler stats if available
        if hasattr(self, 'smart_dispatcher'):
            stats["rate_limit_stats"] = self.smart_dispatcher.get_rotation_stats()
        
        return stats
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session context for debugging"""
        if hasattr(self, 'context_manager'):
            return self.context_manager.load_context(session_id)
        return None
    
    def clear_session_context(self, session_id: str) -> None:
        """Clear session context"""
        if hasattr(self, 'context_manager'):
            self.context_manager.clear_context(session_id)