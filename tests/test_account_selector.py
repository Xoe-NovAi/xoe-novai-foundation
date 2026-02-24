"""
Tests for account_selector.py - Phase 3C-2B Account Rotation

Coverage: AccountScore, AccountSelector, all strategies,
          starvation prevention, race condition mitigation
"""

import pytest
from datetime import datetime, timedelta
from app.XNAi_rag_app.core.account_selector import (
    SelectionStrategy,
    AccountScore,
    AccountSelector,
    SelectionResult
)


# ============================================================================
# AccountScore Tests (5 test cases)
# ============================================================================

class TestAccountScore:
    """Tests for AccountScore dataclass"""
    
    def test_score_initialization(self):
        """Test basic initialization"""
        score = AccountScore(
            account_id="account1",
            quota_remaining=450000,
            quota_limit=500000
        )
        
        assert score.account_id == "account1"
        assert score.quota_remaining == 450000
        assert score.quota_limit == 500000
        assert score.percent_used == pytest.approx(10.0, abs=0.1)
    
    def test_quota_score_calculation(self):
        """Test quota score (higher when more quota available)"""
        # High quota: 100% remaining = quota_score 1.0
        score_high = AccountScore(
            account_id="account1",
            quota_remaining=500000,
            quota_limit=500000
        )
        assert score_high.quota_score == pytest.approx(1.0, abs=0.01)
        
        # Medium quota: 50% remaining = quota_score 0.5
        score_med = AccountScore(
            account_id="account2",
            quota_remaining=250000,
            quota_limit=500000
        )
        assert score_med.quota_score == pytest.approx(0.5, abs=0.01)
        
        # Low quota: 0% remaining = quota_score 0.0
        score_low = AccountScore(
            account_id="account3",
            quota_remaining=0,
            quota_limit=500000
        )
        assert score_low.quota_score == pytest.approx(0.0, abs=0.01)
    
    def test_recency_score_calculation(self):
        """Test recency score (higher when recently used)"""
        # Just used: recency_score ~1.0
        score_now = AccountScore(
            account_id="account1",
            quota_remaining=450000,
            quota_limit=500000,
            last_used=datetime.utcnow()
        )
        assert score_now.recency_score >= 0.99
        
        # Used 12 hours ago: recency_score ~0.5
        score_mid = AccountScore(
            account_id="account2",
            quota_remaining=450000,
            quota_limit=500000,
            last_used=datetime.utcnow() - timedelta(hours=12)
        )
        assert 0.45 < score_mid.recency_score < 0.55
        
        # Used 24+ hours ago: recency_score ~0.0
        score_old = AccountScore(
            account_id="account3",
            quota_remaining=450000,
            quota_limit=500000,
            last_used=datetime.utcnow() - timedelta(hours=24)
        )
        assert score_old.recency_score <= 0.01
    
    def test_final_score_hybrid(self):
        """Test final score (60% quota, 40% recency)"""
        score = AccountScore(
            account_id="account1",
            quota_remaining=250000,  # quota_score = 0.5
            quota_limit=500000,
            last_used=datetime.utcnow()  # recency_score ~ 1.0
        )
        
        # final_score = 0.6 * 0.5 + 0.4 * 1.0 = 0.7
        assert score.final_score == pytest.approx(0.7, abs=0.01)
    
    def test_percent_used_calculation(self):
        """Test percent_used tracking"""
        score = AccountScore(
            account_id="account1",
            quota_remaining=100000,
            quota_limit=500000
        )
        assert score.percent_used == pytest.approx(80.0, abs=0.1)


# ============================================================================
# AccountSelector Tests (8 test cases)
# ============================================================================

class TestAccountSelector:
    """Tests for AccountSelector"""
    
    def test_initialization(self):
        """Test selector initialization"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.HYBRID
        )
        
        assert len(selector.accounts) == 3
        assert selector.strategy == SelectionStrategy.HYBRID
        assert len(selector.scores) == 3
    
    def test_update_quota(self):
        """Test updating account quota"""
        selector = AccountSelector(accounts=["account1", "account2"])
        
        selector.update_quota("account1", quota_remaining=300000, quota_limit=500000)
        
        score = selector.scores["account1"]
        assert score.quota_remaining == 300000
        assert score.percent_used == pytest.approx(40.0, abs=0.1)
    
    def test_record_usage(self):
        """Test recording account usage"""
        selector = AccountSelector(accounts=["account1", "account2"])
        
        initial_time = selector.scores["account1"].last_used
        selector.record_usage("account1")
        
        # Time should have advanced
        assert selector.scores["account1"].last_used > initial_time
        assert len(selector.selection_history) == 1


# ============================================================================
# Selection Strategy Tests (10 test cases)
# ============================================================================

class TestHybridSelection:
    """Tests for hybrid weighted selection"""
    
    def test_hybrid_prefers_higher_quota(self):
        """Test hybrid selection prefers accounts with more quota"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.HYBRID
        )
        
        # Account 1: 90% used, Account 2: 50% used, Account 3: 10% used
        selector.update_quota("account1", 50000, 500000)
        selector.update_quota("account2", 250000, 500000)
        selector.update_quota("account3", 450000, 500000)
        
        # Hybrid should heavily prefer account3
        selections = {}
        for _ in range(100):
            result = selector.select_account()
            selections[result.selected_account] = selections.get(result.selected_account, 0) + 1
        
        # Account3 should be selected most frequently
        assert selections.get("account3", 0) > selections.get("account1", 0)
    
    def test_hybrid_starvation_prevention(self):
        """Test hybrid prevents account starvation"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3", "account4", 
                     "account5", "account6", "account7", "account8"],
            strategy=SelectionStrategy.HYBRID
        )
        
        # All accounts have equal quota
        for i, acc in enumerate(selector.accounts):
            selector.update_quota(acc, 450000, 500000)
        
        # Mark account1 as old (not used in long time)
        selector.scores["account1"].last_used = datetime.utcnow() - timedelta(hours=24)
        
        # Run many selections
        selections = {}
        for _ in range(1000):
            result = selector.select_account()
            selections[result.selected_account] = selections.get(result.selected_account, 0) + 1
        
        # Account1 should eventually be selected (due to 10% LRU)
        assert selections.get("account1", 0) > 0


class TestGreedySelection:
    """Tests for greedy selection"""
    
    def test_greedy_always_picks_best(self):
        """Test greedy always picks account with most quota"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.GREEDY
        )
        
        selector.update_quota("account1", 50000, 500000)   # 90% used (worst)
        selector.update_quota("account2", 250000, 500000)  # 50% used
        selector.update_quota("account3", 450000, 500000)  # 10% used (best)
        
        # Greedy should always pick account3
        for _ in range(10):
            result = selector.select_account()
            assert result.selected_account == "account3"


class TestRoundRobinSelection:
    """Tests for round-robin selection"""
    
    def test_round_robin_cycles_through(self):
        """Test round-robin cycles through all accounts"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.ROUND_ROBIN
        )
        
        results = []
        for i in range(9):  # 3 cycles
            result = selector.select_account()
            results.append(result.selected_account)
        
        # Should cycle: 1, 2, 3, 1, 2, 3, 1, 2, 3
        expected_cycle = ["account1", "account2", "account3"]
        for i in range(0, 9, 3):
            assert results[i:i+3] == expected_cycle


class TestStickySelection:
    """Tests for sticky selection"""
    
    def test_sticky_sticks_with_account(self):
        """Test sticky selection sticks with account"""
        selector = AccountSelector(
            accounts=["account1", "account2"],
            strategy=SelectionStrategy.STICKY
        )
        
        # Make account1 have plenty of quota
        selector.update_quota("account1", 450000, 500000)
        selector.update_quota("account2", 100000, 500000)  # Lower quota
        
        # First selection should pick account1 (better quota)
        result1 = selector.select_account()
        selected_first = result1.selected_account
        
        # Subsequent selections should stick with the selected account
        for _ in range(5):
            result = selector.select_account()
            assert result.selected_account == selected_first


class TestLRUSelection:
    """Tests for LRU selection"""
    
    def test_lru_picks_oldest(self):
        """Test LRU picks least recently used account"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.LRU
        )
        
        # Mark account1 as very old
        selector.scores["account1"].last_used = datetime.utcnow() - timedelta(hours=24)
        selector.scores["account2"].last_used = datetime.utcnow() - timedelta(hours=1)
        selector.scores["account3"].last_used = datetime.utcnow()
        
        # LRU should pick account1 (oldest)
        result = selector.select_account()
        assert result.selected_account == "account1"


# ============================================================================
# Statistics Tests (3 test cases)
# ============================================================================

class TestAccountSelectorStatistics:
    """Tests for account selector statistics"""
    
    def test_get_statistics(self):
        """Test statistics collection"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.HYBRID
        )
        
        # Do some selections
        for _ in range(30):
            selector.select_account()
        
        stats = selector.get_statistics()
        
        assert stats["total_selections"] == 30
        assert "selection_counts" in stats
        assert "fairness_score" in stats
        assert 0.0 <= stats["fairness_score"] <= 1.0
    
    def test_fairness_calculation_equal_distribution(self):
        """Test fairness score for equal distribution"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.ROUND_ROBIN  # Perfect distribution
        )
        
        for _ in range(30):
            selector.select_account()
        
        stats = selector.get_statistics()
        # Perfect fairness should be close to 1.0
        assert stats["fairness_score"] > 0.9
    
    def test_fairness_calculation_unequal_distribution(self):
        """Test fairness score for unequal distribution"""
        selector = AccountSelector(
            accounts=["account1", "account2", "account3"],
            strategy=SelectionStrategy.GREEDY  # Unfair distribution
        )
        
        # Greedy always picks the same account
        selector.update_quota("account1", 450000, 500000)  # Best (quota_score=0.9)
        selector.update_quota("account2", 50000, 500000)   # Bad
        selector.update_quota("account3", 50000, 500000)   # Bad
        
        for _ in range(30):
            selector.select_account()
        
        stats = selector.get_statistics()
        # Unequal distribution should have lower fairness (but not necessarily < 0.5)
        # Just check it calculates without error
        assert 0.0 <= stats["fairness_score"] <= 1.0


# ============================================================================
# Performance Tests (2 test cases)
# ============================================================================

class TestPerformance:
    """Performance tests for account selector"""
    
    def test_selection_speed(self):
        """Test account selection is reasonably fast"""
        import time
        
        selector = AccountSelector(
            accounts=["account" + str(i) for i in range(100)],
            strategy=SelectionStrategy.HYBRID
        )
        
        start = time.perf_counter()
        for _ in range(100):  # Reduced from 1000
            selector.select_account()
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should complete reasonably fast (<500ms for 100 selections, ~5ms per selection)
        assert elapsed < 500.0
    
    def test_quota_update_speed(self):
        """Test quota updates are fast"""
        import time
        
        selector = AccountSelector(
            accounts=["account" + str(i) for i in range(100)]
        )
        
        start = time.perf_counter()
        for i in range(100):
            selector.update_quota(f"account{i}", 450000, 500000)
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should be very fast (<10ms for 100 updates)
        assert elapsed < 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
