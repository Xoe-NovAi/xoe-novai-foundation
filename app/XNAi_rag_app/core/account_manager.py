"""
Account Manager for XNAi RAG Stack

Implements multi-account management with proper account switching,
validation, and integration with the existing agent system.

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..services.agent_bus import AgentBusClient
from ..core.iam_service import User, Permission
from ..core.quota_checker import QuotaCache, QuotaInfo, QuotaStatus

logger = logging.getLogger(__name__)


class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class AccountType(str, Enum):
    """Account type enumeration"""
    PRIMARY = "primary"
    SERVICE = "service"
    USER = "user"


@dataclass
class AccountInfo:
    """Account information"""
    account_id: str
    name: str
    account_type: AccountType
    status: AccountStatus
    created_at: datetime
    last_used: Optional[datetime]
    email: str
    provider: str
    quota_remaining: int
    quota_limit: int
    models_preferred: List[str]
    priority: int
    api_key: Optional[str]
    usage_stats: Dict[str, Any]


class AccountManager:
    """Manages multiple provider accounts with proper switching and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the account manager
        
        Args:
            config_path: Path to account configuration
        """
        self.config_path = config_path or "memory_bank/ACCOUNT-REGISTRY.yaml"
        self.accounts: Dict[str, AccountInfo] = {}
        self.current_account: Optional[str] = None
        self.quota_cache = QuotaCache()
        self.logger = logger.getChild("AccountManager")
        
        # Account registry configuration
        self.registry_config = {
            "accounts": [],
            "rotation_strategy": "quota_aware",
            "auto_switch": True,
            "validation_enabled": True
        }
    
    async def initialize(self) -> None:
        """Initialize the account manager"""
        await self._load_registry()
        await self._validate_accounts()
        await self._set_default_account()
        
        self.logger.info(f"Initialized account manager with {len(self.accounts)} accounts")
    
    async def _load_registry(self) -> None:
        """Load account registry from YAML file"""
        if not os.path.exists(self.config_path):
            self.logger.warning(f"Account registry not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                registry_data = yaml.safe_load(f)
            
            if not registry_data:
                return
            
            self.registry_config = registry_data
            
            # Load accounts
            for account_data in registry_data.get("accounts", []):
                account_info = AccountInfo(
                    account_id=account_data["id"],
                    name=account_data["name"],
                    account_type=AccountType(account_data.get("type", "user")),
                    status=AccountStatus(account_data.get("status", "active")),
                    created_at=datetime.fromisoformat(account_data.get("created_at", datetime.now().isoformat())),
                    last_used=datetime.fromisoformat(account_data.get("last_used")) if account_data.get("last_used") else None,
                    email=account_data.get("email", ""),
                    provider=account_data.get("provider", ""),
                    quota_remaining=account_data.get("quota_remaining", 0),
                    quota_limit=account_data.get("quota_limit", 0),
                    models_preferred=account_data.get("models_preferred", []),
                    priority=account_data.get("priority", 1),
                    api_key=account_data.get("api_key"),
                    usage_stats=account_data.get("usage_stats", {
                        "total_requests": 0,
                        "successful_requests": 0,
                        "failed_requests": 0,
                        "avg_response_time": 0.0
                    })
                )
                
                self.accounts[account_info.account_id] = account_info
                
            self.logger.info(f"Loaded {len(self.accounts)} accounts from registry")
            
        except Exception as e:
            self.logger.error(f"Failed to load account registry: {e}")
    
    async def _save_registry(self) -> None:
        """Save account registry to YAML file"""
        registry_data = {
            "accounts": [
                {
                    "id": acc.account_id,
                    "name": acc.name,
                    "type": acc.account_type.value,
                    "status": acc.status.value,
                    "created_at": acc.created_at.isoformat(),
                    "last_used": acc.last_used.isoformat() if acc.last_used else None,
                    "email": acc.email,
                    "provider": acc.provider,
                    "quota_remaining": acc.quota_remaining,
                    "quota_limit": acc.quota_limit,
                    "models_preferred": acc.models_preferred,
                    "priority": acc.priority,
                    "api_key": acc.api_key,
                    "usage_stats": acc.usage_stats
                }
                for acc in self.accounts.values()
            ],
            "rotation_strategy": self.registry_config.get("rotation_strategy", "quota_aware"),
            "auto_switch": self.registry_config.get("auto_switch", True),
            "validation_enabled": self.registry_config.get("validation_enabled", True)
        }
        
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(registry_data, f, default_flow_style=False, indent=2)
            
            self.logger.debug("Saved account registry")
            
        except Exception as e:
            self.logger.error(f"Failed to save account registry: {e}")
    
    async def _validate_accounts(self) -> None:
        """Validate and update account status"""
        current_time = datetime.now()
        
        for account_id, account_info in self.accounts.items():
            # Check if account is expired
            if account_info.status == AccountStatus.ACTIVE:
                if account_info.last_used:
                    time_since_last_use = current_time - account_info.last_used
                    if time_since_last_use > timedelta(days=30):
                        account_info.status = AccountStatus.INACTIVE
                        self.logger.info(f"Account {account_id} marked as inactive (no usage for 30 days)")
            
            # Update quota information
            await self._update_account_quota(account_id)
    
    async def _update_account_quota(self, account_id: str) -> None:
        """Update quota information for an account"""
        if account_id not in self.accounts:
            return
        
        account_info = self.accounts[account_id]
        
        try:
            # Get quota from cache
            quota = await self.quota_cache.get_quota(account_info.provider, account_id)
            
            if quota:
                account_info.quota_remaining = quota.tokens_remaining
                account_info.quota_limit = quota.tokens_limit
                
        except Exception as e:
            self.logger.warning(f"Failed to update quota for account {account_id}: {e}")
    
    async def _set_default_account(self) -> None:
        """Set default account based on priority and availability"""
        if not self.accounts:
            return
        
        # Get active accounts sorted by priority and quota
        active_accounts = [
            acc for acc in self.accounts.values()
            if acc.status == AccountStatus.ACTIVE and acc.quota_remaining > 0
        ]
        
        if active_accounts:
            # Sort by priority (lower is better) and then by quota remaining
            active_accounts.sort(key=lambda x: (x.priority, -x.quota_remaining))
            self.current_account = active_accounts[0].account_id
            self.logger.info(f"Set default account: {self.current_account}")
        else:
            self.logger.warning("No active accounts available")
    
    def get_current_account(self) -> Optional[AccountInfo]:
        """Get the currently active account."""
        if self.current_account and self.current_account in self.accounts:
            return self.accounts[self.current_account]
        return None
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch to a different account"""
        if account_id not in self.accounts:
            self.logger.error(f"Account not found: {account_id}")
            return False
        
        account_info = self.accounts[account_id]
        
        # Check if account is already active
        if self.current_account == account_id:
            self.logger.info(f"Account {account_id} is already active")
            return True
        
        # Validate account status
        if account_info.status != AccountStatus.ACTIVE:
            self.logger.error(f"Account {account_id} is not active: {account_info.status}")
            return False
        
        # Check quota availability
        if account_info.quota_remaining <= 0:
            self.logger.error(f"Account {account_id} has no remaining quota")
            return False
        
        # Switch account
        old_account = self.current_account
        self.current_account = account_id
        account_info.last_used = datetime.now()
        
        await self._save_registry()
        
        self.logger.info(f"Switched from {old_account} to {account_id}")
        return True
    
    async def get_recommended_account(self, task_type: str = "general") -> Optional[AccountInfo]:
        """Get best account for task type"""
        # Get active accounts with quota
        active_accounts = [
            acc for acc in self.accounts.values()
            if acc.status == AccountStatus.ACTIVE and acc.quota_remaining > 0
        ]
        
        if not active_accounts:
            return None
        
        # Task-specific preferences
        task_preferences = {
            "reasoning": ["opus-4.6-thinking", "raptor-mini"],
            "code": ["sonnet-4.5", "haiku-4.5"],
            "quick": ["haiku-4.5", "raptor-mini"],
            "research": ["gemini-3-pro", "kimi-k2.5"]
        }
        
        preferred_models = task_preferences.get(task_type, [])
        
        # Filter accounts that support preferred models
        preferred_accounts = [
            acc for acc in active_accounts
            if any(m in acc.models_preferred for m in preferred_models)
        ]
        
        if preferred_accounts:
            # Sort by priority and quota remaining
            preferred_accounts.sort(key=lambda x: (x.priority, -x.quota_remaining))
            return preferred_accounts[0]
        
        # Fallback to any active account
        active_accounts.sort(key=lambda x: (x.priority, -x.quota_remaining))
        return active_accounts[0]
    
    async def create_account(self, name: str, account_type: AccountType, email: str, 
                           provider: str, quota_limit: int, models_preferred: List[str],
                           priority: int = 1) -> str:
        """
        Create a new account
        
        Args:
            name: Account name
            account_type: Type of account
            email: Account email
            provider: Provider name
            quota_limit: Quota limit
            models_preferred: Preferred models
            priority: Account priority
            
        Returns:
            Account ID
        """
        account_id = f"{provider}_{name.replace(' ', '_').lower()}_{len(self.accounts) + 1}"
        
        account_info = AccountInfo(
            account_id=account_id,
            name=name,
            account_type=account_type,
            status=AccountStatus.ACTIVE,
            created_at=datetime.now(),
            last_used=None,
            email=email,
            provider=provider,
            quota_remaining=quota_limit,
            quota_limit=quota_limit,
            models_preferred=models_preferred,
            priority=priority,
            api_key=None,
            usage_stats={
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0
            }
        )
        
        self.accounts[account_id] = account_info
        await self._save_registry()
        
        self.logger.info(f"Created account: {account_id}")
        return account_id
    
    async def update_usage_stats(self, account_id: str, success: bool, response_time: float) -> None:
        """Update usage statistics for an account"""
        if account_id not in self.accounts:
            return
        
        account_info = self.accounts[account_id]
        stats = account_info.usage_stats
        
        stats['total_requests'] += 1
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # Update average response time
        current_avg = stats['avg_response_time']
        total_requests = stats['total_requests']
        stats['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        await self._save_registry()
    
    async def get_account_status(self, account_id: str) -> Optional[AccountInfo]:
        """Get account status"""
        return self.accounts.get(account_id)
    
    async def list_accounts(self, account_type: Optional[AccountType] = None) -> List[AccountInfo]:
        """List accounts, optionally filtered by type"""
        if account_type:
            return [
                acc for acc in self.accounts.values()
                if acc.account_type == account_type
            ]
        return list(self.accounts.values())
    
    async def suspend_account(self, account_id: str, reason: str = "") -> bool:
        """Suspend an account"""
        if account_id not in self.accounts:
            return False
        
        account_info = self.accounts[account_id]
        account_info.status = AccountStatus.SUSPENDED
        
        await self._save_registry()
        self.logger.info(f"Suspended account {account_id}: {reason}")
        return True
    
    async def activate_account(self, account_id: str) -> bool:
        """Activate a suspended account"""
        if account_id not in self.accounts:
            return False
        
        account_info = self.accounts[account_id]
        account_info.status = AccountStatus.ACTIVE
        
        await self._save_registry()
        self.logger.info(f"Activated account {account_id}")
        return True
    
    async def get_usage_report(self) -> Dict[str, Any]:
        """Get usage report for all accounts"""
        report = {
            'total_accounts': len(self.accounts),
            'active_accounts': 0,
            'inactive_accounts': 0,
            'suspended_accounts': 0,
            'expired_accounts': 0,
            'account_details': []
        }
        
        for account_info in self.accounts.values():
            # Count status
            if account_info.status == AccountStatus.ACTIVE:
                report['active_accounts'] += 1
            elif account_info.status == AccountStatus.INACTIVE:
                report['inactive_accounts'] += 1
            elif account_info.status == AccountStatus.SUSPENDED:
                report['suspended_accounts'] += 1
            elif account_info.status == AccountStatus.EXPIRED:
                report['expired_accounts'] += 1
            
            # Add account details
            stats = account_info.usage_stats
            success_rate = (
                stats['successful_requests'] / stats['total_requests'] * 100
                if stats['total_requests'] > 0 else 0
            )
            
            report['account_details'].append({
                'account_id': account_info.account_id,
                'name': account_info.name,
                'type': account_info.account_type.value,
                'status': account_info.status.value,
                'provider': account_info.provider,
                'priority': account_info.priority,
                'models_preferred': account_info.models_preferred,
                'quota_remaining': account_info.quota_remaining,
                'quota_limit': account_info.quota_limit,
                'quota_percent': round((account_info.quota_remaining / max(account_info.quota_limit, 1)) * 100, 2),
                'total_requests': stats['total_requests'],
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(stats['avg_response_time'], 2),
                'last_used': account_info.last_used.isoformat() if account_info.last_used else None
            })
        
        return report
    
    async def cleanup_expired_accounts(self, days_old: int = 90) -> int:
        """Clean up accounts that haven't been used for specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        accounts_to_delete = []
        for account_id, account_info in self.accounts.items():
            if account_info.last_used and account_info.last_used < cutoff_date:
                accounts_to_delete.append(account_id)
        
        for account_id in accounts_to_delete:
            del self.accounts[account_id]
            deleted_count += 1
        
        if deleted_count > 0:
            await self._save_registry()
            self.logger.info(f"Cleaned up {deleted_count} expired accounts")
        
        return deleted_count


# Global account manager instance
account_manager = AccountManager()


async def get_account_manager() -> AccountManager:
    """Get the global account manager instance"""
    if not account_manager.accounts:
        await account_manager.initialize()
    return account_manager