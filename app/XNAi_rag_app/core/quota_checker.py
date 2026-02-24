"""
Rate Limit Detection & Quota Management System
Xoe-NovAi Foundation Stack - Phase 3C Integration

Provides real-time quota checking for:
- Gemini (Google API v1beta quotaStatus)
- Copilot (GitHub API + CLI fallback)
- Antigravity (cached, per-account tracking)

Features:
- 5-10 minute caching (configurable TTL)
- Graceful degradation (pessimistic on API failure)
- Pre-dispatch quota validation
- Fallback trigger at 80%+ threshold
- Full audit trail logging
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)


class QuotaStatus(Enum):
    """Quota status indicators"""
    HEALTHY = "healthy"          # < 50% used
    WARNING = "warning"          # 50-80% used
    CRITICAL = "critical"        # 80-95% used
    EXHAUSTED = "exhausted"      # > 95% used


@dataclass
class QuotaInfo:
    """Quota information for a provider"""
    provider: str
    account: str
    tokens_remaining: int
    tokens_limit: int
    reset_time: Optional[datetime] = None
    cached_at: datetime = field(default_factory=datetime.now)
    cache_ttl: int = 300  # 5 minutes
    
    @property
    def tokens_used(self) -> int:
        return self.tokens_limit - self.tokens_remaining
    
    @property
    def quota_percent_used(self) -> float:
        """Calculate percentage of quota used"""
        if self.tokens_limit == 0:
            return 0.0
        return (self.tokens_used / self.tokens_limit) * 100.0
    
    @property
    def status(self) -> QuotaStatus:
        """Determine quota status"""
        percent = self.quota_percent_used
        if percent >= 95:
            return QuotaStatus.EXHAUSTED
        elif percent >= 80:
            return QuotaStatus.CRITICAL
        elif percent >= 50:
            return QuotaStatus.WARNING
        else:
            return QuotaStatus.HEALTHY
    
    @property
    def is_cached(self) -> bool:
        """Check if cached data is still valid"""
        age = (datetime.now() - self.cached_at).total_seconds()
        return age < self.cache_ttl
    
    def __repr__(self) -> str:
        return (
            f"QuotaInfo({self.provider}/{self.account}: "
            f"{self.quota_percent_used:.1f}% used, "
            f"status={self.status.value})"
        )


class GeminiQuotaClient:
    """Gemini quota API client"""
    
    QUOTA_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/quotaStatus"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set, quota checks will use pessimistic values")
    
    async def get_quota(self) -> Optional[QuotaInfo]:
        """Fetch Gemini quota from API
        
        Returns:
            QuotaInfo with current quota status, or None on error
        """
        if not self.api_key:
            # Pessimistic fallback: assume 90% used
            logger.warning("Gemini API key not available, using pessimistic quota estimate")
            return QuotaInfo(
                provider="gemini",
                account="default",
                tokens_remaining=32000,  # Assume 90% of 320K daily limit
                tokens_limit=320000,
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"x-goog-api-key": self.api_key}
                async with session.get(
                    self.QUOTA_ENDPOINT,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"Gemini quota API returned {resp.status}")
                        return self._pessimistic_quota()
                    
                    data = await resp.json()
                    return self._parse_gemini_response(data)
        
        except asyncio.TimeoutError:
            logger.warning("Gemini quota API timeout, using pessimistic estimate")
            return self._pessimistic_quota()
        except Exception as e:
            logger.warning(f"Failed to fetch Gemini quota: {e}")
            return self._pessimistic_quota()
    
    def _parse_gemini_response(self, data: Dict[str, Any]) -> QuotaInfo:
        """Parse Gemini API response"""
        try:
            quota_status = data.get("quota_status", {})
            tokens_per_minute = quota_status.get("tokens_per_minute", {})
            
            limit = tokens_per_minute.get("limit", 32000)
            current = tokens_per_minute.get("current", 28500)
            remaining = limit - current
            
            reset_time = data.get("reset_time")
            if reset_time:
                reset_time = datetime.fromisoformat(reset_time)
            
            return QuotaInfo(
                provider="gemini",
                account="default",
                tokens_remaining=remaining,
                tokens_limit=limit,
                reset_time=reset_time,
            )
        except Exception as e:
            logger.warning(f"Failed to parse Gemini response: {e}")
            return self._pessimistic_quota()
    
    def _pessimistic_quota(self) -> QuotaInfo:
        """Return pessimistic quota estimate (assume 90% used)"""
        return QuotaInfo(
            provider="gemini",
            account="default",
            tokens_remaining=32000,  # 10% of 320K
            tokens_limit=320000,
        )


class CopilotQuotaClient:
    """Copilot quota detection via CLI and GitHub API"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
    
    async def get_quota(self) -> Optional[QuotaInfo]:
        """Fetch Copilot quota
        
        Tries methods in order:
        1. `copilot quota --json` (CLI, fastest)
        2. GitHub API endpoint (API, most accurate)
        3. Pessimistic fallback
        """
        # Try CLI method first
        quota = await self._get_quota_from_cli()
        if quota:
            return quota
        
        # Try GitHub API method
        quota = await self._get_quota_from_api()
        if quota:
            return quota
        
        # Fallback to pessimistic estimate
        logger.warning("Could not fetch Copilot quota, using pessimistic estimate")
        return self._pessimistic_quota()
    
    async def _get_quota_from_cli(self) -> Optional[QuotaInfo]:
        """Try to get quota from Copilot CLI"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["copilot", "quota", "--json"],
                capture_output=True,
                timeout=5,
            )
            
            if result.returncode != 0:
                logger.debug("Copilot CLI quota command failed")
                return None
            
            data = json.loads(result.stdout)
            
            # Parse Copilot CLI response
            remaining = data.get("remaining", 0)
            limit = data.get("limit", 18750)  # Default: 18.75K per week
            
            return QuotaInfo(
                provider="copilot",
                account="default",
                tokens_remaining=remaining,
                tokens_limit=limit,
            )
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            logger.debug("Failed to get Copilot quota from CLI")
            return None
        except Exception as e:
            logger.debug(f"Copilot CLI error: {e}")
            return None
    
    async def _get_quota_from_api(self) -> Optional[QuotaInfo]:
        """Try to get quota from GitHub API"""
        if not self.github_token:
            logger.debug("GitHub token not available for quota API")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                async with session.get(
                    "https://api.github.com/user/copilot/usage",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status != 200:
                        logger.debug(f"GitHub API returned {resp.status}")
                        return None
                    
                    data = await resp.json()
                    return self._parse_github_response(data)
        
        except asyncio.TimeoutError:
            logger.debug("GitHub API timeout")
            return None
        except Exception as e:
            logger.debug(f"GitHub API error: {e}")
            return None
    
    def _parse_github_response(self, data: Dict[str, Any]) -> QuotaInfo:
        """Parse GitHub API response"""
        try:
            usage = data.get("usage", {})
            
            # GitHub API returns usage, not remaining
            used = usage.get("tokens_used", 0)
            limit = usage.get("tokens_limit", 18750)
            remaining = limit - used
            
            return QuotaInfo(
                provider="copilot",
                account="default",
                tokens_remaining=max(0, remaining),
                tokens_limit=limit,
            )
        except Exception as e:
            logger.warning(f"Failed to parse GitHub response: {e}")
            return self._pessimistic_quota()
    
    def _pessimistic_quota(self) -> QuotaInfo:
        """Return pessimistic quota estimate (assume 80% used)"""
        return QuotaInfo(
            provider="copilot",
            account="default",
            tokens_remaining=3750,  # 20% of 18.75K
            tokens_limit=18750,
        )


class AntigravityQuotaTracker:
    """Track Antigravity account quotas (cached, per-account)"""
    
    def __init__(self):
        self.quotas: Dict[str, QuotaInfo] = {}
        self.update_count = 0
    
    def update_quota(self, account: str, tokens_used: int, tokens_limit: int = 500000):
        """Update quota for an account"""
        remaining = max(0, tokens_limit - tokens_used)
        self.quotas[account] = QuotaInfo(
            provider="antigravity",
            account=account,
            tokens_remaining=remaining,
            tokens_limit=tokens_limit,
        )
        self.update_count += 1
    
    def get_quota(self, account: str) -> Optional[QuotaInfo]:
        """Get cached quota for account"""
        return self.quotas.get(account)
    
    def get_all_quotas(self) -> Dict[str, QuotaInfo]:
        """Get all account quotas"""
        return self.quotas.copy()
    
    def get_healthiest_account(self) -> Optional[str]:
        """Find account with most remaining tokens"""
        if not self.quotas:
            return None
        
        return max(
            self.quotas.items(),
            key=lambda x: x[1].tokens_remaining,
        )[0]
    
    def get_accounts_below_threshold(self, percent_threshold: float = 80.0) -> list:
        """Get accounts above usage threshold (for fallback)"""
        return [
            account
            for account, quota in self.quotas.items()
            if quota.quota_percent_used >= percent_threshold
        ]


class QuotaCache:
    """Central cache for all provider quotas"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.gemini_client = GeminiQuotaClient()
        self.copilot_client = CopilotQuotaClient()
        self.antigravity_tracker = AntigravityQuotaTracker()
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, QuotaInfo] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
    
    async def get_quota(self, provider: str, account: str = "default") -> Optional[QuotaInfo]:
        """Get quota for provider (cached if valid)"""
        cache_key = f"{provider}/{account}"
        
        # Check cache first
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age = (datetime.now() - self.cache_timestamps[cache_key]).total_seconds()
            if age < self.ttl_seconds:
                logger.debug(f"Using cached quota for {cache_key}")
                return cached
        
        # Fetch fresh quota
        if provider == "gemini":
            quota = await self.gemini_client.get_quota()
        elif provider == "copilot":
            quota = await self.copilot_client.get_quota()
        elif provider == "antigravity":
            quota = self.antigravity_tracker.get_quota(account)
        else:
            logger.warning(f"Unknown provider: {provider}")
            return None
        
        if quota:
            self.cache[cache_key] = quota
            self.cache_timestamps[cache_key] = datetime.now()
        
        return quota
    
    def update_antigravity_quota(
        self, account: str, tokens_used: int, tokens_limit: int = 500000
    ):
        """Update Antigravity account quota after dispatch"""
        self.antigravity_tracker.update_quota(account, tokens_used, tokens_limit)
        
        # Update cache as well
        quota = self.antigravity_tracker.get_quota(account)
        if quota:
            cache_key = f"antigravity/{account}"
            self.cache[cache_key] = quota
            self.cache_timestamps[cache_key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached quotas"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Quota cache cleared")


# Global quota cache instance
_quota_cache_instance: Optional[QuotaCache] = None


def get_quota_cache() -> QuotaCache:
    """Get or create global quota cache instance"""
    global _quota_cache_instance
    if _quota_cache_instance is None:
        _quota_cache_instance = QuotaCache()
    return _quota_cache_instance


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test():
        cache = QuotaCache()
        
        # Test Gemini quota
        print("\n=== Gemini Quota ===")
        gemini = await cache.get_quota("gemini")
        if gemini:
            print(f"Status: {gemini.status.value}")
            print(f"Usage: {gemini.quota_percent_used:.1f}%")
            print(f"Remaining: {gemini.tokens_remaining}/{gemini.tokens_limit}")
        
        # Test Copilot quota
        print("\n=== Copilot Quota ===")
        copilot = await cache.get_quota("copilot")
        if copilot:
            print(f"Status: {copilot.status.value}")
            print(f"Usage: {copilot.quota_percent_used:.1f}%")
            print(f"Remaining: {copilot.tokens_remaining}/{copilot.tokens_limit}")
        
        # Test Antigravity quota
        print("\n=== Antigravity Quota ===")
        cache.update_antigravity_quota("antigravity-01", 450000)  # 90% used
        antigravity = await cache.get_quota("antigravity", "antigravity-01")
        if antigravity:
            print(f"Status: {antigravity.status.value}")
            print(f"Usage: {antigravity.quota_percent_used:.1f}%")
            print(f"Remaining: {antigravity.tokens_remaining}/{antigravity.tokens_limit}")
    
    asyncio.run(test())
