#!/usr/bin/env python3
"""
Agent Account Manager for XNAi Foundation

This script manages multiple CLI agent accounts, handles authentication,
and provides account-specific configuration and monitoring.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import asyncio
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    SUBAGENT = "subagent"
    COORDINATOR = "coordinator"
    VALIDATOR = "validator"


@dataclass
class AccountInfo:
    """Account information"""
    account_id: str
    name: str
    account_type: AccountType
    status: AccountStatus
    created_at: datetime
    last_used: Optional[datetime]
    rate_limit: str
    capabilities: List[str]
    priority: int
    api_key: Optional[str]
    encrypted_config: Optional[bytes]
    usage_stats: Dict[str, Any]


class AgentAccountManager:
    """Manages multiple CLI agent accounts"""
    
    def __init__(self, accounts_dir: str = "secrets/accounts"):
        """
        Initialize the account manager
        
        Args:
            accounts_dir: Directory to store account information
        """
        self.accounts_dir = Path(accounts_dir)
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        
        # Encryption key for sensitive data
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Account registry
        self.accounts: Dict[str, AccountInfo] = {}
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Configuration
        self.config_path = Path("configs/multi-agent-config.yaml")
        self.config: Optional[Dict] = None
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for account data"""
        key_file = self.accounts_dir / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key
    
    async def load_config(self) -> None:
        """Load multi-agent configuration"""
        if not self.config_path.exists():
            logger.warning(f"Configuration file not found: {self.config_path}")
            return
        
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        self.config = config_data.get('multi_agent', {})
        logger.info("Loaded multi-agent configuration")
    
    async def initialize(self) -> None:
        """Initialize the account manager"""
        await self.load_config()
        await self._load_accounts()
        await self._validate_accounts()
        
        logger.info(f"Initialized account manager with {len(self.accounts)} accounts")
    
    async def _load_accounts(self) -> None:
        """Load existing accounts from disk"""
        accounts_file = self.accounts_dir / "accounts.json"
        
        if not accounts_file.exists():
            logger.info("No existing accounts found")
            return
        
        try:
            with open(accounts_file, 'r') as f:
                accounts_data = json.load(f)
            
            for account_data in accounts_data:
                # Decrypt sensitive data
                if account_data.get('encrypted_config'):
                    account_data['encrypted_config'] = self.cipher.decrypt(
                        account_data['encrypted_config'].encode()
                    )
                
                account_info = AccountInfo(**account_data)
                self.accounts[account_info.account_id] = account_info
                
            logger.info(f"Loaded {len(self.accounts)} accounts from disk")
            
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
    
    async def _save_accounts(self) -> None:
        """Save accounts to disk"""
        accounts_data = []
        
        for account_info in self.accounts.values():
            # Encrypt sensitive data
            account_dict = asdict(account_info)
            if account_dict.get('encrypted_config'):
                account_dict['encrypted_config'] = self.cipher.encrypt(
                    account_dict['encrypted_config']
                ).decode()
            
            accounts_data.append(account_dict)
        
        accounts_file = self.accounts_dir / "accounts.json"
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f, indent=2, default=str)
        
        logger.debug("Saved accounts to disk")
    
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
                        logger.info(f"Account {account_id} marked as inactive (no usage for 30 days)")
            
            # Initialize rate limit tracking
            if account_id not in self.rate_limits:
                self.rate_limits[account_id] = []
    
    async def create_account(self, name: str, account_type: AccountType, capabilities: List[str], 
                           priority: int = 1, rate_limit: str = "standard") -> str:
        """
        Create a new agent account
        
        Args:
            name: Account name
            account_type: Type of account
            capabilities: List of capabilities
            priority: Account priority (lower = higher priority)
            rate_limit: Rate limit configuration
            
        Returns:
            Account ID
        """
        account_id = f"{account_type.value}_{secrets.token_hex(8)}"
        
        account_info = AccountInfo(
            account_id=account_id,
            name=name,
            account_type=account_type,
            status=AccountStatus.ACTIVE,
            created_at=datetime.now(),
            last_used=None,
            rate_limit=rate_limit,
            capabilities=capabilities,
            priority=priority,
            api_key=None,  # Will be set by user
            encrypted_config=None,
            usage_stats={
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0.0,
                'last_reset': datetime.now().isoformat()
            }
        )
        
        self.accounts[account_id] = account_info
        await self._save_accounts()
        
        # Create account-specific directory
        account_dir = self.accounts_dir / account_id
        account_dir.mkdir(exist_ok=True)
        
        logger.info(f"Created account: {account_id} ({name})")
        return account_id
    
    async def set_api_key(self, account_id: str, api_key: str) -> bool:
        """
        Set API key for an account
        
        Args:
            account_id: Account ID
            api_key: API key
            
        Returns:
            True if successful, False otherwise
        """
        if account_id not in self.accounts:
            logger.error(f"Account not found: {account_id}")
            return False
        
        account_info = self.accounts[account_id]
        account_info.api_key = api_key
        
        await self._save_accounts()
        logger.info(f"Set API key for account: {account_id}")
        return True
    
    async def set_account_config(self, account_id: str, config: Dict[str, Any]) -> bool:
        """
        Set encrypted configuration for an account
        
        Args:
            account_id: Account ID
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if account_id not in self.accounts:
            logger.error(f"Account not found: {account_id}")
            return False
        
        account_info = self.accounts[account_id]
        encrypted_config = self.cipher.encrypt(json.dumps(config).encode())
        account_info.encrypted_config = encrypted_config
        
        await self._save_accounts()
        logger.info(f"Set encrypted config for account: {account_id}")
        return True
    
    async def get_account_config(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get decrypted configuration for an account
        
        Args:
            account_id: Account ID
            
        Returns:
            Configuration dictionary or None
        """
        if account_id not in self.accounts:
            return None
        
        account_info = self.accounts[account_id]
        if not account_info.encrypted_config:
            return None
        
        try:
            decrypted_config = self.cipher.decrypt(account_info.encrypted_config)
            return json.loads(decrypted_config.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt config for account {account_id}: {e}")
            return None
    
    async def update_usage_stats(self, account_id: str, success: bool, response_time: float) -> None:
        """
        Update usage statistics for an account
        
        Args:
            account_id: Account ID
            success: Whether the request was successful
            response_time: Response time in seconds
        """
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
        
        account_info.last_used = datetime.now()
        await self._save_accounts()
    
    async def check_rate_limit(self, account_id: str) -> Tuple[bool, Optional[int]]:
        """
        Check if account has exceeded rate limits
        
        Args:
            account_id: Account ID
            
        Returns:
            (allowed, seconds_to_wait)
        """
        if account_id not in self.accounts:
            return False, None
        
        account_info = self.accounts[account_id]
        
        # Get rate limit configuration
        rate_limit_config = self._get_rate_limit_config(account_info.rate_limit)
        if not rate_limit_config:
            return True, None
        
        # Clean old requests (older than window)
        current_time = datetime.now()
        window_seconds = rate_limit_config['window_seconds']
        self.rate_limits[account_id] = [
            req_time for req_time in self.rate_limits[account_id]
            if current_time - req_time < timedelta(seconds=window_seconds)
        ]
        
        # Check if within limits
        max_requests = rate_limit_config['max_requests']
        current_requests = len(self.rate_limits[account_id])
        
        if current_requests >= max_requests:
            # Calculate wait time
            oldest_request = min(self.rate_limits[account_id])
            wait_time = window_seconds - int((current_time - oldest_request).total_seconds())
            return False, max(0, wait_time)
        
        # Add current request
        self.rate_limits[account_id].append(current_time)
        return True, None
    
    def _get_rate_limit_config(self, rate_limit_type: str) -> Optional[Dict[str, int]]:
        """Get rate limit configuration by type"""
        if not self.config or 'rate_limits' not in self.config:
            # Default rate limits
            return {
                'max_requests': 60,
                'window_seconds': 3600  # 1 hour
            }
        
        return self.config['rate_limits'].get(rate_limit_type)
    
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
        
        await self._save_accounts()
        logger.info(f"Suspended account {account_id}: {reason}")
        return True
    
    async def activate_account(self, account_id: str) -> bool:
        """Activate a suspended account"""
        if account_id not in self.accounts:
            return False
        
        account_info = self.accounts[account_id]
        account_info.status = AccountStatus.ACTIVE
        
        await self._save_accounts()
        logger.info(f"Activated account {account_id}")
        return True
    
    async def delete_account(self, account_id: str) -> bool:
        """Delete an account"""
        if account_id not in self.accounts:
            return False
        
        # Remove from registry
        del self.accounts[account_id]
        if account_id in self.rate_limits:
            del self.rate_limits[account_id]
        
        # Remove from disk
        account_dir = self.accounts_dir / account_id
        if account_dir.exists():
            import shutil
            shutil.rmtree(account_dir)
        
        await self._save_accounts()
        logger.info(f"Deleted account {account_id}")
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
                'priority': account_info.priority,
                'capabilities': account_info.capabilities,
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
            await self.delete_account(account_id)
            deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired accounts")
        
        return deleted_count


async def main():
    """Main entry point for testing"""
    manager = AgentAccountManager()
    await manager.initialize()
    
    # Example usage
    print("Agent Account Manager initialized")
    
    # List existing accounts
    accounts = await manager.list_accounts()
    print(f"Found {len(accounts)} accounts")
    
    # Create a new account
    new_account_id = await manager.create_account(
        name="test_subagent",
        account_type=AccountType.SUBAGENT,
        capabilities=["testing", "analysis"],
        priority=2
    )
    
    print(f"Created new account: {new_account_id}")
    
    # Get usage report
    report = await manager.get_usage_report()
    print(f"Usage report: {json.dumps(report, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())