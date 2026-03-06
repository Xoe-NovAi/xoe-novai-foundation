"""
Quota Checking System - Pre-dispatch rate limit detection
Phase 3C-2: Smart Fallback Orchestration

Tier 1: Quota API checks (pre-dispatch, cached 5-10 min)
Tier 2: Circuit breaker (on HTTP 429 errors)
Tier 3: Response size tracking (post-dispatch validation)
"""

import asyncio
import time
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
import logging

import aiohttp

logger = logging.getLogger(__name__)


class QuotaStatus(Enum):
    """Provider quota status"""
    HEALTHY = "healthy"  # >50% quota remaining
    WARNING = "warning"  # 20-50% quota remaining
    CRITICAL = "critical"  # <20% quota remaining
    EXHAUSTED = "exhausted"  # >95% quota used
    UNKNOWN = "unknown"  # Cannot determine


@dataclass
class QuotaInfo:
    """Per-account quota information"""
    provider: str
    account_id: str
    tokens_remaining: int
    tokens_limit: int
    percent_used: float = field(default=0.0)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: QuotaStatus = QuotaStatus.UNKNOWN
    
    def __post_init__(self):
        self.percent_used = 100.0 * (1 - self.tokens_remaining / max(self.tokens_limit, 1))
        
        # Determine status based on remaining quota
        if self.percent_used >= 95:
            self.status = QuotaStatus.EXHAUSTED
        elif self.percent_used >= 80:
            self.status = QuotaStatus.CRITICAL
        elif self.percent_used >= 50:
            self.status = QuotaStatus.WARNING
        else:
            self.status = QuotaStatus.HEALTHY
    
    def is_stale(self, ttl_seconds: int = 300) -> bool:
        """Check if quota info is stale (>TTL old)"""
        age = (datetime.utcnow() - self.updated_at).total_seconds()
        return age > ttl_seconds
    
    def should_fallback(self, threshold_percent: float = 95.0) -> bool:
        """Should we fallback to another provider?"""
        return self.percent_used >= threshold_percent


class GeminiQuotaClient:
    """Gemini API quota checker"""
    
    API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/quotaStatus"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logger.getChild("GeminiQuotaClient")
    
    async def get_quota(self, api_key: Optional[str] = None) -> Optional[QuotaInfo]:
        """
        Fetch quota from Gemini API
        
        Returns:
            QuotaInfo if successful, None if API unavailable
        """
        key = api_key or self.api_key
        if not key:
            self.logger.warning("No Gemini API key provided")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"x-goog-api-key": key}
                async with session.get(
                    self.API_ENDPOINT,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse quota from response
                        # Gemini returns "current" (tokens used), not remaining
                        requests_quota = data.get("quotaStatus", {})
                        current = requests_quota.get("current", 0)
                        limit = requests_quota.get("limit", 1000000)
                        
                        remaining = max(0, limit - current)
                        
                        return QuotaInfo(
                            provider="gemini",
                            account_id=key[:8] + "...",
                            tokens_remaining=remaining,
                            tokens_limit=limit
                        )
                    else:
                        self.logger.warning(f"Gemini API returned {response.status}")
                        return None
        except asyncio.TimeoutError:
            self.logger.warning("Gemini quota API timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching Gemini quota: {e}")
            return None
    
    async def get_pessimistic_quota(self) -> QuotaInfo:
        """Return pessimistic quota (assume 90% used) when API unavailable"""
        return QuotaInfo(
            provider="gemini",
            account_id="unknown",
            tokens_remaining=100000,  # Assume 100K remaining (pessimistic)
            tokens_limit=1000000
        )


class CopilotQuotaClient:
    """Copilot CLI quota checker"""
    
    GITHUB_API_ENDPOINT = "https://api.github.com/user/copilot_metrics"
    
    def __init__(self, cli_path: Optional[str] = None, github_token: Optional[str] = None):
        self.cli_path = cli_path or "/usr/local/bin/copilot"
        self.github_token = github_token
        self.logger = logger.getChild("CopilotQuotaClient")
    
    async def get_quota_from_cli(self) -> Optional[QuotaInfo]:
        """
        Fetch quota from Copilot CLI
        
        Returns:
            QuotaInfo if CLI available and returning quota
        """
        try:
            # Try to run copilot CLI
            proc = await asyncio.create_subprocess_exec(
                self.cli_path,
                "quota",
                "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            
            if proc.returncode == 0:
                data = json.loads(stdout.decode())
                
                # Parse CLI response
                remaining = data.get("remaining", 0)
                limit = data.get("limit", 18750)  # 18.75K per week default
                
                return QuotaInfo(
                    provider="copilot",
                    account_id="cli_user",
                    tokens_remaining=remaining,
                    tokens_limit=limit
                )
            else:
                self.logger.warning(f"Copilot CLI failed: {stderr.decode()}")
                return None
        except FileNotFoundError:
            self.logger.warning("Copilot CLI not found")
            return None
        except asyncio.TimeoutError:
            self.logger.warning("Copilot CLI timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching Copilot quota from CLI: {e}")
            return None
    
    async def get_quota_from_github_api(self) -> Optional[QuotaInfo]:
        """
        Fetch quota from GitHub API (fallback)
        
        Returns:
            QuotaInfo if GitHub API available
        """
        if not self.github_token:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"token {self.github_token}"}
                async with session.get(
                    self.GITHUB_API_ENDPOINT,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        remaining = data.get("quota_remaining", 0)
                        limit = data.get("quota_limit", 18750)
                        
                        return QuotaInfo(
                            provider="copilot",
                            account_id="github_user",
                            tokens_remaining=remaining,
                            tokens_limit=limit
                        )
                    else:
                        self.logger.warning(f"GitHub API returned {response.status}")
                        return None
        except asyncio.TimeoutError:
            self.logger.warning("GitHub API timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching Copilot quota from GitHub: {e}")
            return None
    
    async def get_quota(self) -> Optional[QuotaInfo]:
        """Fetch quota from CLI first, then fallback to GitHub API"""
        # Try CLI first (faster, doesn't require token)
        quota = await self.get_quota_from_cli()
        if quota:
            return quota
        
        # Fallback to GitHub API
        quota = await self.get_quota_from_github_api()
        if quota:
            return quota
        
        return None
    
    async def get_pessimistic_quota(self) -> QuotaInfo:
        """Return pessimistic quota when both methods fail"""
        return QuotaInfo(
            provider="copilot",
            account_id="unknown",
            tokens_remaining=1875,  # Assume 10% remaining (pessimistic)
            tokens_limit=18750
        )


class AntigravityQuotaTracker:
    """
    Antigravity quota tracker (no external API)
    
    Tracks quota per account via local state.
    Each account has ~500K tokens/week.
    """
    
    def __init__(self):
        self.logger = logger.getChild("AntigravityQuotaTracker")
        # Per-account quota state (would be persisted in Redis in production)
        self.account_quotas: Dict[str, QuotaInfo] = {}
        self.reset_day = 7  # Sunday (0=Monday)
        self.reset_hour = 0  # Midnight UTC
    
    def update_quota_usage(self, account_id: str, tokens_used: int) -> None:
        """Update quota after request"""
        if account_id not in self.account_quotas:
            # Initialize new account
            self.account_quotas[account_id] = QuotaInfo(
                provider="antigravity",
                account_id=account_id,
                tokens_remaining=500000,
                tokens_limit=500000
            )
        
        quota = self.account_quotas[account_id]
        quota.tokens_remaining = max(0, quota.tokens_remaining - tokens_used)
        quota.updated_at = datetime.utcnow()
    
    def get_quota(self, account_id: str) -> QuotaInfo:
        """Get current quota for account"""
        if account_id not in self.account_quotas:
            # Return fresh quota for new account
            return QuotaInfo(
                provider="antigravity",
                account_id=account_id,
                tokens_remaining=500000,
                tokens_limit=500000
            )
        
        quota = self.account_quotas[account_id]
        # Recalculate status (in case it changed)
        quota.__post_init__()
        return quota
    
    def check_reset(self) -> bool:
        """
        Check if Sunday reset happened
        
        Returns:
            True if it's Sunday and quotas should reset
        """
        now = datetime.utcnow()
        if now.weekday() == self.reset_day and now.hour == self.reset_hour:
            # Reset all accounts
            for account_id in self.account_quotas:
                self.account_quotas[account_id].tokens_remaining = 500000
                self.account_quotas[account_id].updated_at = datetime.utcnow()
            
            self.logger.info(f"Antigravity quotas reset at {now}")
            return True
        
        return False


class QuotaCache:
    """
    Quota caching layer
    
    Caches quota info with TTL to avoid hammering APIs.
    Gracefully falls back to pessimistic estimates on failure.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache
        
        Args:
            ttl_seconds: Time to live for cached quota info (default 5 min)
        """
        self.ttl = ttl_seconds
        self.cache: Dict[str, QuotaInfo] = {}
        self.logger = logger.getChild("QuotaCache")
        
        # Initialize clients
        self.gemini_client = GeminiQuotaClient()
        self.copilot_client = CopilotQuotaClient()
        self.antigravity_tracker = AntigravityQuotaTracker()
    
    async def get_quota(
        self,
        provider: str,
        account_id: str,
        force_refresh: bool = False
    ) -> QuotaInfo:
        """
        Get quota for provider/account
        
        Returns cached quota if available and fresh, otherwise fetches new.
        Falls back to pessimistic estimate if fetch fails.
        
        Args:
            provider: Provider name ("gemini", "copilot", "antigravity")
            account_id: Account identifier
            force_refresh: Skip cache, always fetch fresh
        
        Returns:
            QuotaInfo with current/estimated quota
        """
        cache_key = f"{provider}:{account_id}"
        
        # Check cache first
        if not force_refresh and cache_key in self.cache:
            cached = self.cache[cache_key]
            if not cached.is_stale(self.ttl):
                self.logger.debug(f"Cache hit: {cache_key} ({cached.percent_used:.1f}% used)")
                return cached
        
        # Fetch fresh quota
        self.logger.debug(f"Cache miss: {cache_key}, fetching fresh quota")
        
        if provider == "gemini":
            quota = await self.gemini_client.get_quota()
            if not quota:
                quota = await self.gemini_client.get_pessimistic_quota()
        
        elif provider == "copilot":
            quota = await self.copilot_client.get_quota()
            if not quota:
                quota = await self.copilot_client.get_pessimistic_quota()
        
        elif provider == "antigravity":
            quota = self.antigravity_tracker.get_quota(account_id)
        
        else:
            self.logger.error(f"Unknown provider: {provider}")
            quota = QuotaInfo(
                provider=provider,
                account_id=account_id,
                tokens_remaining=0,
                tokens_limit=1
            )
        
        # Cache result
        self.cache[cache_key] = quota
        self.logger.info(f"Quota cached: {cache_key} ({quota.percent_used:.1f}% used)")
        
        return quota
    
    def clear_cache(self, provider: Optional[str] = None) -> None:
        """
        Clear cache
        
        Args:
            provider: If specified, only clear cache for this provider
        """
        if provider:
            keys_to_delete = [k for k in self.cache if k.startswith(f"{provider}:")]
            for key in keys_to_delete:
                del self.cache[key]
            self.logger.info(f"Cleared {len(keys_to_delete)} cache entries for {provider}")
        else:
            self.cache.clear()
            self.logger.info("Cleared all quota cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_entries": len(self.cache),
            "cache_size_bytes": sum(len(str(v)) for v in self.cache.values()),
            "ttl_seconds": self.ttl
        }


# Global cache instance
_quota_cache: Optional[QuotaCache] = None


def get_quota_cache() -> QuotaCache:
    """Get or create global quota cache"""
    global _quota_cache
    if _quota_cache is None:
        _quota_cache = QuotaCache()
    return _quota_cache


async def check_provider_quota(
    provider: str,
    account_id: str,
    threshold_percent: float = 95.0
) -> bool:
    """
    Check if provider account has available quota
    
    Args:
        provider: Provider name
        account_id: Account identifier
        threshold_percent: Quota threshold for fallback (default 95%)
    
    Returns:
        True if quota available (below threshold), False if should fallback
    """
    cache = get_quota_cache()
    quota = await cache.get_quota(provider, account_id)
    return not quota.should_fallback(threshold_percent)


async def get_provider_quota_status(
    provider: str,
    account_id: str
) -> QuotaStatus:
    """
    Get quota status for provider account
    
    Args:
        provider: Provider name
        account_id: Account identifier
    
    Returns:
        QuotaStatus enum value
    """
    cache = get_quota_cache()
    quota = await cache.get_quota(provider, account_id)
    return quota.status


# For Antigravity usage tracking
def record_antigravity_usage(account_id: str, tokens_used: int) -> None:
    """Record token usage for Antigravity account"""
    cache = get_quota_cache()
    cache.antigravity_tracker.update_quota_usage(account_id, tokens_used)
