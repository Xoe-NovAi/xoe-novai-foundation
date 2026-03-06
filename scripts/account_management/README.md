# XNAi Modular Account Management System

**Version**: 1.0.0  
**Date**: 2026-02-26  
**Purpose**: Modular, plug-and-play account management for multi-provider AI services

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    XNAi Account Management System                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │   GitHub    │    │  Antigravity │    │   OpenCode  │            │
│  │   Module    │    │    Module    │    │    Module   │            │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘            │
│         │                   │                   │                      │
│         └───────────────────┼───────────────────┘                      │
│                             ▼                                          │
│                  ┌──────────────────────┐                              │
│                  │   Account Registry   │                              │
│                  │   (Unified Config)  │                              │
│                  └──────────┬───────────┘                              │
│                             │                                          │
│         ┌───────────────────┼───────────────────┐                    │
│         ▼                   ▼                   ▼                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Quota     │    │  Rotation   │    │   Audit     │          │
│  │   Monitor   │    │   Engine    │    │   Logger    │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
scripts/account_management/
├── __init__.py
├── base.py                 # Abstract base class for all providers
├── github.py               # GitHub/Copilot account management
├── antigravity.py           # Antigravity account management  
├── opencode.py             # OpenCode account management
├── rotation.py             # Rotation engine
├── quota_monitor.py        # Quota monitoring
├── audit.py                # Audit logging
└── registry.py             # Unified account registry
```

---

## Base Interface

```python
# base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class AccountStatus:
    """Status of a single account."""
    account_id: str
    email: str
    authenticated: bool
    remaining: int
    limit: int
    used: int
    reset_date: Optional[datetime]
    models_preferred: List[str]
    status: str  # active, ready, depleted, error


class BaseAccountProvider(ABC):
    """Abstract base class for account providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Provider name (e.g., 'github', 'antigravity')."""
        pass
    
    @abstractmethod
    async def get_accounts(self) -> List[AccountStatus]:
        """Get status of all accounts."""
        pass
    
    @abstractmethod
    async def check_rate_limit(self, account_id: str) -> Dict[str, Any]:
        """Check rate limit for specific account."""
        pass
    
    @abstractmethod
    async def switch_account(self, account_id: str) -> bool:
        """Switch to a different account."""
        pass
    
    @abstractmethod
    def get_recommended_account(self, task_type: str) -> Optional[AccountStatus]:
        """Get best account for task type."""
        pass
```

---

## GitHub Provider Implementation

```python
# github.py
import os
import json
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAccountProvider, AccountStatus


class GitHubProvider(BaseAccountProvider):
    """GitHub/Copilot account management."""
    
    def __init__(self, config_path: str = "memory_bank/usage/github-accounts.yaml"):
        self.config_path = config_path
        self.accounts = self._load_config()
        
    def get_name(self) -> str:
        return "github"
    
    def _load_config(self) -> List[Dict]:
        """Load account config from YAML."""
        import yaml
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                return config.get("accounts", [])
        except:
            return []
    
    async def get_accounts(self) -> List[AccountStatus]:
        """Get status of all GitHub accounts."""
        accounts = []
        
        # Try gh CLI first
        try:
            result = subprocess.run(
                ["gh", "auth", "status", "--verbose"],
                capture_output=True,
                text=True
            )
            
            # Parse authenticated accounts
            for line in result.stdout.split("\n"):
                if "Logged in to github.com" in line:
                    # Extract username
                    pass
                    
        except:
            pass
        
        # Fall back to config
        for acc in self.accounts:
            accounts.append(AccountStatus(
                account_id=acc.get("id", ""),
                email=acc.get("email", ""),
                authenticated=acc.get("status") == "active",
                remaining=acc.get("copilot", {}).get("messages_limit", 50) - 
                         acc.get("copilot", {}).get("messages_used", 0),
                limit=acc.get("copilot", {}).get("messages_limit", 50),
                used=acc.get("copilot", {}).get("messages_used", 0),
                reset_date=datetime.fromisoformat(acc.get("copilot", {}).get("reset_date", "2026-03-01")),
                models_preferred=acc.get("copilot", {}).get("models_preferred", ["raptor-mini", "haiku-4.5"]),
                status=acc.get("status", "ready")
            ))
        
        return accounts
    
    async def check_rate_limit(self, account_id: str) -> Dict[str, Any]:
        """Check rate limit via GitHub API."""
        try:
            result = subprocess.run(
                ["gh", "api", "rate_limit"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                core = data.get("resources", {}).get("core", {})
                
                return {
                    "limit": core.get("limit", 5000),
                    "remaining": core.get("remaining", 5000),
                    "used": core.get("limit", 5000) - core.get("remaining", 5000),
                    "reset": datetime.fromtimestamp(core.get("reset", 0))
                }
        except:
            pass
        
        return {"error": "Could not check rate limit"}
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch GitHub account."""
        account = next((a for a in self.accounts if a.get("id") == account_id), None)
        
        if not account:
            return False
            
        try:
            username = account.get("username") or account.get("email", "").split("@")[0]
            result = subprocess.run(
                ["gh", "auth", "switch", "--user", username],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_recommended_account(self, task_type: str) -> Optional[AccountStatus]:
        """Get best account for task type."""
        import asyncio
        accounts = asyncio.run(self.get_accounts())
        
        # Filter by status
        active = [a for a in accounts if a.status == "active" and a.remaining > 0]
        
        if not active:
            # Get any account with remaining quota
            active = [a for a in accounts if a.remaining > 0]
        
        if not active:
            return None
        
        # Task-specific selection
        if task_type == "reasoning":
            # Prefer accounts with more quota for reasoning
            return max(active, key=lambda a: a.remaining)
        
        # Default: round-robin or least-used
        return min(active, key=lambda a: a.used)
```

---

## Rotation Engine

```python
# rotation.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class RotationStrategy(Enum):
    """Available rotation strategies."""
    LOWEST_USAGE = "lowest-usage-first"
    ROUND_ROBIN = "round-robin"
    QUOTA_AWARE = "quota-aware"
    TASK_SPECIFIC = "task-specific"


@dataclass
class RotationRule:
    """Rule for account rotation."""
    strategy: RotationStrategy
    warning_threshold: int = 40  # % remaining
    exhaustion_threshold: int = 10  # % remaining
    auto_switch: bool = True


class RotationEngine:
    """Intelligent account rotation engine."""
    
    def __init__(self, accounts: List[Any], rules: RotationRule):
        self.accounts = accounts
        self.rules = rules
        self.current_index = 0
        self.last_rotation = datetime.now()
        
    def select_account(self, task_type: str = "general") -> Optional[Any]:
        """Select best account based on strategy."""
        
        if self.rules.strategy == RotationStrategy.LOWEST_USAGE:
            return self._select_lowest_usage()
        
        elif self.rules.strategy == RotationStrategy.ROUND_ROBIN:
            return self._select_round_robin()
        
        elif self.rules.strategy == RotationStrategy.QUOTA_AWARE:
            return self._select_quota_aware()
        
        elif self.rules.strategy == RotationStrategy.TASK_SPECIFIC:
            return self._select_task_specific(task_type)
        
        return None
    
    def _select_lowest_usage(self) -> Optional[Any]:
        """Select account with lowest usage."""
        available = [a for a in self.accounts if a.remaining > 0]
        
        if not available:
            return None
            
        return min(available, key=lambda a: a.used)
    
    def _select_round_robin(self) -> Optional[Any]:
        """Round-robin selection."""
        available = [a for a in self.accounts if a.remaining > 0]
        
        if not available:
            return None
        
        # Move through accounts
        selected = available[self.current_index % len(available)]
        self.current_index += 1
        
        return selected
    
    def _select_quota_aware(self) -> Optional[Any]:
        """Select based on quota percentage remaining."""
        available = [a for a in self.accounts if a.remaining > 0]
        
        if not available:
            return None
        
        # Prefer accounts above warning threshold
        above_warning = [
            a for a in available 
            if (a.remaining / a.limit * 100) > self.rules.warning_threshold
        ]
        
        if above_warning:
            return min(above_warning, key=lambda a: a.used)
        
        return min(available, key=lambda a: a.remaining)
    
    def _select_task_specific(self, task_type: str) -> Optional[Any]:
        """Select based on task type."""
        # Task-specific preferences
        preferences = {
            "reasoning": {"models": ["opus-4.6-thinking", "raptor-mini"]},
            "code": {"models": ["sonnet-4.5", "haiku-4.5"]},
            "quick": {"models": ["haiku-4.5", "raptor-mini"]},
            "research": {"models": ["gemini-3-pro", "kimi-k2.5"]}
        }
        
        preferred = preferences.get(task_type, {})
        
        # Filter accounts that support preferred models
        available = [
            a for a in self.accounts 
            if a.remaining > 0 and any(m in a.models_preferred for m in preferred.get("models", []))
        ]
        
        if not available:
            return self._select_lowest_usage()
        
        return min(available, key=lambda a: a.used)
    
    def should_rotate(self, account: Any) -> bool:
        """Check if account should be rotated."""
        if not account:
            return True
        
        if account.remaining == 0:
            return True
        
        percentage = (account.remaining / account.limit) * 100
        
        return percentage < self.rules.exhaustion_threshold
```

---

## Usage Examples

### Basic Usage

```python
# example_usage.py
import asyncio
from account_management.github import GitHubProvider
from account_management.rotation import RotationEngine, RotationStrategy, RotationRule

async def main():
    # Initialize provider
    github = GitHubProvider()
    
    # Get all accounts
    accounts = await github.get_accounts()
    
    for account in accounts:
        print(f"{account.email}: {account.remaining}/{account.limit} remaining")
    
    # Initialize rotation engine
    rule = RotationRule(
        strategy=RotationStrategy.QUOTA_AWARE,
        warning_threshold=40,
        exhaustion_threshold=10,
        auto_switch=True
    )
    
    engine = RotationEngine(accounts, rule)
    
    # Get best account for task
    best = engine.select_account(task_type="reasoning")
    print(f"Best account: {best.email}")
    
    # Check if should rotate
    if engine.should_rotate(best):
        print("Warning: Account quota low, consider rotating")

asyncio.run(main())
```

### CLI Integration

```bash
# Check account status
python -m account_management github status

# Switch account
python -m account_management github switch --account gh-contrib-01

# Get recommendation
python -m account_management recommend --task reasoning
```

---

## Integration with Existing Infrastructure

### Integration Points

| Component | Integration | Method |
|-----------|-------------|--------|
| **Quota Auditor** | `scripts/xnai-quota-audit.py` | Read JSON output, update dashboard |
| **Dispatcher** | `multi_provider_dispatcher.py` | Use as account selector |
| **Dashboard** | `memory_bank/usage/DASHBOARD.md` | Generate from audit JSON |
| **Agent Bus** | Redis Streams | Publish account events |

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GitHub Audit   │────▶│  Account        │────▶│  Rotation      │
│  Script         │     │  Registry        │     │  Engine        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ github-accounts │     │ Unified Config  │     │ Dispatcher      │
│ .yaml           │     │ JSON             │     │ Selection       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Quota           │     │ Dashboard        │     │ Agent Bus       │
│ Monitoring      │     │ Generation       │     │ Events          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Portable / Plug-and-Play Design

### As Standalone Module

```bash
# Install as standalone
pip install -e /path/to/xoe-novai-foundation/scripts/account_management

# Use in any project
from account_management.github import GitHubProvider

provider = GitHubProvider(config_path="/my/config/accounts.yaml")
```

### Environment Variables

```bash
# Configure via environment
export ACCOUNT_MGMT_CONFIG_PATH="/my/config/accounts.yaml"
export ACCOUNT_MGMT_LOG_LEVEL="INFO"
export ACCOUNT_MGMT_AUTO_ROTATE="true"
```

### Docker Integration

```yaml
# docker-compose.yml
services:
  account-auditor:
    image: xnai-account-management
    volumes:
      - ./accounts.yaml:/app/config/accounts.yaml
    environment:
      - ACCOUNT_MGMT_CONFIG_PATH=/app/config/accounts.yaml
    cron:
      - "0 0 * * * python -m account_management audit"
```

---

## Configuration Files

### Account Registry Format

```yaml
# accounts.yaml
version: "1.0.0"

providers:
  github:
    enabled: true
    accounts:
      - id: "gh-01"
        email: "user1@example.com"
        role: "admin"
        daily_driver: true
        copilot:
          messages_limit: 50
          models_preferred: ["raptor-mini", "haiku-4.5"]
          
  antigravity:
    enabled: true
    accounts:
      - id: "ag-01"
        email: "user1@antigravity.com"
        models_preferred: ["claude-opus-4.6-thinking"]

rotation:
  default_strategy: "quota-aware"
  warning_threshold: 40
  exhaustion_threshold: 10
  auto_switch: true
```

---

## Dependencies

```txt
# requirements.txt
pyyaml>=6.0
aiohttp>=3.9.0
redis>=5.0.0
```

---

## Status

**Version**: 1.0.0  
**Status**: Modular architecture designed, implementation ready  
**Next**: Implement all provider modules, integrate with dispatcher

---

**Last Updated**: 2026-02-26
