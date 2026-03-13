#!/usr/bin/env python3
"""
XNAi Account Management - Base Module

Provides abstract base classes and common interfaces for multi-provider
account management. Designed to be modular and portable.

Author: XNAi Foundation
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import os


class ProviderName(Enum):
    """Supported providers."""

    GITHUB = "github"
    ANTIGRAVITY = "antigravity"
    OPENCODE = "opencode"
    GEMINI = "gemini"


@dataclass
class AccountStatus:
    """
    Status of a single account.

    This is the core data structure representing an account's state.
    Used by all provider implementations.
    """

    account_id: str
    email: str
    authenticated: bool = False
    remaining: int = 0
    limit: int = 0
    used: int = 0
    reset_date: Optional[datetime] = None
    models_preferred: List[str] = field(default_factory=list)
    status: str = "unknown"  # active, ready, depleted, error
    provider: str = ""
    last_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def usage_percent(self) -> float:
        """Calculate usage percentage."""
        if self.limit == 0:
            return 0.0
        return (self.used / self.limit) * 100

    @property
    def remaining_percent(self) -> float:
        """Calculate remaining percentage."""
        return 100 - self.usage_percent

    @property
    def is_available(self) -> bool:
        """Check if account has remaining quota."""
        return self.remaining > 0 and self.status != "depleted"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "account_id": self.account_id,
            "email": self.email,
            "authenticated": self.authenticated,
            "remaining": self.remaining,
            "limit": self.limit,
            "used": self.used,
            "reset_date": self.reset_date.isoformat() if self.reset_date else None,
            "models_preferred": self.models_preferred,
            "status": self.status,
            "provider": self.provider,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "usage_percent": self.usage_percent,
            "remaining_percent": self.remaining_percent,
            "is_available": self.is_available,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccountStatus":
        """Create from dictionary."""
        reset_date = data.get("reset_date")
        if isinstance(reset_date, str):
            reset_date = datetime.fromisoformat(reset_date)

        last_check = data.get("last_check")
        if isinstance(last_check, str):
            last_check = datetime.fromisoformat(last_check)

        return cls(
            account_id=data.get("account_id", ""),
            email=data.get("email", ""),
            authenticated=data.get("authenticated", False),
            remaining=data.get("remaining", 0),
            limit=data.get("limit", 0),
            used=data.get("used", 0),
            reset_date=reset_date,
            models_preferred=data.get("models_preferred", []),
            status=data.get("status", "unknown"),
            provider=data.get("provider", ""),
            last_check=last_check,
            metadata=data.get("metadata", {}),
        )


class BaseAccountProvider(ABC):
    """
    Abstract base class for account providers.

    All provider implementations must inherit from this class
    and implement the abstract methods.

    Design principles:
    - Provider-agnostic core logic
    - Async-first architecture
    - Stateless (state stored in registry)
    - Pluggable for easy extension
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize provider.

        Args:
            config_path: Path to provider-specific config
        """
        self.config_path = config_path or os.getenv("ACCOUNT_MGMT_CONFIG_PATH", "memory_bank/usage/accounts.yaml")
        self.config = self._load_config()

    @abstractmethod
    def get_name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name (e.g., 'github', 'antigravity')
        """
        pass

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            return {}

        try:
            with open(self.config_path) as f:
                if self.config_path.endswith(".yaml") or self.config_path.endswith(".yml"):
                    import yaml

                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}

    async def get_accounts(self) -> List[AccountStatus]:
        """
        Get status of all accounts for this provider.

        Returns:
            List of AccountStatus objects
        """
        raise NotImplementedError("Subclasses must implement get_accounts")

    async def check_rate_limit(self, account_id: str) -> Dict[str, Any]:
        """
        Check rate limit for specific account.

        Args:
            account_id: Account identifier

        Returns:
            Dict with limit, remaining, used, reset info
        """
        raise NotImplementedError("Subclasses must implement check_rate_limit")

    async def switch_account(self, account_id: str) -> bool:
        """
        Switch to a different account.

        Args:
            account_id: Target account ID

        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement switch_account")

    def get_recommended_account(self, accounts: List[AccountStatus], task_type: str = "general") -> Optional[AccountStatus]:
        """
        Get best account for task type.

        Args:
            accounts: List of available accounts
            task_type: Type of task (reasoning, code, quick, research)

        Returns:
            Best account or None
        """
        # Default implementation: return available with lowest usage
        available = [a for a in accounts if a.is_available]

        if not available:
            return None

        return min(available, key=lambda a: a.used)

    def validate_account(self, account: AccountStatus) -> bool:
        """
        Validate account is in good standing.

        Args:
            account: Account to validate

        Returns:
            True if account is valid
        """
        return account.authenticated and account.is_available and account.status != "error"

    def filter_by_model(self, accounts: List[AccountStatus], model: str) -> List[AccountStatus]:
        """
        Filter accounts by supported model.

        Args:
            accounts: List of accounts
            model: Model name

        Returns:
            Filtered list
        """
        return [a for a in accounts if model in a.models_preferred and a.is_available]


# Utility functions


def load_accounts_from_yaml(config_path: str) -> List[Dict]:
    """Load accounts from YAML config."""
    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config.get("accounts", [])


def load_accounts_from_json(config_path: str) -> List[Dict]:
    """Load accounts from JSON config."""
    with open(config_path) as f:
        config = json.load(f)

    return config.get("accounts", [])


def save_accounts_to_json(accounts: List[AccountStatus], output_path: str):
    """Save accounts to JSON file."""
    data = {"timestamp": datetime.now().isoformat(), "accounts": [a.to_dict() for a in accounts]}

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
