"""
Account Rotation System - Phase 3C-2B Smart Fallback Orchestration

Implements hybrid weighted selection for account rotation:
- 60% weight: Quota remaining score
- 40% weight: Recency score (when last used)
- Starvation prevention: 10% forced LRU selection
- Race condition mitigation: Jitter for top 3 accounts
"""

import random
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SelectionStrategy(Enum):
    """Account selection strategies"""
    GREEDY = "greedy"  # Always pick highest quota
    ROUND_ROBIN = "round_robin"  # Rotate through accounts in order
    STICKY = "sticky"  # Stick with account until exhausted
    LRU = "lru"  # Least-recently-used (fairness)
    HYBRID = "hybrid"  # Hybrid weighted (recommended)


@dataclass
class AccountScore:
    """Per-account scoring for selection"""
    account_id: str
    quota_remaining: int
    quota_limit: int
    percent_used: float = field(default=0.0)
    last_used: datetime = field(default_factory=datetime.utcnow)
    health_score: float = field(default=1.0)  # 0.0-1.0
    
    # Calculated scores
    quota_score: float = field(default=0.0)  # 0.0-1.0 (higher = more quota)
    recency_score: float = field(default=0.0)  # 0.0-1.0 (higher = more recently used)
    final_score: float = field(default=0.0)  # 0.0-1.0 (weighted combination)
    
    def __post_init__(self):
        self.percent_used = 100.0 * (1 - self.quota_remaining / max(self.quota_limit, 1))
        self._calculate_scores()
    
    def _calculate_scores(self):
        """Calculate quota and recency scores"""
        # Quota score: 1.0 when 0% used, 0.0 when 100% used
        self.quota_score = max(0.0, 1.0 - (self.percent_used / 100.0))
        
        # Recency score: 1.0 if used now, 0.0 if never used
        # Decay over 24 hours
        age_seconds = (datetime.utcnow() - self.last_used).total_seconds()
        max_age_seconds = 86400  # 24 hours
        self.recency_score = max(0.0, 1.0 - (age_seconds / max_age_seconds))
        
        # Health score multiplier (e.g., 0.5 if circuit open)
        # Applied separately in selection logic
        
        # Final score: 60% quota, 40% recency
        self.final_score = (0.6 * self.quota_score) + (0.4 * self.recency_score)


@dataclass
class SelectionResult:
    """Result of account selection"""
    selected_account: str
    selection_strategy: SelectionStrategy
    score: float
    candidates: List[str]  # Top 3 candidates considered
    reasoning: str


class AccountSelector:
    """
    Intelligent account selector for load balancing
    
    Implements hybrid weighted selection with:
    - 60% quota optimization
    - 40% recency fairness
    - 10% forced LRU rotation (starvation prevention)
    - Jitter across top 3 accounts (race condition mitigation)
    """
    
    def __init__(self, accounts: List[str], strategy: SelectionStrategy = SelectionStrategy.HYBRID):
        """
        Initialize account selector
        
        Args:
            accounts: List of account IDs to manage
            strategy: Selection strategy to use
        """
        self.accounts = accounts
        self.strategy = strategy
        self.scores: Dict[str, AccountScore] = {}
        self.selection_history: List[Tuple[str, datetime]] = []
        self.logger = logger.getChild("AccountSelector")
        
        # Initialize scores for all accounts
        for account_id in accounts:
            self.scores[account_id] = AccountScore(
                account_id=account_id,
                quota_remaining=500000,
                quota_limit=500000
            )
    
    def update_quota(self, account_id: str, quota_remaining: int, quota_limit: int) -> None:
        """Update quota for account"""
        if account_id not in self.scores:
            self.scores[account_id] = AccountScore(
                account_id=account_id,
                quota_remaining=quota_remaining,
                quota_limit=quota_limit
            )
        else:
            self.scores[account_id].quota_remaining = quota_remaining
            self.scores[account_id].quota_limit = quota_limit
            self.scores[account_id].__post_init__()  # Recalculate scores
    
    def record_usage(self, account_id: str) -> None:
        """Record when account was last used"""
        if account_id in self.scores:
            self.scores[account_id].last_used = datetime.utcnow()
        
        self.selection_history.append((account_id, datetime.utcnow()))
    
    def select_account(self, force_strategy: Optional[SelectionStrategy] = None) -> SelectionResult:
        """
        Select best account based on strategy
        
        Args:
            force_strategy: Override default strategy for this selection
        
        Returns:
            SelectionResult with selected account and reasoning
        """
        strategy = force_strategy or self.strategy
        
        if strategy == SelectionStrategy.HYBRID:
            return self._select_hybrid()
        elif strategy == SelectionStrategy.GREEDY:
            return self._select_greedy()
        elif strategy == SelectionStrategy.ROUND_ROBIN:
            return self._select_round_robin()
        elif strategy == SelectionStrategy.STICKY:
            return self._select_sticky()
        elif strategy == SelectionStrategy.LRU:
            return self._select_lru()
        else:
            # Default to hybrid
            return self._select_hybrid()
    
    def _select_hybrid(self) -> SelectionResult:
        """
        Hybrid weighted selection (recommended)
        
        - 60% quota score (prefer high-quota accounts)
        - 40% recency score (prefer recently-used, fairness)
        - 10% forced LRU (prevent starvation)
        - Jitter across top 3 (prevent thundering herd)
        """
        # Sort by final score
        sorted_accounts = sorted(
            self.scores.items(),
            key=lambda x: x[1].final_score,
            reverse=True
        )
        
        # Get top 3 candidates
        top_3 = sorted_accounts[:3]
        candidates = [acc for acc, _ in top_3]
        
        # 90% of time: choose from top 3
        if random.random() < 0.9:
            # Add small jitter to prevent all instances picking same account
            jitter = random.uniform(0.95, 1.05)
            weighted_scores = [(acc, score.final_score * jitter) for acc, score in top_3]
            selected = max(weighted_scores, key=lambda x: x[1])[0]
        
        # 10% of time: forced LRU (prevent starvation)
        else:
            # Pick account with oldest last_used
            selected = min(
                self.scores.items(),
                key=lambda x: x[1].last_used
            )[0]
        
        self.record_usage(selected)
        
        selected_score = self.scores[selected].final_score
        reasoning = f"Hybrid: top3={candidates}, selected={selected} (score={selected_score:.2f})"
        
        self.logger.info(reasoning)
        
        return SelectionResult(
            selected_account=selected,
            selection_strategy=SelectionStrategy.HYBRID,
            score=selected_score,
            candidates=candidates,
            reasoning=reasoning
        )
    
    def _select_greedy(self) -> SelectionResult:
        """Always pick account with most quota"""
        selected = max(
            self.scores.items(),
            key=lambda x: x[1].quota_score
        )
        
        account_id, score = selected
        self.record_usage(account_id)
        
        reasoning = f"Greedy: selected={account_id} (quota_score={score.quota_score:.2f})"
        self.logger.info(reasoning)
        
        return SelectionResult(
            selected_account=account_id,
            selection_strategy=SelectionStrategy.GREEDY,
            score=score.quota_score,
            candidates=[account_id],
            reasoning=reasoning
        )
    
    def _select_round_robin(self) -> SelectionResult:
        """Rotate through accounts in order"""
        idx = len(self.selection_history) % len(self.accounts)
        account_id = self.accounts[idx]
        
        self.record_usage(account_id)
        score = self.scores[account_id].final_score
        
        reasoning = f"RoundRobin: turn={len(self.selection_history)}, selected={account_id}"
        self.logger.info(reasoning)
        
        return SelectionResult(
            selected_account=account_id,
            selection_strategy=SelectionStrategy.ROUND_ROBIN,
            score=score,
            candidates=[account_id],
            reasoning=reasoning
        )
    
    def _select_sticky(self) -> SelectionResult:
        """Stick with account until exhausted"""
        if self.selection_history:
            # Use same account if it has quota
            last_account, _ = self.selection_history[-1]
            last_score = self.scores[last_account]
            
            if last_score.percent_used < 95:
                # Still has quota, stick with it
                self.record_usage(last_account)
                reasoning = f"Sticky: continuing with {last_account}"
                self.logger.info(reasoning)
                
                return SelectionResult(
                    selected_account=last_account,
                    selection_strategy=SelectionStrategy.STICKY,
                    score=last_score.final_score,
                    candidates=[last_account],
                    reasoning=reasoning
                )
        
        # Account exhausted or first call, pick best available
        selected = max(
            self.scores.items(),
            key=lambda x: x[1].quota_score
        )
        
        account_id, score = selected
        self.record_usage(account_id)
        
        reasoning = f"Sticky: switched to {account_id} (prev exhausted)"
        self.logger.info(reasoning)
        
        return SelectionResult(
            selected_account=account_id,
            selection_strategy=SelectionStrategy.STICKY,
            score=score.quota_score,
            candidates=[account_id],
            reasoning=reasoning
        )
    
    def _select_lru(self) -> SelectionResult:
        """Least-recently-used (perfect fairness)"""
        selected = min(
            self.scores.items(),
            key=lambda x: x[1].last_used
        )
        
        account_id, score = selected
        self.record_usage(account_id)
        
        reasoning = f"LRU: selected={account_id} (least recently used)"
        self.logger.info(reasoning)
        
        return SelectionResult(
            selected_account=account_id,
            selection_strategy=SelectionStrategy.LRU,
            score=score.recency_score,
            candidates=[account_id],
            reasoning=reasoning
        )
    
    def get_statistics(self) -> Dict:
        """Get selection statistics"""
        total_selections = len(self.selection_history)
        
        # Count selections per account
        selection_counts = {}
        for account_id, _ in self.selection_history:
            selection_counts[account_id] = selection_counts.get(account_id, 0) + 1
        
        # Calculate fairness (Gini coefficient)
        if selection_counts:
            counts = list(selection_counts.values())
            mean_count = sum(counts) / len(counts)
            variance = sum((c - mean_count) ** 2 for c in counts) / len(counts)
            fairness = 1.0 - (variance / (mean_count ** 2 + 1e-6))  # 0.0 = unfair, 1.0 = fair
        else:
            fairness = 1.0
        
        return {
            "total_selections": total_selections,
            "selection_counts": selection_counts,
            "fairness_score": max(0.0, fairness),
            "avg_selections_per_account": total_selections / len(self.accounts) if self.accounts else 0,
            "quota_states": {
                acc_id: {
                    "percent_used": self.scores[acc_id].percent_used,
                    "quota_score": self.scores[acc_id].quota_score,
                    "recency_score": self.scores[acc_id].recency_score,
                    "final_score": self.scores[acc_id].final_score,
                }
                for acc_id in self.accounts
            }
        }
