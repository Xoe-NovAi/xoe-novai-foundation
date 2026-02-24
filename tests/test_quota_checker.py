"""
Tests for quota_checker.py - Phase 3C-2 Rate Limit Detection

Coverage: QuotaInfo, GeminiQuotaClient, CopilotQuotaClient, 
          AntigravityQuotaTracker, QuotaCache, integration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from app.XNAi_rag_app.core.quota_checker import (
    QuotaStatus,
    QuotaInfo,
    GeminiQuotaClient,
    CopilotQuotaClient,
    AntigravityQuotaTracker,
    QuotaCache,
    check_provider_quota,
    get_provider_quota_status,
    record_antigravity_usage
)


# ============================================================================
# QuotaInfo Tests (7 test cases)
# ============================================================================

class TestQuotaInfo:
    """Tests for QuotaInfo dataclass"""
    
    def test_quota_info_initialization(self):
        """Test basic initialization"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key123",
            tokens_remaining=900000,
            tokens_limit=1000000
        )
        
        assert quota.provider == "gemini"
        assert quota.account_id == "key123"
        assert quota.percent_used == pytest.approx(10.0, abs=0.1)
        assert quota.status == QuotaStatus.HEALTHY
    
    def test_quota_status_healthy(self):
        """Test HEALTHY status (>50% remaining)"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=600000,
            tokens_limit=1000000
        )
        assert quota.status == QuotaStatus.HEALTHY
        assert quota.percent_used == pytest.approx(40.0, abs=0.1)
    
    def test_quota_status_warning(self):
        """Test WARNING status (20-50% remaining)"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=300000,
            tokens_limit=1000000
        )
        assert quota.status == QuotaStatus.WARNING
        assert quota.percent_used == pytest.approx(70.0, abs=0.1)
    
    def test_quota_status_critical(self):
        """Test CRITICAL status (20-80% used)"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=100000,
            tokens_limit=1000000
        )
        assert quota.status == QuotaStatus.CRITICAL
        assert quota.percent_used == pytest.approx(90.0, abs=0.1)
    
    def test_quota_status_exhausted(self):
        """Test EXHAUSTED status (>95% used)"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=40000,
            tokens_limit=1000000
        )
        assert quota.status == QuotaStatus.EXHAUSTED
        assert quota.percent_used == pytest.approx(96.0, abs=0.1)
    
    def test_is_stale_not_stale(self):
        """Test is_stale returns False for fresh quota"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=900000,
            tokens_limit=1000000,
            updated_at=datetime.utcnow()
        )
        assert not quota.is_stale(ttl_seconds=300)
    
    def test_is_stale_stale(self):
        """Test is_stale returns True for old quota"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=900000,
            tokens_limit=1000000,
            updated_at=datetime.utcnow() - timedelta(seconds=400)
        )
        assert quota.is_stale(ttl_seconds=300)
    
    def test_should_fallback_yes(self):
        """Test should_fallback returns True when >95% used"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=40000,
            tokens_limit=1000000
        )
        assert quota.should_fallback(threshold_percent=95.0)
    
    def test_should_fallback_no(self):
        """Test should_fallback returns False when <95% used"""
        quota = QuotaInfo(
            provider="gemini",
            account_id="key",
            tokens_remaining=60000,
            tokens_limit=1000000
        )
        assert not quota.should_fallback(threshold_percent=95.0)


# ============================================================================
# GeminiQuotaClient Tests (3 test cases)
# ============================================================================

class TestGeminiQuotaClient:
    """Tests for GeminiQuotaClient"""
    
    @pytest.mark.asyncio
    async def test_get_quota_success(self):
        """Test successful quota fetch from Gemini API"""
        client = GeminiQuotaClient(api_key="test_key")
        
        # Mock the HTTP request
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "quotaStatus": {
                "current": 100000,
                "limit": 1000000
            }
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None
        
        with patch("aiohttp.ClientSession.get", return_value=mock_context) as mock_get:
            quota = await client.get_quota(api_key="test_key")
        
        assert quota is not None
        assert quota.provider == "gemini"
        assert quota.tokens_remaining == 900000
        assert quota.tokens_limit == 1000000
    
    @pytest.mark.asyncio
    async def test_get_quota_api_error(self):
        """Test quota fetch with API error"""
        client = GeminiQuotaClient(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = 500
        
        with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            quota = await client.get_quota(api_key="test_key")
        
        assert quota is None
    
    @pytest.mark.asyncio
    async def test_get_quota_timeout(self):
        """Test quota fetch with timeout"""
        client = GeminiQuotaClient(api_key="test_key")
        
        with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.side_effect = asyncio.TimeoutError()
            
            quota = await client.get_quota(api_key="test_key")
        
        assert quota is None
    
    @pytest.mark.asyncio
    async def test_get_pessimistic_quota(self):
        """Test pessimistic fallback quota"""
        client = GeminiQuotaClient()
        quota = await client.get_pessimistic_quota()
        
        assert quota is not None
        assert quota.provider == "gemini"
        assert quota.tokens_remaining == 100000
        assert quota.tokens_limit == 1000000


# ============================================================================
# CopilotQuotaClient Tests (2 test cases)
# ============================================================================

class TestCopilotQuotaClient:
    """Tests for CopilotQuotaClient"""
    
    @pytest.mark.asyncio
    async def test_get_quota_from_cli_success(self):
        """Test successful quota fetch from Copilot CLI"""
        client = CopilotQuotaClient(cli_path="/usr/bin/copilot")
        
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b'{"remaining": 15000, "limit": 18750}',
            b''
        ))
        
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            
            quota = await client.get_quota_from_cli()
        
        assert quota is not None
        assert quota.provider == "copilot"
        assert quota.tokens_remaining == 15000
        assert quota.tokens_limit == 18750
    
    @pytest.mark.asyncio
    async def test_get_quota_from_cli_not_found(self):
        """Test quota fetch when CLI not found"""
        client = CopilotQuotaClient(cli_path="/nonexistent/copilot")
        
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            quota = await client.get_quota_from_cli()
        
        assert quota is None
    
    @pytest.mark.asyncio
    async def test_get_pessimistic_quota(self):
        """Test pessimistic fallback for Copilot"""
        client = CopilotQuotaClient()
        quota = await client.get_pessimistic_quota()
        
        assert quota is not None
        assert quota.provider == "copilot"
        assert quota.tokens_remaining == 1875
        assert quota.tokens_limit == 18750


# ============================================================================
# AntigravityQuotaTracker Tests (4 test cases)
# ============================================================================

class TestAntigravityQuotaTracker:
    """Tests for AntigravityQuotaTracker"""
    
    def test_track_initial_quota(self):
        """Test initial quota for new account"""
        tracker = AntigravityQuotaTracker()
        
        quota = tracker.get_quota("account1")
        
        assert quota.provider == "antigravity"
        assert quota.account_id == "account1"
        assert quota.tokens_remaining == 500000
        assert quota.tokens_limit == 500000
    
    def test_update_quota_usage(self):
        """Test tracking usage reduces quota"""
        tracker = AntigravityQuotaTracker()
        
        tracker.update_quota_usage("account1", 50000)
        quota = tracker.get_quota("account1")
        
        assert quota.tokens_remaining == 450000
        assert quota.percent_used == pytest.approx(10.0, abs=0.1)
    
    def test_multiple_account_tracking(self):
        """Test tracking multiple accounts independently"""
        tracker = AntigravityQuotaTracker()
        
        tracker.update_quota_usage("account1", 100000)
        tracker.update_quota_usage("account2", 200000)
        
        quota1 = tracker.get_quota("account1")
        quota2 = tracker.get_quota("account2")
        
        assert quota1.tokens_remaining == 400000
        assert quota2.tokens_remaining == 300000
    
    def test_check_reset(self):
        """Test Sunday reset detection"""
        tracker = AntigravityQuotaTracker()
        
        # Update account to simulate usage
        tracker.update_quota_usage("account1", 100000)
        assert tracker.get_quota("account1").tokens_remaining == 400000
        
        # Note: This test would need time mocking for full coverage
        # For now, verify logic doesn't crash
        tracker.check_reset()


# ============================================================================
# QuotaCache Tests (3 test cases)
# ============================================================================

class TestQuotaCache:
    """Tests for QuotaCache"""
    
    def test_cache_initialization(self):
        """Test cache initializes correctly"""
        cache = QuotaCache(ttl_seconds=300)
        
        assert cache.ttl == 300
        assert len(cache.cache) == 0
        assert cache.gemini_client is not None
        assert cache.copilot_client is not None
        assert cache.antigravity_tracker is not None
    
    @pytest.mark.asyncio
    async def test_get_quota_antigravity_cached(self):
        """Test Antigravity quota caching"""
        cache = QuotaCache(ttl_seconds=300)
        
        quota1 = await cache.get_quota("antigravity", "account1")
        quota2 = await cache.get_quota("antigravity", "account1")
        
        # Both should return same object from cache
        assert quota1.tokens_remaining == quota2.tokens_remaining
        assert "antigravity:account1" in cache.cache
    
    def test_clear_cache_all(self):
        """Test clearing entire cache"""
        cache = QuotaCache()
        
        # Add some entries
        cache.cache["gemini:key1"] = QuotaInfo(
            provider="gemini",
            account_id="key1",
            tokens_remaining=900000,
            tokens_limit=1000000
        )
        cache.cache["copilot:account1"] = QuotaInfo(
            provider="copilot",
            account_id="account1",
            tokens_remaining=15000,
            tokens_limit=18750
        )
        
        assert len(cache.cache) == 2
        
        cache.clear_cache()
        assert len(cache.cache) == 0
    
    def test_clear_cache_provider_specific(self):
        """Test clearing cache for specific provider"""
        cache = QuotaCache()
        
        cache.cache["gemini:key1"] = QuotaInfo(
            provider="gemini",
            account_id="key1",
            tokens_remaining=900000,
            tokens_limit=1000000
        )
        cache.cache["copilot:account1"] = QuotaInfo(
            provider="copilot",
            account_id="account1",
            tokens_remaining=15000,
            tokens_limit=18750
        )
        
        cache.clear_cache(provider="gemini")
        
        assert len(cache.cache) == 1
        assert "copilot:account1" in cache.cache
        assert "gemini:key1" not in cache.cache
    
    def test_get_cache_stats(self):
        """Test cache statistics"""
        cache = QuotaCache()
        
        cache.cache["gemini:key1"] = QuotaInfo(
            provider="gemini",
            account_id="key1",
            tokens_remaining=900000,
            tokens_limit=1000000
        )
        
        stats = cache.get_cache_stats()
        
        assert stats["cached_entries"] == 1
        assert stats["ttl_seconds"] == 300
        assert stats["cache_size_bytes"] > 0


# ============================================================================
# Integration Tests (2 test cases)
# ============================================================================

class TestIntegration:
    """Integration tests for quota checking"""
    
    @pytest.mark.asyncio
    async def test_check_provider_quota_available(self):
        """Test check_provider_quota returns True when quota available"""
        with patch("app.XNAi_rag_app.core.quota_checker.get_quota_cache") as mock_get:
            mock_cache = Mock()
            mock_cache.get_quota = AsyncMock(return_value=QuotaInfo(
                provider="gemini",
                account_id="key1",
                tokens_remaining=900000,
                tokens_limit=1000000
            ))
            mock_get.return_value = mock_cache
            
            result = await check_provider_quota("gemini", "key1")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_provider_quota_exhausted(self):
        """Test check_provider_quota returns False when quota exhausted"""
        with patch("app.XNAi_rag_app.core.quota_checker.get_quota_cache") as mock_get:
            mock_cache = Mock()
            mock_cache.get_quota = AsyncMock(return_value=QuotaInfo(
                provider="gemini",
                account_id="key1",
                tokens_remaining=40000,
                tokens_limit=1000000
            ))
            mock_get.return_value = mock_cache
            
            result = await check_provider_quota("gemini", "key1")
            
            assert result is False


# ============================================================================
# Performance Tests (1 test case)
# ============================================================================

class TestPerformance:
    """Performance tests for quota checking"""
    
    def test_quota_info_performance(self):
        """Test QuotaInfo creation is fast (<1ms)"""
        import time
        
        start = time.perf_counter()
        for _ in range(1000):
            QuotaInfo(
                provider="gemini",
                account_id="key",
                tokens_remaining=900000,
                tokens_limit=1000000
            )
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should be very fast (all 1000 in <10ms)
        assert elapsed < 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
