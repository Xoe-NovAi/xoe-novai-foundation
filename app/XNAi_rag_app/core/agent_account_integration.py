"""
Agent Account Integration for XNAi RAG Stack

Integrates the account manager with the existing agent system,
providing seamless account switching and context propagation.

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from .account_manager import AccountManager, AccountInfo, get_account_manager
from .dependencies import get_redis_client

# Lazy imports for optional dependencies — prevents crash if not installed
try:
    from .agent_bus import AgentBusClient
    _HAS_AGENT_BUS = True
except ImportError:
    _HAS_AGENT_BUS = False
    AgentBusClient = None

try:
    from .security.knowledge_access import (
        KnowledgeAccessController,
        KnowledgeOperation,
        KnowledgePermission,
    )
    _HAS_KNOWLEDGE_ACCESS = True
except (ImportError, SyntaxError):
    _HAS_KNOWLEDGE_ACCESS = False
    KnowledgeAccessController = None
    KnowledgeOperation = None

logger = logging.getLogger(__name__)

# Operation string to KnowledgeOperation mapping
OPERATION_MAP = {}
if _HAS_KNOWLEDGE_ACCESS and KnowledgeOperation is not None:
    OPERATION_MAP = {
        "execute_task": KnowledgeOperation.READ,
        "read": KnowledgeOperation.READ,
        "query": KnowledgeOperation.QUERY,
        "search": KnowledgeOperation.SEARCH,
        "write": KnowledgeOperation.WRITE,
        "ingest": KnowledgeOperation.INGEST,
        "update": KnowledgeOperation.UPDATE,
        "delete": KnowledgeOperation.DELETE,
        "admin": KnowledgeOperation.ADMIN,
    }


class AgentAccountContext:
    """Context manager for agent account operations"""
    
    def __init__(self, agent_id: str, account_manager: AccountManager):
        self.agent_id = agent_id
        self.account_manager = account_manager
        self.original_account: Optional[str] = None
        self.redis_client = None
    
    async def __aenter__(self):
        """Enter context and save current account"""
        self.original_account = self.account_manager.current_account
        
        # Get Redis client for context storage
        try:
            self.redis_client = get_redis_client()
        except Exception as e:
            logger.warning(f"Could not connect to Redis for context storage: {e}")
        
        # Store agent context
        if self.redis_client:
            context_key = f"agent_context:{self.agent_id}"
            context_data = {
                "agent_id": self.agent_id,
                "original_account": self.original_account,
                "entered_at": datetime.now().isoformat()
            }
            
            try:
                self.redis_client.setex(context_key, 3600, str(context_data))  # 1 hour TTL
            except Exception as e:
                logger.warning(f"Could not store agent context: {e}")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original account"""
        if self.original_account and self.account_manager.current_account != self.original_account:
            try:
                await self.account_manager.switch_account(self.original_account)
                logger.info(f"Restored original account {self.original_account} for agent {self.agent_id}")
            except Exception as e:
                logger.error(f"Failed to restore original account for agent {self.agent_id}: {e}")
        
        # Clean up context storage
        if self.redis_client:
            try:
                context_key = f"agent_context:{self.agent_id}"
                self.redis_client.delete(context_key)
            except Exception as e:
                logger.warning(f"Could not clean up agent context: {e}")


class AgentAccountManager:
    """Enhanced agent account management with IAM context awareness"""
    
    def __init__(self):
        self.account_manager = None
        self._access_controller = None
        self._agent_bus = None
        self.logger = logger.getChild("AgentAccountManager")
    
    async def initialize(self):
        """Initialize the agent account manager with IAM and Agent Bus"""
        self.account_manager = await get_account_manager()

        # Initialize KnowledgeAccessController if available
        if _HAS_KNOWLEDGE_ACCESS and KnowledgeAccessController is not None:
            try:
                self._access_controller = KnowledgeAccessController()
                self.logger.info("IAM KnowledgeAccessController initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize KnowledgeAccessController: {e}")

        self.logger.info("Agent account manager initialized")
    
    async def get_current_account_for_agent(self, agent_id: str) -> Optional[AccountInfo]:
        """Get current account for an agent"""
        if not self.account_manager:
            await self.initialize()
        
        return self.account_manager.get_current_account()
    
    async def switch_account_for_agent(self, agent_id: str, account_id: str) -> bool:
        """Switch account for an agent with context preservation"""
        if not self.account_manager:
            await self.initialize()
        
        # Create context manager to preserve original account
        async with AgentAccountContext(agent_id, self.account_manager):
            success = await self.account_manager.switch_account(account_id)
            
            if success:
                self.logger.info(f"Agent {agent_id} switched to account {account_id}")
                
                # Publish account switch event
                await self._publish_account_switch_event(agent_id, account_id)
            
            return success
    
    async def get_recommended_account_for_agent(self, agent_id: str, task_type: str = "general") -> Optional[AccountInfo]:
        """Get recommended account for agent task"""
        if not self.account_manager:
            await self.initialize()
        
        return await self.account_manager.get_recommended_account(task_type)
    
    async def execute_with_account(self, agent_id: str, account_id: str, task_func, *args, **kwargs):
        """
        Execute a task function with a specific account
        
        Args:
            agent_id: Agent identifier
            account_id: Account to use for the task
            task_func: Function to execute
            *args, **kwargs: Arguments for the task function
            
        Returns:
            Result of the task function
        """
        if not self.account_manager:
            await self.initialize()
        
        async with AgentAccountContext(agent_id, self.account_manager):
            # Switch to the specified account
            success = await self.account_manager.switch_account(account_id)
            
            if not success:
                raise Exception(f"Failed to switch to account {account_id}")
            
            # Execute the task
            try:
                result = await task_func(*args, **kwargs)
                
                # Update usage statistics
                await self.account_manager.update_usage_stats(account_id, True, 0.0)  # TODO: measure response time
                
                return result
                
            except Exception as e:
                # Update usage statistics for failed request
                await self.account_manager.update_usage_stats(account_id, False, 0.0)
                raise e
    
    async def execute_with_recommended_account(self, agent_id: str, task_func, task_type: str = "general", *args, **kwargs):
        """
        Execute a task function with the recommended account
        
        Args:
            agent_id: Agent identifier
            task_func: Function to execute
            task_type: Type of task
            *args, **kwargs: Arguments for the task function
            
        Returns:
            Result of the task function
        """
        if not self.account_manager:
            await self.initialize()
        
        # Get recommended account
        recommended_account = await self.get_recommended_account_for_agent(agent_id, task_type)
        
        if not recommended_account:
            raise Exception("No suitable account available for task")
        
        return await self.execute_with_account(agent_id, recommended_account.account_id, task_func, *args, **kwargs)
    
    async def get_agent_account_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive account status for an agent"""
        if not self.account_manager:
            await self.initialize()
        
        current_account = self.account_manager.get_current_account()
        
        return {
            "agent_id": agent_id,
            "current_account": current_account.account_id if current_account else None,
            "account_details": current_account.to_dict() if current_account else None,
            "available_accounts": [
                acc.to_dict() for acc in await self.account_manager.list_accounts()
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    async def validate_agent_account_access(self, agent_id: str, account_id: str, operation: str) -> bool:
        """
        Validate that an agent has access to perform an operation on an account.

        Checks:
        1. Account exists and is active
        2. Account has remaining quota
        3. IAM KnowledgeAccessController permission check (if available)

        Args:
            agent_id: Agent identifier (used as DID prefix: did:xnai:{agent_id})
            account_id: Account identifier
            operation: Operation to validate (read, write, query, etc.)

        Returns:
            True if access is granted
        """
        if not self.account_manager:
            await self.initialize()

        # Check if account exists
        account = await self.account_manager.get_account_status(account_id)
        if not account:
            self.logger.warning(f"Account {account_id} not found for agent {agent_id}")
            return False

        # Check account status
        if account.status != "active":
            self.logger.warning(f"Account {account_id} is not active for agent {agent_id}")
            return False

        # Check quota availability
        if account.quota_remaining <= 0:
            self.logger.warning(f"Account {account_id} has no remaining quota for agent {agent_id}")
            return False

        # IAM permission check via KnowledgeAccessController
        if self._access_controller is not None and _HAS_KNOWLEDGE_ACCESS:
            try:
                # Map operation string to KnowledgeOperation enum
                knowledge_op = OPERATION_MAP.get(operation.lower())
                if knowledge_op is None:
                    self.logger.warning(
                        f"Unknown operation '{operation}' for IAM check, defaulting to READ"
                    )
                    knowledge_op = KnowledgeOperation.READ

                # Build agent DID from agent_id
                agent_did = f"did:xnai:{agent_id}" if not agent_id.startswith("did:") else agent_id

                # Check access (require_verified=False for graceful degradation)
                decision = await self._access_controller.check_access(
                    agent_did=agent_did,
                    operation=knowledge_op,
                    resource=account_id,
                    require_verified=False,
                )

                if not decision.allowed:
                    self.logger.warning(
                        f"IAM denied {operation} for agent {agent_id} on account {account_id}: "
                        f"{decision.reason}"
                    )
                    return False

                self.logger.debug(
                    f"IAM granted {operation} for agent {agent_id} on account {account_id}"
                )

            except Exception as e:
                # Graceful degradation — if IAM check fails, allow with warning
                self.logger.warning(
                    f"IAM check failed for agent {agent_id}, allowing with warning: {e}"
                )
        else:
            self.logger.debug(
                "KnowledgeAccessController not available, skipping IAM permission check"
            )

        return True
    
    async def _publish_account_switch_event(self, agent_id: str, account_id: str):
        """Publish account switch event to Agent Bus via Redis Streams."""
        try:
            if _HAS_AGENT_BUS and AgentBusClient is not None:
                # Build agent DID
                agent_did = f"did:xnai:{agent_id}" if not agent_id.startswith("did:") else agent_id

                async with AgentBusClient(agent_did) as bus:
                    await bus.send_task(
                        target_did="*",  # Broadcast
                        task_type="account_switch",
                        payload={
                            "agent_id": agent_id,
                            "account_id": account_id,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                    self.logger.info(
                        f"Account switch event published to Agent Bus: "
                        f"{agent_id} -> {account_id}"
                    )
            else:
                self.logger.info(
                    f"Agent {agent_id} switched to account {account_id} "
                    f"(Agent Bus not available, event not published)"
                )

        except Exception as e:
            # Non-fatal — log and continue, the switch itself succeeded
            self.logger.warning(f"Failed to publish account switch event: {e}")


class AccountAwareAgent:
    """Base class for agents that are aware of account management"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.account_manager = AgentAccountManager()
        self.logger = logger.getChild(f"AccountAwareAgent[{agent_id}]")
    
    async def initialize(self):
        """Initialize the agent with account management"""
        await self.account_manager.initialize()
        self.logger.info(f"Agent {self.agent_id} initialized with account management")
    
    async def get_current_account(self) -> Optional[AccountInfo]:
        """Get current account for this agent"""
        return await self.account_manager.get_current_account_for_agent(self.agent_id)
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch to a different account"""
        return await self.account_manager.switch_account_for_agent(self.agent_id, account_id)
    
    async def get_recommended_account(self, task_type: str = "general") -> Optional[AccountInfo]:
        """Get recommended account for task"""
        return await self.account_manager.get_recommended_account_for_agent(self.agent_id, task_type)
    
    async def execute_with_account(self, account_id: str, task_func, *args, **kwargs):
        """Execute task with specific account"""
        return await self.account_manager.execute_with_account(self.agent_id, account_id, task_func, *args, **kwargs)
    
    async def execute_with_recommended_account(self, task_func, task_type: str = "general", *args, **kwargs):
        """Execute task with recommended account"""
        return await self.account_manager.execute_with_recommended_account(self.agent_id, task_func, task_type, *args, **kwargs)
    
    async def get_account_status(self) -> Dict[str, Any]:
        """Get comprehensive account status"""
        return await self.account_manager.get_agent_account_status(self.agent_id)
    
    async def validate_account_access(self, account_id: str, operation: str) -> bool:
        """Validate account access"""
        return await self.account_manager.validate_agent_account_access(self.agent_id, account_id, operation)
    
    async def perform_task(self, task_func, task_type: str = "general", preferred_account: Optional[str] = None, *args, **kwargs):
        """
        Perform a task with intelligent account selection
        
        Args:
            task_func: Function to execute
            task_type: Type of task
            preferred_account: Preferred account (if None, use recommended)
            *args, **kwargs: Arguments for the task function
            
        Returns:
            Result of the task function
        """
        if preferred_account:
            # Validate preferred account
            if await self.validate_account_access(preferred_account, "execute_task"):
                return await self.execute_with_account(preferred_account, task_func, *args, **kwargs)
            else:
                self.logger.warning(f"Preferred account {preferred_account} not accessible, falling back to recommendation")
        
        # Use recommended account
        return await self.execute_with_recommended_account(task_func, task_type, *args, **kwargs)


# Global agent account manager instance
agent_account_manager = AgentAccountManager()


async def get_agent_account_manager() -> AgentAccountManager:
    """Get the global agent account manager instance"""
    if not agent_account_manager.account_manager:
        await agent_account_manager.initialize()
    return agent_account_manager