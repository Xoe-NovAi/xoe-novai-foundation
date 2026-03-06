"""
Rate Limit Handler and Automatic Account Rotation

This module provides intelligent rate limit detection and automatic account rotation
for OpenCode CLI and other providers. It addresses the critical issue where the system
doesn't automatically rotate accounts when hitting rate limits, causing context loss.

Key Features:
- Real-time rate limit detection from CLI responses
- Automatic account rotation on HTTP 429 errors
- Context preservation across account switches
- Smart fallback strategies
- Integration with existing multi-account system

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import json
import logging
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
from collections import defaultdict

import anyio

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ContextLossError(Exception):
    """Custom exception for context loss"""
    def __init__(self, message: str, session_id: Optional[str] = None):
        super().__init__(message)
        self.session_id = session_id


class AccountStatus(Enum):
    """Account status for rotation"""
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    EXHAUSTED = "exhausted"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


@dataclass
class AccountState:
    """Account state for rate limiting and rotation"""
    account_id: str
    provider: str
    status: AccountStatus = AccountStatus.HEALTHY
    last_rate_limit: Optional[datetime] = None
    rate_limit_count: int = 0
    retry_after: Optional[int] = None
    context_preserved: bool = True
    last_used: Optional[datetime] = None
    tokens_used: int = 0
    consecutive_failures: int = 0


class RateLimitDetector:
    """Detect rate limits from CLI responses"""
    
    # Common rate limit patterns across providers
    RATE_LIMIT_PATTERNS = {
        "http_429": [
            r"429.*Too Many Requests",
            r"Rate limit exceeded",
            r"Too many requests",
            r"Request limit exceeded",
            r"API rate limit",
            r"rateLimitExceeded",
            r"quota exceeded",
        ],
        "deepseek": [
            r"DeepSeek.*rate limit",
            r"DeepSeek.*quota",
            r"DeepSeek.*429",
        ],
        "minimax": [
            r"Minimax.*rate limit",
            r"Minimax.*quota",
            r"Minimax.*429",
        ],
        "opencode": [
            r"OpenCode.*rate limit",
            r"OpenCode.*quota",
            r"OpenCode.*429",
        ],
        "context_loss": [
            r"session.*lost",
            r"context.*lost",
            r"session.*expired",
            r"session.*reset",
            r"new session",
            r"session.*not found",
        ]
    }
    
    @classmethod
    def detect_rate_limit(cls, response_text: str) -> Tuple[bool, str]:
        """Detect if response indicates a rate limit error"""
        response_lower = response_text.lower()
        
        # Check context loss patterns first to avoid false positives
        for pattern in cls.RATE_LIMIT_PATTERNS["context_loss"]:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return False, "context_loss"
        
        # Then check rate limit patterns in order of specificity
        # Check provider-specific patterns first, then general patterns
        for error_type in ["deepseek", "minimax", "opencode", "http_429"]:
            if error_type in cls.RATE_LIMIT_PATTERNS:
                for pattern in cls.RATE_LIMIT_PATTERNS[error_type]:
                    if re.search(pattern, response_lower, re.IGNORECASE):
                        return True, error_type
        
        return False, "unknown"
    
    @classmethod
    def detect_context_loss(cls, response_text: str) -> bool:
        """Detect if response indicates context loss"""
        response_lower = response_text.lower()
        
        for pattern in cls.RATE_LIMIT_PATTERNS["context_loss"]:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def extract_retry_after(cls, response_text: str) -> Optional[int]:
        """Extract retry-after time from response"""
        # Look for retry-after patterns
        patterns = [
            r"retry[-\s]?after[:\s]*(\d+)",
            r"try again in (\d+) seconds",
            r"wait (\d+) seconds",
            r"retry in (\d+) seconds",
            r"retry after (\d+) seconds",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None


class ContextManager:
    """Manage context preservation across account switches"""
    
    def __init__(self, context_dir: Optional[str] = None):
        self.context_dir = Path(context_dir or "~/.opencode/context").expanduser()
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def save_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Save context for a session"""
        try:
            context_file = self.context_dir / f"{session_id}.json"
            with open(context_file, 'w') as f:
                json.dump(context, f, indent=2)
            
            self.active_sessions[session_id] = context
            logger.debug(f"Context saved for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save context for {session_id}: {e}")
    
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context for a session"""
        try:
            # Try active sessions first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Try file system
            context_file = self.context_dir / f"{session_id}.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    context = json.load(f)
                self.active_sessions[session_id] = context
                logger.debug(f"Context loaded for session: {session_id}")
                return context
            
            logger.warning(f"No context found for session: {session_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to load context for {session_id}: {e}")
            return None
    
    def clear_context(self, session_id: str) -> None:
        """Clear context for a session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            context_file = self.context_dir / f"{session_id}.json"
            if context_file.exists():
                context_file.unlink()
            
            logger.debug(f"Context cleared for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear context for {session_id}: {e}")
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a session, creating if needed"""
        context = self.load_context(session_id)
        if context is None:
            context = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "context_window": [],
                "metadata": {}
            }
            self.save_context(session_id, context)
        
        return context
    
    def add_message_to_context(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the session context"""
        context = self.get_session_context(session_id)
        
        # Add message
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        context["messages"].append(message)
        
        # Update context window (keep last 10 messages for context)
        context["context_window"] = context["messages"][-10:]
        
        self.save_context(session_id, context)
    
    def get_context_prompt(self, session_id: str) -> str:
        """Get context prompt for continuing conversation"""
        context = self.load_context(session_id)
        if not context or not context.get("context_window"):
            return ""
        
        # Build context prompt
        context_messages = []
        for msg in context["context_window"]:
            role = msg["role"].upper()
            content = msg["content"][:500]  # Limit context length
            context_messages.append(f"{role}: {content}")
        
        return "\n".join(context_messages)


class AccountRotator:
    """Manage account rotation and state"""
    
    def __init__(self, accounts: List[Dict[str, Any]]):
        self.accounts = {acc["account_id"]: AccountState(
            account_id=acc["account_id"],
            provider=acc["provider"]
        ) for acc in accounts}
        
        self.rotation_index = 0
        self.rate_limit_backoff = defaultdict(lambda: 300)  # 5 minutes default
        self.max_consecutive_failures = 3
    
    def get_next_available_account(self, preferred_account: Optional[str] = None) -> Optional[str]:
        """Get next available account, respecting rate limits"""
        now = datetime.now()
        
        # Try preferred account first if specified
        if preferred_account and preferred_account in self.accounts:
            account_state = self.accounts[preferred_account]
            if self._is_account_available(account_state, now):
                return preferred_account
        
        # Try all accounts in rotation
        for i in range(len(self.accounts)):
            idx = (self.rotation_index + i) % len(self.accounts)
            account_id = list(self.accounts.keys())[idx]
            account_state = self.accounts[account_id]
            
            if self._is_account_available(account_state, now):
                self.rotation_index = (idx + 1) % len(self.accounts)
                return account_id
        
        return None
    
    def _is_account_available(self, account_state: AccountState, now: datetime) -> bool:
        """Check if account is available for use"""
        if account_state.status == AccountStatus.HEALTHY:
            return True
        
        if account_state.status == AccountStatus.RATE_LIMITED:
            if account_state.retry_after:
                # Use retry-after time if available
                return now >= account_state.last_rate_limit + timedelta(seconds=account_state.retry_after)
            else:
                # Use exponential backoff
                backoff_time = self.rate_limit_backoff[account_state.account_id]
                return now >= account_state.last_rate_limit + timedelta(seconds=backoff_time)
        
        if account_state.status == AccountStatus.EXHAUSTED:
            # Check if enough time has passed for quota reset
            # For weekly quotas, reset on Sunday
            if now.weekday() == 6 and now.hour >= 0:  # Sunday 00:00 UTC
                account_state.status = AccountStatus.HEALTHY
                account_state.rate_limit_count = 0
                account_state.consecutive_failures = 0
                return True
            return False
        
        if account_state.status == AccountStatus.SUSPENDED:
            return False
        
        return True
    
    def mark_rate_limit(self, account_id: str, retry_after: Optional[int] = None) -> None:
        """Mark account as rate limited"""
        if account_id in self.accounts:
            account_state = self.accounts[account_id]
            account_state.status = AccountStatus.RATE_LIMITED
            account_state.last_rate_limit = datetime.now()
            account_state.rate_limit_count += 1
            account_state.retry_after = retry_after
            account_state.consecutive_failures += 1
            
            # Exponential backoff
            current_backoff = self.rate_limit_backoff[account_id]
            self.rate_limit_backoff[account_id] = min(current_backoff * 2, 3600)  # Max 1 hour
            
            logger.warning(
                f"Account {account_id} rate limited (count: {account_state.rate_limit_count}, "
                f"retry_after: {retry_after}s, backoff: {self.rate_limit_backoff[account_id]}s)"
            )
    
    def mark_exhausted(self, account_id: str) -> None:
        """Mark account as exhausted"""
        if account_id in self.accounts:
            account_state = self.accounts[account_id]
            account_state.status = AccountStatus.EXHAUSTED
            account_state.consecutive_failures += 1
            logger.warning(f"Account {account_id} marked as exhausted")
    
    def mark_suspended(self, account_id: str) -> None:
        """Mark account as suspended"""
        if account_id in self.accounts:
            account_state = self.accounts[account_id]
            account_state.status = AccountStatus.SUSPENDED
            account_state.consecutive_failures += 1
            logger.warning(f"Account {account_id} marked as suspended")
    
    def mark_success(self, account_id: str) -> None:
        """Mark account as successful"""
        if account_id in self.accounts:
            account_state = self.accounts[account_id]
            account_state.status = AccountStatus.HEALTHY
            account_state.consecutive_failures = 0
            account_state.last_used = datetime.now()
            logger.debug(f"Account {account_id} marked as successful")
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Get account statistics"""
        stats = {
            "total_accounts": len(self.accounts),
            "healthy": 0,
            "rate_limited": 0,
            "exhausted": 0,
            "suspended": 0,
            "unknown": 0,
            "accounts": {}
        }
        
        now = datetime.now()
        for account_id, account_state in self.accounts.items():
            status = account_state.status.value
            stats[status] += 1
            
            # Calculate time until available
            time_until_available = 0
            if account_state.status == AccountStatus.RATE_LIMITED:
                if account_state.retry_after:
                    time_until_available = max(0, account_state.retry_after - int((now - account_state.last_rate_limit).total_seconds()))
                else:
                    backoff = self.rate_limit_backoff[account_id]
                    time_until_available = max(0, backoff - int((now - account_state.last_rate_limit).total_seconds()))
            
            stats["accounts"][account_id] = {
                "status": status,
                "rate_limit_count": account_state.rate_limit_count,
                "consecutive_failures": account_state.consecutive_failures,
                "last_used": account_state.last_used.isoformat() if account_state.last_used else None,
                "time_until_available": time_until_available
            }
        
        return stats


class SmartDispatcher:
    """Smart dispatcher with automatic rate limit handling and context preservation"""
    
    def __init__(
        self,
        accounts: List[Dict[str, Any]],
        context_manager: Optional[ContextManager] = None
    ):
        self.accounts = accounts
        self.account_rotator = AccountRotator(accounts)
        self.context_manager = context_manager or ContextManager()
        self.rate_limit_detector = RateLimitDetector()
        
        # Session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.max_retries = 3
        self.context_preservation_enabled = True
    
    async def dispatch_with_rotation(
        self,
        task: str,
        session_id: Optional[str] = None,
        preferred_account: Optional[str] = None,
        context_window: Optional[List[Dict[str, str]]] = None,
        timeout_sec: float = 60.0
    ) -> Dict[str, Any]:
        """
        Dispatch task with automatic rate limit handling and context preservation
        
        Args:
            task: The task to execute
            session_id: Session ID for context preservation
            preferred_account: Preferred account to use first
            context_window: Context messages to include
            timeout_sec: Timeout for the operation
        
        Returns:
            Dict with success status, output, account used, and metadata
        """
        
        # Initialize session context
        if session_id:
            session_context = self.context_manager.get_session_context(session_id)
            if context_window:
                # Add provided context to session
                for msg in context_window:
                    self.context_manager.add_message_to_context(
                        session_id, msg["role"], msg["content"]
                    )
        else:
            session_id = f"session_{int(time.time())}"
            session_context = self.context_manager.get_session_context(session_id)
        
        # Add current task to context
        self.context_manager.add_message_to_context(session_id, "user", task)
        
        # Get context prompt for continuation
        context_prompt = ""
        if self.context_preservation_enabled:
            context_prompt = self.context_manager.get_context_prompt(session_id)
        
        # Prepare enhanced task with context
        enhanced_task = task
        if context_prompt:
            enhanced_task = f"Context:\n{context_prompt}\n\nTask:\n{task}"
        
        # Attempt dispatch with rotation
        for attempt in range(self.max_retries):
            # Get next available account
            account_id = self.account_rotator.get_next_available_account(preferred_account)
            if not account_id:
                return {
                    "success": False,
                    "error": "No available accounts",
                    "session_id": session_id,
                    "attempt": attempt + 1,
                    "total_attempts": self.max_retries
                }
            
            try:
                # Execute with the selected account
                result = await self._execute_with_account(
                    account_id, enhanced_task, session_id, timeout_sec
                )
                
                if result["success"]:
                    # Success - mark account as healthy
                    self.account_rotator.mark_success(account_id)
                    
                    # Add assistant response to context
                    if result.get("output"):
                        self.context_manager.add_message_to_context(
                            session_id, "assistant", result["output"]
                        )
                    
                    return {
                        "success": True,
                        "output": result["output"],
                        "account_used": account_id,
                        "session_id": session_id,
                        "attempt": attempt + 1,
                        "context_preserved": True
                    }
                else:
                    # Handle failure
                    error_msg = result.get("error", "")
                    is_rate_limit, error_type = self.rate_limit_detector.detect_rate_limit(error_msg)
                    
                    if is_rate_limit:
                        retry_after = self.rate_limit_detector.extract_retry_after(error_msg)
                        self.account_rotator.mark_rate_limit(account_id, retry_after)
                        
                        # Check if context was lost
                        if self.rate_limit_detector.detect_context_loss(error_msg):
                            logger.warning(f"Context loss detected for session {session_id}")
                            # Try to recover context
                            await self._recover_context(session_id, account_id)
                    else:
                        # Other failure types
                        self.account_rotator.mark_exhausted(account_id)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed for account {account_id}: {error_msg}"
                    )
                    
            except Exception as e:
                logger.error(f"Exception during dispatch attempt {attempt + 1}: {e}")
                self.account_rotator.mark_exhausted(account_id)
        
        # All attempts failed
        return {
            "success": False,
            "error": "All accounts failed after rotation",
            "session_id": session_id,
            "attempt": self.max_retries,
            "total_attempts": self.max_retries,
            "account_stats": self.account_rotator.get_account_stats()
        }
    
    async def _execute_with_account(
        self,
        account_id: str,
        task: str,
        session_id: str,
        timeout_sec: float
    ) -> Dict[str, Any]:
        """Execute task with specific account"""
        try:
            # Determine provider and execute
            account_info = next(acc for acc in self.accounts if acc["account_id"] == account_id)
            provider = account_info["provider"]
            
            if provider == "opencode":
                return await self._execute_opencode(account_id, task, session_id, timeout_sec)
            elif provider == "deepseek":
                return await self._execute_deepseek(account_id, task, session_id, timeout_sec)
            elif provider == "minimax":
                return await self._execute_minimax(account_id, task, session_id, timeout_sec)
            else:
                return await self._execute_generic(account_id, task, session_id, timeout_sec)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "account_id": account_id
            }
    
    async def _execute_opencode(
        self,
        account_id: str,
        task: str,
        session_id: str,
        timeout_sec: float
    ) -> Dict[str, Any]:
        """Execute task with OpenCode CLI"""
        try:
            # Use XDG_DATA_HOME to isolate each instance and preserve session
            import tempfile
            with tempfile.TemporaryDirectory(prefix=f"opencode-{session_id}-") as tmpdir:
                cmd = ["opencode", "chat", "--json", task]
                
                env = self._get_provider_env(account_id)
                env["XDG_DATA_HOME"] = tmpdir  # Isolate auth and session data
                
                result = await anyio.to_thread.run_blocking(
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout_sec,
                        env=env,
                    )
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "output": result.stdout,
                        "account_id": account_id
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr,
                        "account_id": account_id
                    }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "OpenCode timeout",
                "account_id": account_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "account_id": account_id
            }
    
    async def _execute_deepseek(
        self,
        account_id: str,
        task: str,
        session_id: str,
        timeout_sec: float
    ) -> Dict[str, Any]:
        """Execute task with DeepSeek CLI"""
        try:
            cmd = ["deepseek", "chat", "--json", task]
            env = self._get_provider_env(account_id)
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                )
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "account_id": account_id
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "account_id": account_id
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "DeepSeek timeout",
                "account_id": account_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "account_id": account_id
            }
    
    async def _execute_minimax(
        self,
        account_id: str,
        task: str,
        session_id: str,
        timeout_sec: float
    ) -> Dict[str, Any]:
        """Execute task with Minimax CLI"""
        try:
            cmd = ["minimax", "chat", "--json", task]
            env = self._get_provider_env(account_id)
            
            result = await anyio.to_thread.run_blocking(
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                )
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "account_id": account_id
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "account_id": account_id
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Minimax timeout",
                "account_id": account_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "account_id": account_id
            }
    
    async def _execute_generic(
        self,
        account_id: str,
        task: str,
        session_id: str,
        timeout_sec: float
    ) -> Dict[str, Any]:
        """Generic execution for other providers"""
        # This would be implemented for other providers
        return {
            "success": False,
            "error": f"Provider not implemented for account {account_id}",
            "account_id": account_id
        }
    
    def _get_provider_env(self, account_id: str) -> Dict[str, str]:
        """Get environment variables for provider authentication"""
        import os
        env = os.environ.copy()
        
        # Inject provider tokens from config
        # This would load from the account registry
        account_info = next(acc for acc in self.accounts if acc["account_id"] == account_id)
        
        # Set provider-specific environment variables
        if account_info["provider"] == "opencode":
            env["OPENCODE_API_KEY"] = account_info.get("api_key", "")
        elif account_info["provider"] == "deepseek":
            env["DEEPSEEK_API_KEY"] = account_info.get("api_key", "")
        elif account_info["provider"] == "minimax":
            env["MINIMAX_API_KEY"] = account_info.get("api_key", "")
        
        return env
    
    async def _recover_context(self, session_id: str, failed_account: str) -> bool:
        """Attempt to recover context after account failure"""
        try:
            # Try to load context from backup
            context = self.context_manager.load_context(session_id)
            if context:
                logger.info(f"Context recovered for session {session_id}")
                return True
            
            # Try to recover from file system
            context_dir = Path.home() / ".opencode" / "sessions"
            if context_dir.exists():
                for session_file in context_dir.glob(f"{session_id}*"):
                    try:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                        self.context_manager.save_context(session_id, session_data)
                        logger.info(f"Context recovered from {session_file} for session {session_id}")
                        return True
                    except Exception:
                        continue
            
            logger.warning(f"Context recovery failed for session {session_id}")
            return False
            
        except Exception as e:
            logger.error(f"Context recovery error for session {session_id}: {e}")
            return False
    
    def get_rotation_stats(self) -> Dict[str, Any]:
        """Get rotation statistics"""
        return {
            "account_stats": self.account_rotator.get_account_stats(),
            "active_sessions": len(self.active_sessions),
            "context_manager_stats": {
                "context_dir": str(self.context_manager.context_dir),
                "active_sessions": len(self.context_manager.active_sessions)
            }
        }