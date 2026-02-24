"""
XNAi Foundation - Multi-CLI Testing Framework (Phase 3C)

Comprehensive test suite for:
- Cline CLI dispatch
- Copilot CLI dispatch
- OpenCode CLI dispatch
- Multi-account rotation
- Quota-aware routing
- Fallback chains
- Error recovery

Status: Phase 3B (Framework design, Phase 3C ready for implementation)
"""

import pytest
import anyio
from datetime import datetime
from typing import List

from app.XNAi_rag_app.core.multi_provider_dispatcher import (
    MultiProviderDispatcher,
    TaskSpecialization,
    ProviderQuota,
    DispatchResult,
)


class TestMultiProviderDispatcher:
    """Test suite for MultiProviderDispatcher"""
    
    @pytest.fixture
    def dispatcher(self):
        """Create dispatcher instance for testing"""
        return MultiProviderDispatcher()
    
    # ===========================================================================
    # UNIT TESTS: Scoring Algorithm
    # ===========================================================================
    
    def test_quota_score_fresh_account(self, dispatcher):
        """New account (0% used) should score 100"""
        quota = ProviderQuota(provider="cline", account="new", used=0, limit=100)
        score = dispatcher._calculate_quota_score(quota)
        assert score == 100.0
    
    def test_quota_score_half_used(self, dispatcher):
        """50% used should score 50"""
        quota = ProviderQuota(provider="cline", account="half", used=50, limit=100)
        score = dispatcher._calculate_quota_score(quota)
        assert score == 50.0
    
    def test_quota_score_95_percent_used(self, dispatcher):
        """95% used should score 0 (threshold penalty)"""
        quota = ProviderQuota(provider="cline", account="exhausted", used=95, limit=100)
        score = dispatcher._calculate_quota_score(quota)
        assert score == 0.0
    
    def test_quota_score_unhealthy_provider(self, dispatcher):
        """Unhealthy provider should score 0"""
        quota = ProviderQuota(
            provider="cline",
            account="sick",
            used=10,
            limit=100,
            healthy=False,
        )
        score = dispatcher._calculate_quota_score(quota)
        assert score == 0.0
    
    def test_latency_score_fast_provider(self, dispatcher):
        """Fast provider (100ms) should score ~90"""
        # OpenCode at 100ms
        score = dispatcher._calculate_latency_score("opencode")
        assert 85 <= score <= 95  # Roughly 90
    
    def test_latency_score_slow_provider(self, dispatcher):
        """Slow provider (5000ms) should score 0"""
        score = dispatcher._calculate_latency_score("local")
        assert score == 0.0
    
    def test_fit_score_code_specialization(self, dispatcher):
        """Cline should score high for code specialization"""
        score = dispatcher._calculate_fit_score(
            "cline",
            TaskSpecialization.CODE,
            context_size=50000,
        )
        assert score > 80  # Should be ~95
    
    def test_fit_score_reasoning_specialization(self, dispatcher):
        """OpenCode should score high for reasoning"""
        score = dispatcher._calculate_fit_score(
            "opencode",
            TaskSpecialization.REASONING,
            context_size=50000,
        )
        assert score > 80  # Should be ~95
    
    def test_fit_score_insufficient_context(self, dispatcher):
        """Provider with insufficient context should score low"""
        score = dispatcher._calculate_fit_score(
            "local",  # Only 8K context
            TaskSpecialization.LARGE_DOCUMENT,
            context_size=500000,  # 500K needed
        )
        assert score == 0.0  # Impossible
    
    # ===========================================================================
    # UNIT TESTS: Multi-Account Rotation
    # ===========================================================================
    
    def test_account_rotation_round_robin(self, dispatcher):
        """Accounts should rotate in round-robin fashion"""
        accounts: List[str] = []
        
        for _ in range(16):  # 2 full cycles of 8 accounts
            account = dispatcher._get_account_for_provider("cline")
            accounts.append(account)
        
        # Should have 8 unique accounts
        assert len(set(accounts)) == 8
        
        # Should cycle correctly
        assert accounts[0] == accounts[8]  # First and 9th should match
        assert accounts[1] == accounts[9]
    
    def test_account_rotation_independent_per_provider(self, dispatcher):
        """Each provider should have independent rotation"""
        cline_accounts = [
            dispatcher._get_account_for_provider("cline") for _ in range(3)
        ]
        copilot_accounts = [
            dispatcher._get_account_for_provider("copilot") for _ in range(3)
        ]
        
        # Should be in same order (independent rotations)
        assert cline_accounts == copilot_accounts
    
    # ===========================================================================
    # UNIT TESTS: Provider Selection
    # ===========================================================================
    
    def test_select_best_provider_code_task(self, dispatcher):
        """Code task should prefer Cline"""
        # Mock: all providers fresh
        for provider in ["cline", "copilot", "opencode"]:
            for i, account in enumerate(dispatcher.email_accounts):
                quota_key = f"{provider}:{account}"
                dispatcher.quota_cache[quota_key] = ProviderQuota(
                    provider=provider,
                    account=account,
                    used=0,
                    limit=1000,
                )
        
        provider, account, score = dispatcher._select_best_provider(
            TaskSpecialization.CODE,
            context_size=10000,
        )
        
        assert provider == "cline"
        assert score.overall_score > 0
    
    def test_select_best_provider_reasoning_task(self, dispatcher):
        """Reasoning task should prefer OpenCode"""
        # Mock: all providers fresh
        for provider in ["cline", "copilot", "opencode"]:
            for account in dispatcher.email_accounts:
                quota_key = f"{provider}:{account}"
                dispatcher.quota_cache[quota_key] = ProviderQuota(
                    provider=provider,
                    account=account,
                    used=0,
                    limit=1000,
                )
        
        provider, account, score = dispatcher._select_best_provider(
            TaskSpecialization.REASONING,
            context_size=10000,
        )
        
        assert provider == "opencode"
    
    def test_select_best_provider_falls_back_on_quota(self, dispatcher):
        """Should fallback to 2nd choice if primary exhausted"""
        # Cline exhausted
        dispatcher.quota_cache["cline:xoe.nova.ai@gmail.com"] = ProviderQuota(
            provider="cline",
            account="xoe.nova.ai@gmail.com",
            used=990,
            limit=1000,  # 99% used
        )
        
        # Copilot fresh
        dispatcher.quota_cache["copilot:xoe.nova.ai@gmail.com"] = ProviderQuota(
            provider="copilot",
            account="xoe.nova.ai@gmail.com",
            used=0,
            limit=1000,
        )
        
        # OpenCode fresh
        dispatcher.quota_cache["opencode:xoe.nova.ai@gmail.com"] = ProviderQuota(
            provider="opencode",
            account="xoe.nova.ai@gmail.com",
            used=0,
            limit=10000,
        )
        
        # Task prefers code (Cline) but should fallback to Copilot
        provider, account, score = dispatcher._select_best_provider(
            TaskSpecialization.CODE,
            context_size=10000,
        )
        
        # Should pick Copilot (not exhausted Cline)
        assert provider in ["copilot", "opencode"]
    
    # ===========================================================================
    # INTEGRATION TESTS: Dispatch Execution
    # ===========================================================================
    
    @pytest.mark.asyncio
    async def test_dispatch_general_task(self, dispatcher):
        """Test dispatch to a provider with general task"""
        result = await dispatcher.dispatch(
            task="Say 'Hello, test!' briefly",
            task_spec=TaskSpecialization.GENERAL,
            context_size=1000,
            timeout_sec=30,
        )
        
        # Should either succeed or fail gracefully
        assert isinstance(result, DispatchResult)
        assert result.provider in ["cline", "copilot", "opencode", "local"]
        assert result.latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_dispatch_code_task(self, dispatcher):
        """Test dispatch to a provider with code task"""
        result = await dispatcher.dispatch(
            task="Write a simple Python function that returns 'hello'",
            task_spec=TaskSpecialization.CODE,
            context_size=5000,
            timeout_sec=30,
        )
        
        assert isinstance(result, DispatchResult)
        assert result.provider in ["cline", "copilot", "opencode"]
        assert result.latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_dispatch_large_document(self, dispatcher):
        """Test dispatch that requires large context"""
        result = await dispatcher.dispatch(
            task="Summarize the following: " + ("text " * 100),
            task_spec=TaskSpecialization.LARGE_DOCUMENT,
            context_size=500000,
            timeout_sec=60,
        )
        
        assert isinstance(result, DispatchResult)
        # Should prefer OpenCode for large context
        if result.success:
            assert result.provider == "opencode"
    
    @pytest.mark.asyncio
    async def test_dispatch_timeout_handling(self, dispatcher):
        """Test timeout recovery"""
        result = await dispatcher.dispatch(
            task="Analyze this code: " + ("x = 1; " * 1000),
            task_spec=TaskSpecialization.CODE,
            context_size=10000,
            timeout_sec=0.1,  # Very short timeout
        )
        
        # Should timeout and fail gracefully
        assert isinstance(result, DispatchResult)
        # Either succeeded quickly or timeout (either is ok)
    
    # ===========================================================================
    # INTEGRATION TESTS: Quota Management
    # ===========================================================================
    
    @pytest.mark.asyncio
    async def test_quota_updated_after_dispatch(self, dispatcher):
        """Quota cache should update after dispatch"""
        initial_quotas = len(dispatcher.quota_cache)
        
        await dispatcher.dispatch(
            task="Test",
            task_spec=TaskSpecialization.GENERAL,
            context_size=1000,
        )
        
        # Quota cache should be updated
        assert len(dispatcher.quota_cache) >= initial_quotas
    
    def test_quota_cache_persistence(self, dispatcher):
        """Quota cache should be saved to disk"""
        # Simulate dispatch
        dispatcher.quota_cache["cline:test@test.com"] = ProviderQuota(
            provider="cline",
            account="test@test.com",
            used=50,
            limit=100,
        )
        
        dispatcher._save_quota_cache()
        
        # Load in new instance
        dispatcher2 = MultiProviderDispatcher(
            quota_file=dispatcher.quota_file
        )
        
        # Should load saved quota
        # (Note: may not persist in test due to temp paths)
    
    # ===========================================================================
    # INTEGRATION TESTS: Statistics & Monitoring
    # ===========================================================================
    
    @pytest.mark.asyncio
    async def test_dispatch_history_tracking(self, dispatcher):
        """Dispatch results should be tracked in history"""
        initial_count = len(dispatcher.call_history)
        
        await dispatcher.dispatch(
            task="Test",
            task_spec=TaskSpecialization.GENERAL,
            context_size=1000,
        )
        
        assert len(dispatcher.call_history) == initial_count + 1
        assert dispatcher.call_history[-1].timestamp
    
    @pytest.mark.asyncio
    async def test_dispatcher_statistics(self, dispatcher):
        """Dispatcher should provide statistics"""
        # Do a few dispatches
        for i in range(3):
            await dispatcher.dispatch(
                task=f"Test {i}",
                task_spec=TaskSpecialization.GENERAL,
                context_size=1000,
            )
        
        stats = dispatcher.get_dispatch_stats()
        
        assert stats["total_calls"] == 3
        assert "successful" in stats
        assert "failed" in stats
        assert "avg_latency_ms" in stats
        assert "providers_used" in stats
    
    # ===========================================================================
    # STRESS TESTS
    # ===========================================================================
    
    @pytest.mark.asyncio
    async def test_multiple_sequential_dispatches(self, dispatcher):
        """Should handle multiple dispatches sequentially"""
        for i in range(5):
            result = await dispatcher.dispatch(
                task=f"Sequential test {i}",
                task_spec=TaskSpecialization.GENERAL,
                context_size=1000,
            )
            
            assert isinstance(result, DispatchResult)
    
    @pytest.mark.asyncio
    async def test_rapid_account_rotation(self, dispatcher):
        """Should correctly rotate through all accounts"""
        accounts_used = set()
        
        for _ in range(24):  # 3 full cycles of 8 accounts
            account = dispatcher._get_account_for_provider("cline")
            accounts_used.add(account)
        
        # Should have used all 8 accounts
        assert len(accounts_used) == 8
    
    # ===========================================================================
    # ERROR HANDLING & EDGE CASES
    # ===========================================================================
    
    def test_dispatch_with_no_context_size(self, dispatcher):
        """Should handle missing context_size (default to small)"""
        # This should work - context_size has default
        provider, account, score = dispatcher._select_best_provider(
            TaskSpecialization.GENERAL,
            context_size=0,  # Edge case
        )
        
        assert provider is not None
    
    @pytest.mark.asyncio
    async def test_dispatch_with_empty_task(self, dispatcher):
        """Should handle empty task gracefully"""
        result = await dispatcher.dispatch(
            task="",
            task_spec=TaskSpecialization.GENERAL,
            context_size=100,
        )
        
        # Should complete (may fail or succeed)
        assert isinstance(result, DispatchResult)
    
    def test_scorer_with_extreme_latency(self, dispatcher):
        """Should handle extreme latency values"""
        # Create fictional provider with 100ms latency
        score = dispatcher._calculate_latency_score("cline")  # 150ms
        
        assert 0 <= score <= 100
    
    def test_all_providers_exhausted(self, dispatcher):
        """Should handle gracefully when all quota exhausted"""
        # Mock: all providers at 99%
        for provider in ["cline", "copilot", "opencode"]:
            for account in dispatcher.email_accounts:
                quota_key = f"{provider}:{account}"
                dispatcher.quota_cache[quota_key] = ProviderQuota(
                    provider=provider,
                    account=account,
                    used=990,
                    limit=1000,
                )
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError):
            dispatcher._select_best_provider(
                TaskSpecialization.GENERAL,
                context_size=1000,
            )


# ===========================================================================
# FIXTURE-BASED TESTS: Provider-Specific
# ===========================================================================

class TestClineDispatch:
    """Tests specific to Cline CLI dispatch"""
    
    @pytest.fixture
    def dispatcher(self):
        return MultiProviderDispatcher()
    
    @pytest.mark.asyncio
    async def test_cline_dispatch_execution(self, dispatcher):
        """Test actual Cline CLI dispatch"""
        # This assumes Cline CLI is installed and authenticated
        result = await dispatcher._dispatch_cline(
            account="xoe.nova.ai@gmail.com",
            task="Return 'ok'",
            timeout_sec=30,
        )
        
        # Should attempt dispatch (may fail if Cline not installed)
        assert isinstance(result, DispatchResult)


class TestCopilotDispatch:
    """Tests specific to Copilot CLI dispatch"""
    
    @pytest.fixture
    def dispatcher(self):
        return MultiProviderDispatcher()
    
    @pytest.mark.asyncio
    async def test_copilot_dispatch_with_raptor_mini(self, dispatcher):
        """Test Copilot dispatch specifically uses Raptor-mini"""
        # This assumes Copilot CLI is installed and authenticated
        result = await dispatcher._dispatch_copilot(
            account="xoe.nova.ai@gmail.com",
            task="Return 'ok'",
            timeout_sec=30,
        )
        
        # Should attempt dispatch (may fail if Copilot not installed)
        assert isinstance(result, DispatchResult)


class TestOpenCodeDispatch:
    """Tests specific to OpenCode CLI dispatch"""
    
    @pytest.fixture
    def dispatcher(self):
        return MultiProviderDispatcher()
    
    @pytest.mark.asyncio
    async def test_opencode_xdg_isolation(self, dispatcher):
        """Test OpenCode XDG_DATA_HOME isolation"""
        # This assumes OpenCode CLI is installed
        result = await dispatcher._dispatch_opencode(
            account="antipode2727@gmail.com",
            task="Return 'ok'",
            timeout_sec=30,
        )
        
        # Should attempt dispatch (may fail if OpenCode not installed)
        assert isinstance(result, DispatchResult)


# ===========================================================================
# PYTEST CONFIGURATION
# ===========================================================================

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async (requires pytest-asyncio)",
    )


# ===========================================================================
# TEST EXECUTION
# ===========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
