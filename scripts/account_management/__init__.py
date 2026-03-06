# Account Management Module
# XNAi Foundation - Modular Multi-Provider Account Management
#
# This module provides a plug-and-play interface for managing
# multiple accounts across different AI providers.

__version__ = "1.0.0"

# Base classes
from .base import BaseAccountProvider, AccountStatus

# Provider implementations
from .github import GitHubProvider
from .antigravity import AntigravityProvider
from .opencode import OpenCodeProvider

# Core functionality
from .rotation import RotationEngine, RotationStrategy, RotationRule
from .quota_monitor import QuotaMonitor
from .audit import AuditLogger, AuditEvent
from .registry import AccountRegistry

__all__ = [
    # Base
    "BaseAccountProvider",
    "AccountStatus",
    # Providers
    "GitHubProvider",
    "AntigravityProvider",
    "OpenCodeProvider",
    # Core
    "RotationEngine",
    "RotationStrategy",
    "RotationRule",
    "QuotaMonitor",
    "AuditLogger",
    "AuditEvent",
    "AccountRegistry",
]


# Quick access
def get_provider(name: str, **kwargs):
    """Get provider by name."""
    providers = {
        "github": GitHubProvider,
        "antigravity": AntigravityProvider,
        "opencode": OpenCodeProvider,
    }

    provider_class = providers.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}")

    return provider_class(**kwargs)
