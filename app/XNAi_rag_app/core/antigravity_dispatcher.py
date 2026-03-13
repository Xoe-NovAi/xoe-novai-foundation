"""
XNAi Foundation - Antigravity CLI Dispatcher (Phase 3B Priority 0)

Antigravity is a top-tier provider delivering:
- 4M tokens/week across 8 accounts (500K/account, Sunday reset)
- Claude Opus 4.6 Thinking (200K context, deep reasoning)
- Gemini 3 Pro (1M context, full-codebase analysis)
- Claude Sonnet 4.6 (200K context, general tasks)
- Deep models: DeepSeek v3, GPT-4.1, o3-mini

Architecture:
1. Account Management: 8-account rotation with weekly reset
2. Model Selection: Route by task specialization
3. Quota Tracking: Per-account quota management
4. Fallback: Auto-rotate on exhaustion

Integration with MultiProviderDispatcher:
- Antigravity is TIER 1 primary provider
- Scores highest for reasoning + large-context tasks
- Fallback chain: Claude Opus → Gemini 3 Pro → Sonnet → Others

Usage:
    dispatcher = AntigravityDispatcher(
        config_file="~/.config/xnai/antigravity-credentials.yaml"
    )
    result = await dispatcher.dispatch(
        task="Analyze full codebase architecture",
        context_size=500000,  # >200K → Gemini 3 Pro
        model_preference="gemini-3.1-pro"
    )
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio
import yaml

logger = logging.getLogger(__name__)


@dataclass
class AntigravityAccount:
    """Antigravity account quota status"""
    account_id: str  # antigravity-01, antigravity-02, etc.
    tokens_used: int = 0
    tokens_limit: int = 500000  # 500K/week
    reset_day: str = "sunday"  # Weekly reset
    last_reset: datetime = field(default_factory=datetime.now)
    healthy: bool = True
    
    @property
    def tokens_available(self) -> int:
        return max(0, self.tokens_limit - self.tokens_used)
    
    @property
    def quota_percent_used(self) -> float:
        return (self.tokens_used / self.tokens_limit) * 100
    
    def is_quota_exhausted(self) -> bool:
        return self.quota_percent_used >= 95


class AntigravityModelSelector:
    """Select optimal Antigravity model for task"""
    
    # Model routing matrix
    MODELS = {
        "claude-opus-4.6-thinking": {
            "context": 200000,
            "output_limit": 64000,
            "thinking_budget": (8192, 32768),
            "specialization": ["reasoning", "architecture", "security", "complex_decision"],
            "speed": "slow",  # ~1-2 seconds + thinking
            "latency_ms": 1500,
            "cost": "free (quota-based)",
        },
        "claude-sonnet-4.6-antigravity": {
            "context": 200000,
            "output_limit": 64000,
            "thinking_budget": None,
            "specialization": ["code_generation", "general", "refactoring"],
            "speed": "fast",
            "latency_ms": 800,
            "cost": "free (quota-based)",
        },
        "gemini-3.1-pro": {
            "context": 1000000,  # 1M - UNIQUE ADVANTAGE
            "output_limit": 65536,
            "thinking_budget": None,
            "specialization": ["large_document", "full_codebase", "reasoning", "research"],
            "speed": "medium",
            "latency_ms": 1200,
            "cost": "free (quota-based)",
        },
        "gemini-3.1-flash": {
            "context": 1000000,
            "output_limit": 65536,
            "thinking_budget": None,
            "specialization": ["fast_response", "batch_processing"],
            "speed": "very_fast",
            "latency_ms": 600,
            "cost": "free (quota-based)",
        },
        "deepseek-v3": {
            "context": 128000,
            "output_limit": 8000,
            "thinking_budget": None,
            "specialization": ["reasoning", "analysis"],
            "speed": "medium",
            "latency_ms": 1000,
            "cost": "free (quota-based)",
        },
        "gpt-4.1": {
            "context": 128000,
            "output_limit": 8000,
            "thinking_budget": None,
            "specialization": ["general", "code"],
            "speed": "medium",
            "latency_ms": 900,
            "cost": "free (quota-based)",
        },
        "o3-mini": {
            "context": 200000,
            "output_limit": 64000,
            "thinking_budget": None,
            "specialization": ["fast_response", "quick_tasks"],
            "speed": "very_fast",
            "latency_ms": 500,
            "cost": "free (quota-based)",
        },
    }
    
    @classmethod
    def select_model(cls, context_size: int, task_type: str, speed_critical: bool = False) -> str:
        """Select best Antigravity model for task
        
        Args:
            context_size: Estimated tokens needed
            task_type: code|reasoning|large_document|general
            speed_critical: Prefer fast model over quality
        
        Returns:
            Model name with format "google/antigravity-*"
        """
        
        # Special case: very large context (>1M)
        if context_size > 1000000:
            return "google/antigravity-gemini-3.1-pro"
        
        # Special case: 200K-1M context → prefer Gemini
        if context_size > 200000:
            if speed_critical:
                return "google/antigravity-gemini-3.1-flash"
            else:
                return "google/antigravity-gemini-3.1-pro"
        
        # Task-based routing
        if task_type == "reasoning":
            if speed_critical:
                return "google/antigravity-deepseek-v3"
            else:
                return "google/antigravity-claude-opus-4.6-thinking"
        
        elif task_type == "code_generation":
            if speed_critical:
                return "google/antigravity-o3-mini"
            else:
                return "google/antigravity-claude-sonnet-4.6-antigravity"
        
        elif task_type == "large_document":
            return "google/antigravity-gemini-3.1-pro"
        
        elif task_type == "general":
            if speed_critical:
                return "google/antigravity-o3-mini"
            else:
                return "google/antigravity-claude-sonnet-4.6-antigravity"
        
        else:
            # Default
            return "google/antigravity-claude-sonnet-4.6-antigravity"


class AntigravityDispatcher:
    """Dispatch tasks to Antigravity models via OpenCode CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize Antigravity dispatcher
        
        Args:
            config_file: Path to Antigravity credentials/config file
        """
        self.config_file = Path(config_file or "~/.config/xnai/antigravity-credentials.yaml").expanduser()
        self.quota_file = Path("~/.config/xnai/antigravity-quota.yaml").expanduser()
        
        # Initialize 8-account pool
        self.accounts: Dict[str, AntigravityAccount] = {}
        self.account_rotation_index = 0
        self.call_history: List[Dict[str, Any]] = []
        
        self._initialize_accounts()
        self._load_quota()
    
    def _initialize_accounts(self) -> None:
        """Initialize 8 Antigravity accounts"""
        for i in range(1, 9):
            account_id = f"antigravity-{i:02d}"
            self.accounts[account_id] = AntigravityAccount(account_id=account_id)
            logger.info(f"Initialized {account_id}: 500K tokens/week available")
    
    def _load_quota(self) -> None:
        """Load quota from previous session"""
        if self.quota_file.exists():
            try:
                with open(self.quota_file) as f:
                    quota_data = yaml.safe_load(f) or {}
                    for account_id, data in quota_data.get("accounts", {}).items():
                        if account_id in self.accounts:
                            self.accounts[account_id].tokens_used = data.get("tokens_used", 0)
                            # Check if reset needed (Sunday)
                            if self._should_reset():
                                self.accounts[account_id].tokens_used = 0
                                self.accounts[account_id].last_reset = datetime.now()
                logger.info(f"Loaded quota data from {self.quota_file}")
            except Exception as e:
                logger.warning(f"Failed to load quota file: {e}")
    
    def _save_quota(self) -> None:
        """Save quota to file"""
        try:
            quota_data = {
                "updated": datetime.now().isoformat(),
                "accounts": {
                    account_id: {
                        "tokens_used": account.tokens_used,
                        "tokens_limit": account.tokens_limit,
                        "quota_percent": account.quota_percent_used,
                    }
                    for account_id, account in self.accounts.items()
                },
                "totals": {
                    "total_tokens_used": sum(a.tokens_used for a in self.accounts.values()),
                    "total_tokens_available": sum(a.tokens_available for a in self.accounts.values()),
                }
            }
            
            with open(self.quota_file, "w") as f:
                yaml.safe_dump(quota_data, f)
            logger.debug(f"Saved quota state to {self.quota_file}")
        except Exception as e:
            logger.error(f"Failed to save quota file: {e}")
    
    def _should_reset(self) -> bool:
        """Check if quota should reset (Sundays)"""
        today = datetime.now().weekday()
        # 6 = Sunday
        return today == 6
    
    def _get_next_available_account(self) -> Optional[str]:
        """Get next available account with quota
        
        Returns:
            Account ID or None if all exhausted
        """
        # Try round-robin across all accounts
        for i in range(len(self.accounts)):
            idx = (self.account_rotation_index + i) % len(self.accounts)
            account_id = f"antigravity-{idx+1:02d}"
            
            if account_id in self.accounts:
                account = self.accounts[account_id]
                if account.tokens_available > 1000:  # Need at least 1K tokens
                    self.account_rotation_index = (idx + 1) % len(self.accounts)
                    return account_id
        
        # All exhausted
        return None
    
    async def dispatch(
        self,
        task: str,
        context_size: int = 10000,
        task_type: str = "general",
        model_preference: Optional[str] = None,
        timeout_sec: float = 60.0,
    ) -> Dict[str, Any]:
        """Dispatch task to Antigravity via OpenCode CLI
        
        Args:
            task: Task prompt
            context_size: Estimated tokens needed
            task_type: code|reasoning|large_document|general
            model_preference: Specific model, e.g., "gemini-3.1-pro"
            timeout_sec: Timeout in seconds
        
        Returns:
            Result dict with success, provider, model, output, latency, tokens_used
        """
        start_time = time.time()
        
        # Select account
        account_id = self._get_next_available_account()
        if not account_id:
            return {
                "success": False,
                "provider": "antigravity",
                "account": "none_available",
                "error": "All Antigravity accounts quota exhausted",
                "latency_ms": (time.time() - start_time) * 1000,
            }
        
        # Select model
        if model_preference:
            model_name = model_preference if model_preference.startswith("google/antigravity-") else f"google/antigravity-{model_preference}"
        else:
            model_name = AntigravityModelSelector.select_model(context_size, task_type)
        
        logger.info(f"Dispatching to {account_id} with {model_name}")
        
        # Execute dispatch
        try:
            cmd = ["opencode", "chat", "--model", model_name, "--json", task]
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                )
            )
            
            if result.returncode == 0:
                # Success
                tokens_used = self._estimate_tokens(result.stdout)
                self.accounts[account_id].tokens_used += tokens_used
                self._save_quota()
                
                return {
                    "success": True,
                    "provider": "antigravity",
                    "account": account_id,
                    "model": model_name,
                    "output": result.stdout,
                    "tokens_used": tokens_used,
                    "latency_ms": (time.time() - start_time) * 1000,
                }
            else:
                # Failure
                return {
                    "success": False,
                    "provider": "antigravity",
                    "account": account_id,
                    "model": model_name,
                    "error": result.stderr,
                    "latency_ms": (time.time() - start_time) * 1000,
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "provider": "antigravity",
                "account": account_id,
                "error": "Timeout",
                "latency_ms": (time.time() - start_time) * 1000,
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "antigravity",
                "account": account_id,
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000,
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status across all accounts"""
        return {
            "timestamp": datetime.now().isoformat(),
            "accounts": {
                account_id: {
                    "tokens_used": account.tokens_used,
                    "tokens_available": account.tokens_available,
                    "quota_percent": round(account.quota_percent_used, 1),
                }
                for account_id, account in self.accounts.items()
            },
            "totals": {
                "total_tokens_used": sum(a.tokens_used for a in self.accounts.values()),
                "total_tokens_available": sum(a.tokens_available for a in self.accounts.values()),
                "total_quota_percent": round(
                    (sum(a.tokens_used for a in self.accounts.values()) / (500000 * 8)) * 100,
                    1
                ),
            },
        }
