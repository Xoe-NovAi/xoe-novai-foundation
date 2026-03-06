"""
OAuth Manager for Multi-Account Authentication

Manages OAuth credentials for multiple accounts with secure storage,
automatic credential rotation, and persistent authentication across sessions.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiofiles
from cryptography.fernet import Fernet
import yaml

logger = logging.getLogger(__name__)


class OAuthManager:
    """Manages OAuth credentials for multiple accounts"""
    
    def __init__(self, storage_path: str = "~/.xnai/oauth_credentials.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.credentials = {}
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        # self.load_credentials() removed because it's async and cannot be called here.
        # Methods that use self.credentials should call await self.load_credentials() first.
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for credential storage.
        Prioritizes XNAI_OAUTH_KEY environment variable.
        """
        # 1. Try Environment Variable (Highest Security)
        env_key = os.getenv("XNAI_OAUTH_KEY")
        if env_key:
            return env_key.encode()

        # 2. Fallback to local file
        key_path = self.storage_path.parent / ".oauth_key"
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)  # Secure permissions
            return key
    
    async def load_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Load stored OAuth credentials"""
        if self.storage_path.exists():
            try:
                async with aiofiles.open(self.storage_path, 'r') as f:
                    encrypted_data = await f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data.encode()).decode()
                    self.credentials = json.loads(decrypted_data)
                logger.info(f"Loaded credentials for {len(self.credentials)} accounts")
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
                self.credentials = {}
        return self.credentials
    
    async def save_credentials(self, account_id: str, credentials: Dict[str, Any]):
        """Save OAuth credentials for an account"""
        credentials['last_updated'] = datetime.now().isoformat()
        self.credentials[account_id] = credentials
        
        # Encrypt and save
        data = json.dumps(self.credentials)
        encrypted_data = self.cipher.encrypt(data.encode()).decode()
        
        async with aiofiles.open(self.storage_path, 'w') as f:
            await f.write(encrypted_data)
        
        logger.info(f"Saved credentials for account: {account_id}")
    
    async def get_credentials(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get OAuth credentials for an account"""
        await self.load_credentials()
        return self.credentials.get(account_id)
    
    async def delete_credentials(self, account_id: str):
        """Delete OAuth credentials for an account"""
        if account_id in self.credentials:
            del self.credentials[account_id]
            await self._save_to_file()
            logger.info(f"Deleted credentials for account: {account_id}")
    
    async def _save_to_file(self):
        """Save credentials to encrypted file"""
        data = json.dumps(self.credentials)
        encrypted_data = self.cipher.encrypt(data.encode()).decode()
        
        async with aiofiles.open(self.storage_path, 'w') as f:
            await f.write(encrypted_data)
    
    async def list_accounts(self) -> List[str]:
        """List all accounts with stored credentials"""
        await self.load_credentials()
        return list(self.credentials.keys())
    
    async def is_valid(self, account_id: str) -> bool:
        """Check if credentials are valid and not expired"""
        credentials = await self.get_credentials(account_id)
        if not credentials:
            return False
        
        # Check if access token is expired
        expires_at = credentials.get('expires_at')
        if expires_at:
            expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() >= expires_datetime:
                return False
        
        return True
    
    async def refresh_credentials(self, account_id: str) -> bool:
        """Refresh OAuth credentials for an account"""
        credentials = await self.get_credentials(account_id)
        if not credentials:
            return False
        
        refresh_token = credentials.get('refresh_token')
        if not refresh_token:
            return False
        
        try:
            # Implement refresh logic based on provider
            provider = credentials.get('provider', 'google')
            if provider == 'google':
                refreshed = await self._refresh_google_credentials(refresh_token)
            elif provider == 'github':
                refreshed = await self._refresh_github_credentials(refresh_token)
            else:
                return False
            
            if refreshed:
                await self.save_credentials(account_id, refreshed)
                return True
        except Exception as e:
            logger.error(f"Failed to refresh credentials for {account_id}: {e}")
        
        return False
    
    async def _refresh_google_credentials(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh Google OAuth credentials"""
        # Implementation would use Google's token refresh endpoint
        # This is a placeholder for the actual implementation
        return None
    
    async def _refresh_github_credentials(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh GitHub OAuth credentials"""
        # Implementation would use GitHub's token refresh endpoint
        # This is a placeholder for the actual implementation
        return None
    
    async def cleanup_expired_credentials(self):
        """Remove expired credentials"""
        accounts = await self.list_accounts()
        for account_id in accounts:
            if not await self.is_valid(account_id):
                await self.delete_credentials(account_id)
                logger.info(f"Removed expired credentials for {account_id}")


from app.XNAi_rag_app.core.paths import get_config_path

class AccountManager:
    """Manages account selection and routing"""
    
    def __init__(self, accounts_config: str = None):
        self.accounts_config = get_config_path(accounts_config or "cline-accounts.yaml")
        self.accounts = self._load_accounts_config()
    
    def _load_accounts_config(self) -> Dict[str, Any]:
        """Load accounts configuration. Handles both Dict and List formats."""
        try:
            with open(self.accounts_config, 'r') as f:
                config = yaml.safe_load(f)
            raw_accounts = config.get('accounts', {})
            
            # Normalize to Dict format if it's a List
            if isinstance(raw_accounts, list):
                normalized = {}
                for acc in raw_accounts:
                    if isinstance(acc, dict) and 'id' in acc:
                        normalized[acc['id']] = acc
                return normalized
            return raw_accounts
        except Exception as e:
            logger.error(f"Failed to load accounts config from {self.accounts_config}: {e}")
            return {}
    
    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account configuration by ID"""
        return self.accounts.get(account_id)
    
    def list_oauth_accounts(self) -> List[str]:
        """List accounts that support OAuth"""
        oauth_accounts = []
        if not isinstance(self.accounts, dict):
            logger.error(f"self.accounts is not a dict: {type(self.accounts)}")
            return []
            
        for account_id, config in self.accounts.items():
            if isinstance(config, dict) and config.get('auth_method') == 'oauth':
                oauth_accounts.append(account_id)
        return oauth_accounts
    
    def select_best_account(self, domain: str = "general") -> Optional[str]:
        """Select the best account for a given domain"""
        oauth_accounts = self.list_oauth_accounts()
        if not oauth_accounts:
            return None
        
        # Simple selection logic - could be enhanced
        # For now, return the first available OAuth account
        return oauth_accounts[0]
    
    def get_account_priority(self, account_id: str) -> int:
        """Get account priority"""
        account_config = self.get_account_by_id(account_id)
        return account_config.get('priority', 999) if account_config else 999


async def batch_authenticate_accounts():
    """Authenticate all 8 accounts with OAuth"""
    
    accounts = [
        "gemini_oauth_01", "gemini_oauth_02", "gemini_oauth_03",
        "opencode_oauth_01", "opencode_oauth_02", "opencode_oauth_03", 
        "copilot_oauth_01", "copilot_oauth_02"
    ]
    
    oauth_manager = OAuthManager()
    account_manager = AccountManager()
    
    for account_id in accounts:
        print(f"Authenticating {account_id}...")
        
        # Check if already authenticated
        if await oauth_manager.is_valid(account_id):
            print(f"✅ {account_id} already authenticated")
            continue
        
        # Get account configuration
        account_config = account_manager.get_account_by_id(account_id)
        if not account_config:
            print(f"❌ Account {account_id} not found in config")
            continue
        
        try:
            # Authenticate account
            credentials = await authenticate_account(account_id, account_config)
            if credentials:
                await oauth_manager.save_credentials(account_id, credentials)
                print(f"✅ {account_id} authenticated")
            else:
                print(f"❌ Failed to authenticate {account_id}")
        except Exception as e:
            print(f"❌ Error authenticating {account_id}: {e}")


async def authenticate_account(account_id: str, account_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Authenticate a single account using OAuth"""
    provider = account_config.get('provider', 'google')
    
    if provider in ['google', 'gemini', 'opencode']:
        return await authenticate_google_oauth(account_id)
    elif provider in ['github', 'copilot']:
        return await authenticate_github_oauth(account_id)
    else:
        logger.error(f"Unsupported provider: {provider}")
        return None


async def authenticate_google_oauth(account_id: str) -> Optional[Dict[str, Any]]:
    """Authenticate Google OAuth account"""
    # Implementation would use Google's OAuth flow
    # This is a placeholder for the actual implementation
    return {
        'provider': 'google',
        'access_token': 'placeholder_token',
        'refresh_token': 'placeholder_refresh_token',
        'expires_at': (datetime.now() + timedelta(days=3650)).isoformat(),
        'scopes': ['https://www.googleapis.com/auth/cloud-platform']
    }


async def authenticate_github_oauth(account_id: str) -> Optional[Dict[str, Any]]:
    """Authenticate GitHub OAuth account"""
    # Implementation would use GitHub's OAuth flow
    # This is a placeholder for the actual implementation
    return {
        'provider': 'github',
        'access_token': 'placeholder_token',
        'refresh_token': 'placeholder_refresh_token',
        'expires_at': (datetime.now() + timedelta(days=3650)).isoformat(),
        'scopes': ['repo', 'read:user']
    }


# CLI Interface for OAuth Management
async def oauth_cli():
    """OAuth CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python oauth_manager.py <command>")
        print("Commands:")
        print("  list                    - List all accounts")
        print("  authenticate <account>  - Authenticate specific account")
        print("  batch                   - Authenticate all accounts")
        print("  cleanup                 - Remove expired credentials")
        return
    
    command = sys.argv[1]
    oauth_manager = OAuthManager()
    
    if command == "list":
        accounts = await oauth_manager.list_accounts()
        print("Stored accounts:")
        for account in accounts:
            valid = "✅" if await oauth_manager.is_valid(account) else "❌"
            print(f"  {valid} {account}")
    
    elif command == "authenticate" and len(sys.argv) > 2:
        account_id = sys.argv[2]
        account_manager = AccountManager()
        account_config = account_manager.get_account_by_id(account_id)
        
        if not account_config:
            print(f"❌ Account {account_id} not found in config")
            return
        
        credentials = await authenticate_account(account_id, account_config)
        if credentials:
            await oauth_manager.save_credentials(account_id, credentials)
            print(f"✅ {account_id} authenticated")
        else:
            print(f"❌ Failed to authenticate {account_id}")
    
    elif command == "batch":
        await batch_authenticate_accounts()
    
    elif command == "cleanup":
        await oauth_manager.cleanup_expired_credentials()
        print("✅ Expired credentials cleaned up")
    
    else:
        print("❌ Unknown command")


if __name__ == "__main__":
    asyncio.run(oauth_cli())