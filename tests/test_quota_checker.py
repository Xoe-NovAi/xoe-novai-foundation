"""
Unit Tests for Quota Checker System
Tests all quota clients and cache functionality
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.XNAi_rag_app.core.quota_checker import (
    QuotaStatus,
    QuotaInfo,
    GeminiQuotaClient,
    CopilotQuotaClient,
    AntigravityQuotaTracker,
    QuotaCache,
    get_quota_cache,
)


class TestQuotaInfo:
    """Tests for QuotaInfo dataclass"""
    
    def test_quota_percent_calculation(self):
        """Test quota percentage calculation"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=50000,
            tokens_limit=100000,
        )
        assert quota.quota_percent_used == 50.0
        assert quota.tokens_used == 50000
    
    def test_quota_status_healthy(self):
        """Test healthy quota status"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=60000,
            tokens_limit=100000,  # 40% used
        )
        assert quota.status == QuotaStatus.HEALTHY
    
    def test_quota_status_warning(self):
        """Test warning quota status"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=30000,
            tokens_limit=100000,  # 70% used
        )
        assert quota.status == QuotaStatus.WARNING
    
    def test_quota_status_critical(self):
        """Test critical quota status"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=15000,
            tokens_limit=100000,  # 85% used
        )
        assert quota.status == QuotaStatus.CRITICAL
    
    def test_quota_status_exhausted(self):
        """Test exhausted quota status"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=2000,
            tokens_limit=100000,  # 98% used
        )
        assert quota.status == QuotaStatus.EXHAUSTED
    
    def test_cache_validity_fresh(self):
        """Test cache validity - fresh data"""
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=50000,
            tokens_limit=100000,
            cache_ttl=300,  # 5 minutes
        )
        assert quota.is_cached is True
    
    def test_cache_validity_stale(self):
        """Test cache validity - stale data"""
        old_time = datetime.now() - timedelta(seconds=400)
        quota = QuotaInfo(
            provider="test",
            account="account1",
            tokens_remaining=50000,
            tokens_limit=100000,
            cached_at=old_time,
            cache_ttl=300,
        )
        assert quota.is_cached is False


class TestGeminiQuotaClient:
    """Tests for Gemini quota client"""
    
    def test_gemini_client_no_api_key(self):
        """Test Gemini client with no API key"""
        with patch.dict("os.environ", {}, clear=True):
            client = GeminiQuotaClient()
            assert client.api_key is None
    
    @pytest.mark.asyncio
    async def test_gemini_client_api_failure(self):
        """Test Gemini client API failure handling"""
        client = GeminiQuotaClient(api_key="invalid_key")
        quota = await client.get_quota()
        
        assert quota is not None
        assert quota.provider == "gemini"
        assert quota.status == QuotaStatus.CRITICAL  # Pessimistic
    
    @pytest.mark.asyncio
    async def test_gemini_client_no_key_pessimistic(self):
        """Test Gemini client without API key uses pessimistic estimate"""
        with patch.dict("os.environ", {}, clear=True):
            client = GeminiQuotaClient()
            quota = await client.get_quota()
            
            assert quota is not None
            assert quota.quota_percent_used == 90.0  # Pessimistic
    
    def test_gemini_parse_response(self):
        """Test parsing valid Gemini API response"""
        client = GeminiQuotaClient(api_key="test_key")
        # "current" in Gemini API = tokens used (not remaining)
        # limit=320000, current=40000 used → remaining=280000
        response = {
            "quota_status": {
                "tokens_per_minute": {
                    "limit": 320000,
                    "current": 40000,  # Only 40K used, 280K remaining
                }
            },
            "reset_time": "2026-02-25T00:00:00Z",
        }
        
        quota = client._parse_gemini_response(response)
        assert quota.tokens_remaining == 280000
        assert quota.tokens_limit == 320000
        assert quota.tokens_used == 40000
        # 40000 used / 320000 limit = 12.5% used = HEALTHY
        assert quota.quota_percent_used == 12.5
        assert quota.status == QuotaStatus.HEALTHY


class TestCopilotQuotaClient:
    """Tests for Copilot quota client"""
    
    @pytest.mark.asyncio
    async def test_copilot_no_methods_available(self):
        """Test Copilot client fallback when no methods available"""
        client = CopilotQuotaClient()
        quota = await client.get_quota()
        
        assert quota is not None
        assert quota.provider == "copilot"
        assert quota.quota_percent_used == 80.0  # Pessimistic
    
    def test_copilot_parse_github_response(self):
        """Test parsing GitHub API response"""
        client = CopilotQuotaClient(github_token="test_token")
        response = {
            "usage": {
                "tokens_used": 10000,
                "tokens_limit": 18750,
            }
        }
        
        quota = client._parse_github_response(response)
        assert quota.tokens_remaining == 8750
        assert quota.tokens_limit == 18750
        assert quota.quota_percent_used == pytest.approx(53.3, rel=0.1)


class TestAntigravityQuotaTracker:
    """Tests for Antigravity quota tracking"""
    
    def test_update_and_get_quota(self):
        """Test updating and retrieving quota"""
        tracker = AntigravityQuotaTracker()
        tracker.update_quota("antigravity-01", 450000)  # 90% used
        
        quota = tracker.get_quota("antigravity-01")
        assert quota is not None
        assert quota.tokens_remaining == 50000
        assert quota.quota_percent_used == 90.0
    
    def test_get_all_quotas(self):
        """Test retrieving all quotas"""
        tracker = AntigravityQuotaTracker()
        tracker.update_quota("antigravity-01", 250000)  # 50% used
        tracker.update_quota("antigravity-02", 450000)  # 90% used
        
        all_quotas = tracker.get_all_quotas()
        assert len(all_quotas) == 2
        assert all_quotas["antigravity-01"].quota_percent_used == 50.0
        assert all_quotas["antigravity-02"].quota_percent_used == 90.0
    
    def test_get_healthiest_account(self):
        """Test finding healthiest account"""
        tracker = AntigravityQuotaTracker()
        tracker.update_quota("antigravity-01", 450000)  # 90% used
        tracker.update_quota("antigravity-02", 100000)  # 20% used
        tracker.update_quota("antigravity-03", 250000)  # 50% used
        
        healthiest = tracker.get_healthiest_account()
        assert healthiest == "antigravity-02"  # Has most remaining
    
    def test_get_accounts_below_threshold(self):
        """Test finding accounts above usage threshold"""
        tracker = AntigravityQuotaTracker()
        tracker.update_quota("antigravity-01", 450000)  # 90% used
        tracker.update_quota("antigravity-02", 100000)  # 20% used
        tracker.update_quota("antigravity-03", 400000)  # 80% used
        
        above_threshold = tracker.get_accounts_below_threshold(80.0)
        assert "antigravity-01" in above_threshold
        assert "antigravity-03" in above_threshold
        assert "antigravity-02" not in above_threshold


class TestQuotaCache:
    """Tests for quota cache"""
    
    @pytest.mark.asyncio
    async def test_cache_antigravity_quota(self):
        """Test caching Antigravity quota"""
        cache = QuotaCache(ttl_seconds=300)
        cache.update_antigravity_quota("antigravity-01", 250000)
        
        quota = await cache.get_quota("antigravity", "antigravity-01")
        assert quota is not None
        assert quota.quota_percent_used == 50.0
    
    @pytest.mark.asyncio
    async def test_cache_ttl_respected(self):
        """Test that cache TTL is respected"""
        cache = QuotaCache(ttl_seconds=1)
        cache.update_antigravity_quota("antigravity-01", 250000)
        
        # First call should use cache
        quota1 = await cache.get_quota("antigravity", "antigravity-01")
        assert quota1 is not None
        
        # Wait for cache to expire
        await asyncio.sleep(1.1)
        
        # Second call should attempt fresh fetch
        quota2 = await cache.get_quota("antigravity", "antigravity-01")
        # Should still work (Antigravity tracker is persistent)
        assert quota2 is not None
    
    def test_clear_cache(self):
        """Test clearing cache"""
        cache = QuotaCache()
        cache.update_antigravity_quota("antigravity-01", 250000)
        
        assert len(cache.cache) > 0
        cache.clear_cache()
        assert len(cache.cache) == 0


class TestIntegration:
    """Integration tests for quota system"""
    
    @pytest.mark.asyncio
    async def test_full_quota_check_flow(self):
        """Test full quota checking flow"""
        cache = QuotaCache()
        
        # Simulate multiple providers
        cache.update_antigravity_quota("antigravity-01", 450000)  # 90%
        cache.update_antigravity_quota("antigravity-02", 100000)  # 20%
        
        # Get quotas
        ag1 = await cache.get_quota("antigravity", "antigravity-01")
        ag2 = await cache.get_quota("antigravity", "antigravity-02")
        copilot = await cache.get_quota("copilot")
        
        assert ag1.status == QuotaStatus.CRITICAL
        assert ag2.status == QuotaStatus.HEALTHY
        assert copilot.status in [QuotaStatus.CRITICAL, QuotaStatus.WARNING]
    
    @pytest.mark.asyncio
    async def test_quota_decision_making(self):
        """Test using quota for dispatch decisions"""
        cache = QuotaCache()
        
        # Setup quotas
        cache.update_antigravity_quota("antigravity-01", 450000)  # 90% - critical
        cache.update_antigravity_quota("antigravity-02", 100000)  # 20% - healthy
        
        # Decision: use healthiest account
        ag1 = await cache.get_quota("antigravity", "antigravity-01")
        ag2 = await cache.get_quota("antigravity", "antigravity-02")
        
        if ag1.status == QuotaStatus.CRITICAL and ag2.status == QuotaStatus.HEALTHY:
            selected_account = "antigravity-02"
        else:
            selected_account = "antigravity-01"
        
        assert selected_account == "antigravity-02"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
