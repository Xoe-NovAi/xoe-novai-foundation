# Omega Stack API Reference

**Created by:** Cline Kat-Coder  
**Session:** Chat Session #20260311-1545  
**Date:** March 11, 2026  
**Version:** 1.0  
**Quality Assessment:** ✅ Comprehensive - Complete API documentation with examples

This document provides comprehensive API documentation for the Omega Stack system.

## Table of Contents

1. [Core Components](#core-components)
2. [Account Management](#account-management)
3. [Agent Communication](#agent-communication)
4. [Memory Systems](#memory-systems)
5. [Provider Integration](#provider-integration)
6. [Authentication & Security](#authentication--security)
7. [Utilities](#utilities)

## Core Components

### Agent Bus

The Agent Bus provides centralized communication between agents using Redis Streams.

#### Class: AgentBusClient

```python
class AgentBusClient:
    """AnyIO-wrapped Redis Stream Client for multi-agent task distribution with IA2 signatures."""
    
    def __init__(self, agent_did: str, stream_name: str = "xnai:agent_bus"):
        """Initialize Agent Bus client.
        
        Args:
            agent_did: Agent DID (Decentralized Identifier)
            stream_name: Redis stream name (default: "xnai:agent_bus")
        """
    
    async def __aenter__(self) -> AgentBusClient:
        """Async context manager entry."""
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
    
    async def check_kill_switch(self) -> bool:
        """Check for emergency stop signals.
        
        Returns:
            True if emergency_stop is active
        """
    
    async def send_emergency_stop(self, reason: str = "Manual Trigger") -> str:
        """Broadcast emergency stop to all agents.
        
        Args:
            reason: Reason for emergency stop
            
        Returns:
            Task ID of the emergency stop message
        """
    
    async def send_task(self, target_did: str, task_type: str, payload: Dict[str, Any]) -> str:
        """Send a signed task to an agent.
        
        Args:
            target_did: Target agent DID
            task_type: Type of task
            payload: Task payload
            
        Returns:
            Task ID
        """
    
    async def fetch_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Fetch tasks assigned to this agent.
        
        Args:
            count: Maximum number of tasks to fetch
            
        Returns:
            List of tasks
        """
    
    async def acknowledge_task(self, task_id: str):
        """Acknowledge task completion.
        
        Args:
            task_id: Task ID to acknowledge
        """
    
    async def emit_session_bloat(self, session_id: str, token_count: int):
        """Broadcast session bloat event.
        
        Args:
            session_id: Session identifier
            token_count: Current token count
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

async def agent_worker():
    async with AgentBusClient("agent:worker:001") as bus:
        # Check for emergency stop
        if await bus.check_kill_switch():
            return
        
        # Fetch tasks
        tasks = await bus.fetch_tasks(count=5)
        
        for task in tasks:
            # Process task
            result = await process_task(task)
            
            # Acknowledge completion
            await bus.acknowledge_task(task["id"])
```

### Domain Router

The Domain Router intelligently routes tasks based on domain expertise and provider capabilities.

#### Class: DomainRouter

```python
class DomainRouter:
    """Intelligent task routing based on domain expertise and provider capabilities."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize domain router.
        
        Args:
            config_path: Path to domain routing configuration
        """
    
    async def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate provider.
        
        Args:
            task: Task to route
            
        Returns:
            Routed task with provider information
        """
    
    async def get_provider_for_domain(self, domain: str) -> Optional[str]:
        """Get best provider for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Provider name or None
        """
    
    async def get_domain_experts(self, domain: str) -> List[str]:
        """Get list of experts for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of expert agent IDs
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.domain_router import DomainRouter

async def route_task_example():
    router = DomainRouter()
    
    task = {
        "type": "code_review",
        "content": "Review this Python code for security issues",
        "domain": "security"
    }
    
    routed_task = await router.route_task(task)
    print(f"Task routed to provider: {routed_task['provider']}")
```

## Account Management

### Account Manager

Centralized account management with multi-provider support and quota tracking.

#### Class: AccountManager

```python
class AccountManager:
    """Manages multiple provider accounts with proper account switching and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize account manager.
        
        Args:
            config_path: Path to account configuration
        """
    
    async def initialize(self) -> None:
        """Initialize the account manager."""
    
    async def get_current_account(self) -> Optional[AccountInfo]:
        """Get the currently active account.
        
        Returns:
            Current account information or None
        """
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch to a different account.
        
        Args:
            account_id: Account ID to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
    
    async def get_recommended_account(self, task_type: str = "general") -> Optional[AccountInfo]:
        """Get best account for task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            Recommended account or None
        """
    
    async def create_account(self, name: str, account_type: AccountType, email: str,
                           provider: str, quota_limit: int, models_preferred: List[str],
                           priority: int = 1) -> str:
        """Create a new account.
        
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
    
    async def get_usage_report(self) -> Dict[str, Any]:
        """Get usage report for all accounts.
        
        Returns:
            Usage report dictionary
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.account_manager import AccountManager

async def account_management_example():
    manager = AccountManager()
    await manager.initialize()
    
    # Get current account
    current = await manager.get_current_account()
    print(f"Current account: {current.name}")
    
    # Switch account
    success = await manager.switch_account("antigravity-01")
    if success:
        print("Account switched successfully")
    
    # Get recommended account for code task
    recommended = await manager.get_recommended_account("code")
    print(f"Recommended for code: {recommended.name}")
```

### Account Selector

Intelligent account selection with hybrid weighted scoring.

#### Class: AccountSelector

```python
class AccountSelector:
    """Intelligent account selector for load balancing."""
    
    def __init__(self, accounts: List[str], strategy: SelectionStrategy = SelectionStrategy.HYBRID):
        """Initialize account selector.
        
        Args:
            accounts: List of account IDs
            strategy: Selection strategy
        """
    
    def update_quota(self, account_id: str, quota_remaining: int, quota_limit: int) -> None:
        """Update quota for account.
        
        Args:
            account_id: Account ID
            quota_remaining: Remaining quota
            quota_limit: Total quota limit
        """
    
    def select_account(self, force_strategy: Optional[SelectionStrategy] = None) -> SelectionResult:
        """Select best account based on strategy.
        
        Args:
            force_strategy: Override default strategy
            
        Returns:
            Selection result with account and reasoning
        """
    
    def get_statistics(self) -> Dict:
        """Get selection statistics.
        
        Returns:
            Statistics dictionary
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.account_selector import AccountSelector, SelectionStrategy

async def account_selection_example():
    accounts = ["antigravity-01", "antigravity-02", "antigravity-03"]
    selector = AccountSelector(accounts, strategy=SelectionStrategy.HYBRID)
    
    # Update quota
    selector.update_quota("antigravity-01", 400000, 500000)
    
    # Select account
    result = selector.select_account()
    print(f"Selected account: {result.selected_account}")
    print(f"Reasoning: {result.reasoning}")
```

## Memory Systems

### Agent Memory

Unified persistent memory system with short-term, long-term, and procedural memory.

#### Class: AgentMemory

```python
class AgentMemory:
    """Main interface for agent memory."""
    
    def __init__(self, provider: MemoryProvider):
        """Initialize agent memory.
        
        Args:
            provider: Memory backend provider
        """
    
    async def snapshot(self, agent_id: str, session_id: str, state_data: Dict[str, Any]):
        """Create a durable checkpoint of agent state.
        
        Args:
            agent_id: Agent identifier
            session_id: Session identifier
            state_data: State data to snapshot
        """
    
    async def learn_fact(self, agent_id: str, fact: str, category: str = "general", confidence: float = 0.5):
        """Record a long-term fact.
        
        Args:
            agent_id: Agent identifier
            fact: Fact content
            category: Fact category
            confidence: Confidence level (0.0-1.0)
        """
    
    async def recall_facts(self, agent_id: str, category: Optional[str] = None) -> List[AgentFact]:
        """Retrieve relevant facts for an agent.
        
        Args:
            agent_id: Agent identifier
            category: Optional fact category filter
            
        Returns:
            List of relevant facts
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.agent_memory import AgentMemory, LocalMemoryProvider

async def memory_example():
    provider = LocalMemoryProvider()
    memory = AgentMemory(provider)
    
    # Create snapshot
    state = {"current_task": "code_review", "context": "Python security"}
    await memory.snapshot("agent-001", "session-123", state)
    
    # Learn fact
    await memory.learn_fact("agent-001", "Python uses indentation for blocks", "programming", 0.9)
    
    # Recall facts
    facts = await memory.recall_facts("agent-001", "programming")
    for fact in facts:
        print(f"Fact: {fact.fact_content} (confidence: {fact.confidence})")
```

### Context Synchronization

Synchronized context management across agent interactions.

#### Class: ContextSyncEngine

```python
class ContextSyncEngine:
    """Synchronizes context across agent interactions."""
    
    def __init__(self, agent_did: str):
        """Initialize context sync engine.
        
        Args:
            agent_did: Agent DID
        """
    
    async def sync_context(self, context: Dict[str, Any]) -> bool:
        """Synchronize context with other agents.
        
        Args:
            context: Context to synchronize
            
        Returns:
            True if sync successful
        """
    
    async def get_shared_context(self, context_key: str) -> Optional[Dict[str, Any]]:
        """Get shared context.
        
        Args:
            context_key: Context key
            
        Returns:
            Shared context or None
        """
    
    async def update_context(self, context_key: str, updates: Dict[str, Any]) -> bool:
        """Update shared context.
        
        Args:
            context_key: Context key
            updates: Context updates
            
        Returns:
            True if update successful
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.context_sync import ContextSyncEngine

async def context_sync_example():
    sync_engine = ContextSyncEngine("agent:sync:001")
    
    # Sync context
    context = {"project": "omega-stack", "focus": "documentation"}
    success = await sync_engine.sync_context(context)
    
    # Get shared context
    shared = await sync_engine.get_shared_context("project-omega")
    
    # Update context
    updates = {"status": "in_progress", "progress": 50}
    await sync_engine.update_context("project-omega", updates)
```

## Provider Integration

### Multi-Provider Dispatcher

Intelligent task dispatching across multiple providers with fallback mechanisms.

#### Class: MultiProviderDispatcher

```python
class MultiProviderDispatcher:
    """Dispatch tasks to multiple providers with intelligent fallback."""
    
    def __init__(self, email_accounts: Optional[List[str]] = None,
                 antigravity_accounts: Optional[List[str]] = None,
                 enable_rate_limit_handling: bool = True):
        """Initialize multi-provider dispatcher.
        
        Args:
            email_accounts: GitHub email accounts for rotation
            antigravity_accounts: Antigravity accounts for rotation
            enable_rate_limit_handling: Enable rate limit detection
        """
    
    async def dispatch(self, task: str, context_size: int = 10000,
                      task_type: str = "general", model_preference: Optional[str] = None,
                      timeout_sec: float = 60.0) -> Dict[str, Any]:
        """Dispatch task to best available provider.
        
        Args:
            task: Task prompt
            context_size: Estimated context size
            task_type: Type of task
            model_preference: Preferred model
            timeout_sec: Timeout in seconds
            
        Returns:
            Dispatch result
        """
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers.
        
        Returns:
            Provider status dictionary
        """
    
    async def rotate_accounts(self, provider: str) -> bool:
        """Rotate accounts for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if rotation successful
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher

async def dispatch_example():
    dispatcher = MultiProviderDispatcher()
    
    # Dispatch task
    result = await dispatcher.dispatch(
        task="Analyze this code for security vulnerabilities",
        context_size=50000,
        task_type="security",
        model_preference="antigravity_opus"
    )
    
    if result["success"]:
        print(f"Task completed: {result['output']}")
    else:
        print(f"Task failed: {result['error']}")
```

### Antigravity Dispatcher

Specialized dispatcher for Antigravity provider with account rotation.

#### Class: AntigravityDispatcher

```python
class AntigravityDispatcher:
    """Dispatch tasks to Antigravity models via OpenCode CLI."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize Antigravity dispatcher.
        
        Args:
            config_file: Path to Antigravity credentials
        """
    
    async def dispatch(self, task: str, context_size: int = 10000,
                      task_type: str = "general", model_preference: Optional[str] = None,
                      timeout_sec: float = 60.0) -> Dict[str, Any]:
        """Dispatch task to Antigravity.
        
        Args:
            task: Task prompt
            context_size: Estimated context size
            task_type: Type of task
            model_preference: Specific model preference
            timeout_sec: Timeout in seconds
            
        Returns:
            Dispatch result
        """
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get quota status across all accounts.
        
        Returns:
            Quota status dictionary
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.antigravity_dispatcher import AntigravityDispatcher

async def antigravity_example():
    dispatcher = AntigravityDispatcher()
    
    # Dispatch with large context
    result = await dispatcher.dispatch(
        task="Analyze this entire codebase architecture",
        context_size=500000,  # Large context for full analysis
        task_type="reasoning",
        model_preference="gemini-3.1-pro"
    )
    
    print(f"Quota status: {dispatcher.get_quota_status()}")
```

## Authentication & Security

### OAuth Manager

Secure OAuth credential management with automatic rotation.

#### Class: OAuthManager

```python
class OAuthManager:
    """Manages OAuth credentials for multiple accounts."""
    
    def __init__(self, storage_path: str = "~/.xnai/oauth_credentials.json"):
        """Initialize OAuth manager.
        
        Args:
            storage_path: Path to encrypted credential storage
        """
    
    async def load_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Load stored OAuth credentials.
        
        Returns:
            Dictionary of credentials
        """
    
    async def save_credentials(self, account_id: str, credentials: Dict[str, Any]):
        """Save OAuth credentials for an account.
        
        Args:
            account_id: Account identifier
            credentials: OAuth credentials
        """
    
    async def get_credentials(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get OAuth credentials for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Credentials or None
        """
    
    async def is_valid(self, account_id: str) -> bool:
        """Check if credentials are valid and not expired.
        
        Args:
            account_id: Account identifier
            
        Returns:
            True if valid
        """
    
    async def refresh_credentials(self, account_id: str) -> bool:
        """Refresh OAuth credentials for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            True if refresh successful
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.oauth_manager import OAuthManager

async def oauth_example():
    oauth_manager = OAuthManager()
    
    # Load credentials
    credentials = await oauth_manager.load_credentials()
    
    # Check validity
    is_valid = await oauth_manager.is_valid("gemini_oauth_01")
    
    # Refresh if needed
    if not is_valid:
        await oauth_manager.refresh_credentials("gemini_oauth_01")
```

### Token Validation

Pre-injection token validation for all provider accounts.

#### Class: TokenValidator

```python
class TokenValidator:
    """Validates and refreshes provider credentials."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize token validator.
        
        Args:
            config_file: Path to credentials configuration
        """
    
    def validate_token(self, provider: str, account: str, token: Optional[str] = None) -> TokenStatus:
        """Validate a token for the specified provider and account.
        
        Args:
            provider: Provider type
            account: Account identifier
            token: Token to validate (optional)
            
        Returns:
            Token validation status
        """
    
    def validate_all_accounts(self) -> Dict[str, TokenStatus]:
        """Validate all configured accounts.
        
        Returns:
            Dictionary of validation results
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.token_validation import TokenValidator

def token_validation_example():
    validator = TokenValidator()
    
    # Validate specific token
    status = validator.validate_token("opencode", "account_1")
    print(f"Token status: {status.result.value}")
    
    # Validate all accounts
    results = validator.validate_all_accounts()
    for key, status in results.items():
        print(f"{key}: {status.result.value}")
```

## Utilities

### Quota Checker

Real-time quota monitoring and management across all providers.

#### Class: QuotaChecker

```python
class QuotaChecker:
    """Monitors and manages quotas across all providers."""
    
    def __init__(self):
        """Initialize quota checker."""
    
    async def get_quota(self, provider: str, account_id: str) -> Optional[QuotaInfo]:
        """Get current quota for provider and account.
        
        Args:
            provider: Provider name
            account_id: Account identifier
            
        Returns:
            Quota information or None
        """
    
    async def update_quota_usage(self, provider: str, account_id: str, tokens_used: int) -> bool:
        """Update quota usage.
        
        Args:
            provider: Provider name
            account_id: Account identifier
            tokens_used: Tokens used in operation
            
        Returns:
            True if update successful
        """
    
    async def get_quota_alerts(self) -> List[Dict[str, Any]]:
        """Get quota alerts.
        
        Returns:
            List of quota alerts
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.quota_checker import QuotaChecker

async def quota_example():
    checker = QuotaChecker()
    
    # Get quota
    quota = await checker.get_quota("antigravity", "antigravity-01")
    if quota:
        print(f"Remaining: {quota.tokens_remaining}/{quota.tokens_limit}")
    
    # Update usage
    await checker.update_quota_usage("antigravity", "antigravity-01", 1000)
    
    # Check alerts
    alerts = await checker.get_quota_alerts()
    for alert in alerts:
        print(f"Alert: {alert['message']}")
```

### Configuration Manager

Centralized configuration management with validation and hot-reloading.

#### Class: ConfigManager

```python
class ConfigManager:
    """Manages application configuration with validation and hot-reloading."""
    
    def __init__(self, config_path: str):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
    
    async def load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid
        """
    
    async def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration.
        
        Args:
            updates: Configuration updates
            
        Returns:
            True if update successful
        """
    
    async def watch_config(self, callback: Callable[[Dict[str, Any]], None]):
        """Watch for configuration changes.
        
        Args:
            callback: Function to call on changes
        """
```

#### Usage Example

```python
from app.XNAi_rag_app.core.config_manager import ConfigManager

async def config_example():
    config_manager = ConfigManager("config/config.toml")
    
    # Load config
    config = await config_manager.load_config()
    
    # Validate
    is_valid = await config_manager.validate_config(config)
    
    # Update
    await config_manager.update_config({"debug": True})
    
    # Watch for changes
    async def on_change(new_config):
        print(f"Config changed: {new_config}")
    
    await config_manager.watch_config(on_change)
```

## Error Handling

### Custom Exceptions

The Omega Stack defines several custom exceptions for specific error conditions:

```python
class OmegaStackError(Exception):
    """Base exception for Omega Stack errors."""
    pass

class AccountNotFoundError(OmegaStackError):
    """Raised when an account is not found."""
    pass

class QuotaExhaustedError(OmegaStackError):
    """Raised when account quota is exhausted."""
    pass

class ProviderError(OmegaStackError):
    """Raised when a provider operation fails."""
    pass

class AuthenticationError(OmegaStackError):
    """Raised when authentication fails."""
    pass

class RateLimitError(OmegaStackError):
    """Raised when rate limits are exceeded."""
    pass
```

#### Usage Example

```python
from app.XNAi_rag_app.core.exceptions import (
    AccountNotFoundError, QuotaExhaustedError, ProviderError
)

async def error_handling_example():
    try:
        result = await dispatcher.dispatch(task="example task")
        if not result["success"]:
            raise ProviderError(result["error"])
    except AccountNotFoundError as e:
        print(f"Account not found: {e}")
    except QuotaExhaustedError as e:
        print(f"Quota exhausted: {e}")
        # Handle account rotation
    except ProviderError as e:
        print(f"Provider error: {e}")
        # Handle fallback to other providers
```

## Best Practices

### Async/Await Patterns

Always use `anyio` for async operations to ensure compatibility:

```python
import anyio
from typing import AsyncGenerator

async def async_operation() -> AsyncGenerator[str, None]:
    """Example async function using anyio."""
    async with anyio.create_task_group() as tg:
        # Perform async operations
        yield "result"
```

### Error Handling

Implement comprehensive error handling:

```python
async def robust_operation():
    try:
        # Operation logic
        result = await some_async_operation()
        return result
    except AuthenticationError:
        # Handle authentication issues
        logger.warning("Authentication failed, attempting refresh")
        await refresh_credentials()
        return await robust_operation()  # Retry once
    except QuotaExhaustedError:
        # Handle quota issues
        logger.warning("Quota exhausted, switching accounts")
        await switch_to_backup_account()
        return await robust_operation()  # Retry with new account
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise
```

### Logging

Use structured logging with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

async def operation_with_logging():
    logger.info("Starting operation", extra={"operation": "example"})
    
    try:
        result = await perform_operation()
        logger.info("Operation completed successfully", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Operation failed", extra={"error": str(e)}, exc_info=True)
        raise
```

### Type Hints

Always provide comprehensive type hints:

```python
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

@dataclass
class TaskResult:
    success: bool
    output: Optional[str]
    error: Optional[str]
    metadata: Dict[str, Any]

async def process_task(task: Dict[str, Any]) -> TaskResult:
    """Process a task and return result.
    
    Args:
        task: Task to process
        
    Returns:
        Task processing result
    """
    # Implementation
    pass
```

This API reference provides comprehensive documentation for all major components of the Omega Stack. For more detailed information about specific classes or methods, refer to the inline documentation and type hints in the source code.