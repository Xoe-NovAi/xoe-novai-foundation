# Omega Stack Development Guide

**Created by:** Cline Kat-Coder  
**Session:** Chat Session #20260311-1545  
**Date:** March 11, 2026  
**Version:** 1.0  
**Quality Assessment:** ✅ Comprehensive - Complete development setup and best practices

This guide provides comprehensive instructions for developing with the Omega Stack, including setup, best practices, and advanced development techniques.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Performance Optimization](#performance-optimization)
8. [Deployment](#deployment)
9. [Advanced Development](#advanced-development)
10. [Troubleshooting](#troubleshooting)

## 🔱 Omega Stack: Metropolis Standards (v4.1.3)

### 1. The Oikos Cognitive Mesh
All complex agentic deliberations MUST use the **Oikos Mastermind** protocol.
- **Internal Access**: Port 8006.
- **Secure Ingress**: Unified entry via Caddy on Port 8002.
- **Architecture**: Asynchronous status polling for long-running sessions.
- **Handshake**: Clients MUST use the `wait_for_service` handshake.

### 2. Rainbow Rotation Protocol
To bypass rate limits and achieve high bandwidth:
- **Authentication**: Use `OAuthManager` for on-the-fly Fernet decryption.
- **Master Key**: Requires `XNAI_OAUTH_KEY` or `~/.xnai/.oauth_key`.
- **Rotation**: Automatic switching between high-quota OAuth accounts and API keys.
- **Fallback**: Graceful transition to local Ollama (Port 11434).

### 3. Permissions & Identity
- **Standard**: UID 1000 (arcana-novai) is the global identity.
- **Hardening**: ALL containers MUST run as `user: "1000:1000"`.
- **Mounts**: Use the `:Z` flag for SELinux-aware volume mapping.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.10 or higher
- **Docker**: Latest version with Docker Compose
- **Git**: Latest version
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB free space

### Python Dependencies

Install the required Python packages:

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Install production dependencies
pip install -r requirements/prod.txt

# Install optional dependencies
pip install -r requirements/optional.txt
```

### Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Xoe-NovAi/xoe-novai-foundation.git
   cd xoe-novai-foundation
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

3. **Initialize Development Environment**
   ```bash
   # Start development stack
   make dev-up
   
   # Initialize database
   make db-migrate
   
   # Set up initial configuration
   python scripts/setup_dev_environment.py
   ```

## Development Environment Setup

### Docker Development Environment

The Omega Stack uses Docker Compose for development environment management:

```bash
# Start all services
docker-compose -f infra/docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f infra/docker/docker-compose.dev.yml logs -f

# Stop services
docker-compose -f infra/docker/docker-compose.dev.yml down

# Clean up
docker-compose -f infra/docker/docker-compose.dev.yml down -v --remove-orphans
```

### Local Development Without Docker

For local development without Docker:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install postgresql redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis

# Create database
sudo -u postgres createdb omega_stack_dev
sudo -u postgres createuser omega_user

# Run application
python -m app.XNAi_rag_app.main
```

### IDE Configuration

#### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true
}
```

#### PyCharm Configuration

1. Open the project in PyCharm
2. Go to File → Settings → Project → Python Interpreter
3. Select your virtual environment
4. Install plugins: BlackConnect, Ruff
5. Configure code style to match Black formatting

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Project Structure

### Directory Organization

```
omega-stack/
├── app/                    # Main application code
│   └── XNAi_rag_app/       # Core RAG application
│       ├── __init__.py
│       ├── main.py         # Application entry point
│       ├── core/           # Core functionality
│       ├── services/       # Business logic services
│       ├── models/         # Data models
│       ├── api/            # API endpoints
│       └── utils/          # Utility functions
├── config/                 # Configuration files
│   ├── config.toml         # Main configuration
│   ├── logging.conf        # Logging configuration
│   └── schemas/            # Database schemas
├── docs/                   # Documentation
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── API_REFERENCE.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── tutorials/          # Step-by-step guides
├── infra/                  # Infrastructure as Code
│   ├── docker/             # Docker configurations
│   ├── kubernetes/         # Kubernetes manifests
│   └── terraform/          # Terraform configurations
├── scripts/                # Utility scripts
│   ├── setup_dev_environment.py
│   ├── migrate_database.py
│   └── deploy.sh
├── tests/                  # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── fixtures/           # Test data
│   └── conftest.py         # Test configuration
├── requirements/           # Python dependencies
│   ├── dev.txt             # Development dependencies
│   ├── prod.txt            # Production dependencies
│   └── optional.txt        # Optional dependencies
├── artifacts/              # Generated artifacts
├── data/                   # Data files
├── logs/                   # Log files
└── Makefile               # Build and development commands
```

### Core Modules

#### Core Functionality (`app/XNAi_rag_app/core/`)

- **`agent_bus.py`**: Inter-agent communication system
- **`account_manager.py`**: Multi-provider account management
- **`domain_router.py`**: Intelligent task routing
- **`memory_systems.py`**: Persistent memory management
- **`quota_checker.py`**: Real-time quota monitoring
- **`oauth_manager.py`**: OAuth credential management
- **`config_manager.py`**: Configuration management

#### Services (`app/XNAi_rag_app/services/`)

- **`agent_service.py`**: Agent orchestration and management
- **`provider_service.py`**: Provider integration services
- **`memory_service.py`**: Memory operations and management
- **`security_service.py`**: Authentication and authorization

#### API Endpoints (`app/XNAi_rag_app/api/`)

- **`v1/`**: Version 1 API endpoints
- **`v2/`**: Version 2 API endpoints (future)
- **`webhooks/`**: Webhook handlers
- **`admin/`**: Administrative endpoints

## Coding Standards

### Python Style Guide

We follow PEP 8 with additional guidelines:

#### Code Formatting

- **Line Length**: Maximum 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings
- **Imports**: Organize with isort

```python
# Good
from typing import Dict, List, Optional, Any
from datetime import datetime

# Bad
from typing import Dict,List,Optional,Any
from datetime import datetime
```

#### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_single_underscore`
- **Internal**: `__double_underscore`

```python
class ExampleClass:
    MAX_RETRIES = 3
    
    def __init__(self, name: str):
        self._internal_data = {}
        self.__private_data = []
    
    def public_method(self) -> None:
        pass
    
    def _internal_method(self) -> None:
        pass
```

#### Type Hints

Always use comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass

@dataclass
class Task:
    id: str
    name: str
    parameters: Dict[str, Any]
    created_at: datetime

async def process_tasks(tasks: List[Task]) -> AsyncGenerator[Task, None]:
    """Process a list of tasks.
    
    Args:
        tasks: List of tasks to process
        
    Yields:
        Processed tasks
    """
    for task in tasks:
        # Process task
        yield task
```

### Async/Await Patterns

Use `anyio` for async operations to ensure compatibility:

```python
import anyio
from typing import AsyncGenerator, Callable

async def async_operation() -> AsyncGenerator[str, None]:
    """Example async function using anyio."""
    async with anyio.create_task_group() as tg:
        # Perform async operations
        yield "result"

async def run_with_timeout(
    func: Callable, timeout: float, *args, **kwargs
) -> Any:
    """Run async function with timeout."""
    with anyio.move_on_after(timeout):
        return await func(*args, **kwargs)
    raise TimeoutError(f"Operation timed out after {timeout} seconds")
```

### Error Handling

Implement comprehensive error handling:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CustomError(Exception):
    """Base exception for custom errors."""
    pass

async def robust_operation() -> Optional[str]:
    """Example of robust error handling."""
    try:
        # Operation logic
        result = await some_async_operation()
        return result
    except AuthenticationError as e:
        logger.warning("Authentication failed", exc_info=True)
        await handle_authentication_failure()
        return None
    except NetworkError as e:
        logger.error("Network error occurred", exc_info=True)
        await retry_operation()
        return None
    except Exception as e:
        logger.critical("Unexpected error", exc_info=True)
        raise CustomError(f"Operation failed: {e}") from e
```

### Logging

Use structured logging with appropriate levels:

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def operation_with_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Example of structured logging."""
    logger.info(
        "Starting operation",
        extra={
            "operation": "data_processing",
            "data_size": len(data),
            "user_id": data.get("user_id")
        }
    )
    
    try:
        result = await process_data(data)
        
        logger.info(
            "Operation completed successfully",
            extra={
                "operation": "data_processing",
                "result_size": len(result),
                "processing_time": "1.5s"
            }
        )
        
        return result
    except Exception as e:
        logger.error(
            "Operation failed",
            extra={
                "operation": "data_processing",
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True
        )
        raise
```

## Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_account_manager.py
│   ├── test_agent_bus.py
│   ├── test_quota_checker.py
│   └── test_memory_systems.py
├── integration/            # Integration tests
│   ├── test_multi_provider.py
│   ├── test_oauth_flow.py
│   └── test_database_operations.py
├── fixtures/               # Test data and fixtures
│   ├── sample_accounts.json
│   ├── test_credentials.json
│   └── mock_responses/
└── conftest.py            # Test configuration
```

### Writing Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.XNAi_rag_app.core.account_manager import AccountManager
from app.XNAi_rag_app.core.account_selector import AccountSelector

@pytest.mark.asyncio
class TestAccountManager:
    """Test cases for AccountManager."""
    
    async def test_create_account(self):
        """Test account creation."""
        manager = AccountManager()
        
        # Mock dependencies
        with patch('app.XNAi_rag_app.core.account_manager.get_redis_client') as mock_redis:
            mock_redis.return_value = AsyncMock()
            
            # Test account creation
            account_id = await manager.create_account(
                name="test_account",
                account_type="user",
                email="test@example.com",
                provider="antigravity",
                quota_limit=500000
            )
            
            # Assertions
            assert account_id is not None
            assert "antigravity" in account_id
    
    async def test_switch_account(self):
        """Test account switching."""
        manager = AccountManager()
        
        # Mock dependencies
        with patch.object(manager, 'accounts', {
            'test_account': MagicMock(status='active', quota_remaining=1000)
        }):
            # Test account switch
            result = await manager.switch_account('test_account')
            
            # Assertions
            assert result is True
            assert manager.current_account == 'test_account'
    
    async def test_get_recommended_account(self):
        """Test account recommendation."""
        manager = AccountManager()
        
        # Mock accounts
        mock_account = MagicMock()
        mock_account.account_id = 'recommended_account'
        mock_account.quota_remaining = 500000
        
        with patch.object(manager, 'accounts', {
            'account1': MagicMock(quota_remaining=1000),
            'recommended_account': mock_account
        }):
            # Test recommendation
            recommended = await manager.get_recommended_account('general')
            
            # Assertions
            assert recommended.account_id == 'recommended_account'
```

### Writing Integration Tests

```python
import pytest
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

@pytest.mark.asyncio
class TestMultiProviderIntegration:
    """Integration tests for multi-provider functionality."""
    
    async def test_dispatch_with_fallback(self):
        """Test dispatch with provider fallback."""
        dispatcher = MultiProviderDispatcher()
        
        # Mock provider failures
        with patch('app.XNAi_rag_app.core.multi_provider_dispatcher.AntigravityDispatcher.dispatch') as mock_antigravity:
            mock_antigravity.return_value = {'success': False, 'error': 'Quota exhausted'}
            
            with patch('app.XNAi_rag_app.core.multi_provider_dispatcher.ClineDispatcher.dispatch') as mock_cline:
                mock_cline.return_value = {'success': True, 'output': 'Task completed'}
                
                # Test dispatch with fallback
                result = await dispatcher.dispatch(
                    task="Test task",
                    task_type="general"
                )
                
                # Assertions
                assert result['success'] is True
                assert result['output'] == 'Task completed'
                assert mock_antigravity.called
                assert mock_cline.called
    
    async def test_agent_bus_integration(self):
        """Test agent bus integration."""
        async with AgentBusClient("test_agent") as bus:
            # Test task sending
            task_id = await bus.send_task(
                target_did="worker:001",
                task_type="test",
                payload={"data": "test_data"}
            )
            
            # Test task fetching
            tasks = await bus.fetch_tasks(count=1)
            
            # Assertions
            assert task_id is not None
            assert len(tasks) == 1
            assert tasks[0]['payload']['data'] == 'test_data'
```

### Test Fixtures

Create reusable test fixtures:

```python
# tests/fixtures/accounts.py
import pytest
from app.XNAi_rag_app.core.account_manager import AccountInfo, AccountStatus, AccountType

@pytest.fixture
def sample_account():
    """Create a sample account for testing."""
    return AccountInfo(
        account_id="test_account_001",
        name="Test Account",
        account_type=AccountType.USER,
        status=AccountStatus.ACTIVE,
        created_at=datetime.now(),
        last_used=None,
        email="test@example.com",
        provider="antigravity",
        quota_remaining=500000,
        quota_limit=500000,
        models_preferred=["claude-opus", "gemini-pro"],
        priority=1,
        api_key="test_api_key",
        usage_stats={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
    )

@pytest.fixture
def multiple_accounts():
    """Create multiple accounts for testing."""
    return [
        AccountInfo(
            account_id="account_001",
            name="Account 1",
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            quota_remaining=400000,
            quota_limit=500000,
            priority=1
        ),
        AccountInfo(
            account_id="account_002",
            name="Account 2",
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            quota_remaining=300000,
            quota_limit=500000,
            priority=2
        ),
        AccountInfo(
            account_id="account_003",
            name="Account 3",
            account_type=AccountType.USER,
            status=AccountStatus.INACTIVE,
            quota_remaining=0,
            quota_limit=500000,
            priority=3
        )
    ]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_account_manager.py

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run integration tests
pytest tests/integration/

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_account_manager.py::TestAccountManager::test_create_account
```

## Debugging

### Development Tools

#### Logging Configuration

Configure detailed logging for development:

```python
# config/logging.conf
[loggers]
keys=root,omega_stack

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=detailedFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[logger_omega_stack]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=omega_stack
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=detailedFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/development.log',)

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

#### Debug Mode

Enable debug mode in development:

```python
# .env
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_PROFILING=true
```

#### Interactive Debugging

Use interactive debugging tools:

```python
import pdb
import ipdb

# Set breakpoints
def debug_function():
    pdb.set_trace()  # Python debugger
    # or
    ipdb.set_trace()  # IPython debugger
    
    # Your code here
    result = some_operation()
    return result
```

### Common Debugging Scenarios

#### Async/Await Issues

Debug async operations:

```python
import asyncio
import anyio
from contextlib import asynccontextmanager

@asynccontextmanager
async def debug_async_operation():
    """Debug async operation with timing."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        yield
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        raise
    finally:
        end_time = asyncio.get_event_loop().time()
        logger.debug(f"Async operation took {end_time - start_time:.2f} seconds")

# Usage
async def example_async_function():
    async with debug_async_operation():
        await some_async_operation()
```

#### Memory Issues

Debug memory usage:

```python
import tracemalloc
import gc

def debug_memory_usage():
    """Debug memory usage."""
    tracemalloc.start()
    
    # Your code here
    result = some_memory_intensive_operation()
    
    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
    
    # Force garbage collection
    gc.collect()
    
    return result
```

#### Database Issues

Debug database operations:

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log all SQL statements."""
    context._query_start_time = time.time()
    logger.debug(f"Query: {statement}")
    logger.debug(f"Parameters: {parameters}")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time."""
    total = time.time() - context._query_start_time
    logger.debug(f"Query executed in {total:.2f} seconds")
```

## Performance Optimization

### Async Optimization

Optimize async operations:

```python
import anyio
from typing import List, Callable, Any

async def optimized_batch_operation(
    items: List[Any],
    operation: Callable[[Any], Any],
    concurrency_limit: int = 10
) -> List[Any]:
    """Optimized batch operation with concurrency control."""
    
    results = []
    
    async def process_item(item: Any):
        """Process single item."""
        result = await operation(item)
        results.append(result)
    
    # Use semaphore to limit concurrency
    semaphore = anyio.Semaphore(concurrency_limit)
    
    async with anyio.create_task_group() as tg:
        for item in items:
            async with semaphore:
                tg.start_soon(process_item, item)
    
    return results
```

### Database Optimization

Optimize database operations:

```python
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select

async def optimized_query():
    """Optimized database query."""
    # Use eager loading to avoid N+1 queries
    query = select(Account).options(
        selectinload(Account.usage_stats),
        joinedload(Account.quota_info)
    ).where(Account.status == 'active')
    
    # Use pagination for large datasets
    paginated_query = query.offset(0).limit(100)
    
    # Execute query
    result = await session.execute(paginated_query)
    accounts = result.scalars().all()
    
    return accounts
```

### Caching Strategy

Implement caching for performance:

```python
import redis.asyncio as redis
import json
from functools import wraps

class CacheManager:
    """Redis-based caching manager."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache."""
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete value from cache."""
        await self.redis.delete(key)

def cached(ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cache_manager = CacheManager("redis://localhost:6379")
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=1800)  # Cache for 30 minutes
async def expensive_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Expensive operation with caching."""
    # Your expensive operation here
    return result
```

### Memory Management

Optimize memory usage:

```python
import gc
import weakref
from typing import Dict, Any, Optional

class MemoryManager:
    """Memory management utilities."""
    
    def __init__(self):
        self._weak_refs = weakref.WeakValueDictionary()
    
    def track_object(self, obj: Any, key: str):
        """Track object for memory management."""
        self._weak_refs[key] = obj
    
    def cleanup_memory(self):
        """Force garbage collection and cleanup."""
        gc.collect()
        
        # Remove dead weak references
        dead_keys = [k for k, v in self._weak_refs.items() if v is None]
        for key in dead_keys:
            del self._weak_refs[key]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "tracked_objects": len(self._weak_refs)
        }

# Usage
memory_manager = MemoryManager()

async def memory_intensive_operation():
    """Memory-intensive operation with management."""
    try:
        # Your memory-intensive operation
        result = await process_large_dataset()
        
        # Track result
        memory_manager.track_object(result, "latest_result")
        
        return result
    finally:
        # Cleanup if needed
        memory_manager.cleanup_memory()
```

## Deployment

### Development Deployment

Deploy to development environment:

```bash
# Build Docker images
docker-compose -f infra/docker/docker-compose.dev.yml build

# Start development stack
docker-compose -f infra/docker/docker-compose.dev.yml up -d

# Run migrations
docker-compose -f infra/docker/docker-compose.dev.yml exec app python scripts/migrate_database.py

# Verify deployment
curl http://localhost:8000/health
```

### Production Deployment

#### Docker Compose Production

```bash
# Build production images
docker-compose -f infra/docker/docker-compose.prod.yml build

# Start production stack
docker-compose -f infra/docker/docker-compose.prod.yml up -d

# Run production migrations
docker-compose -f infra/docker/docker-compose.prod.yml exec app python scripts/migrate_database.py
```

#### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infra/kubernetes/

# Check deployment status
kubectl get pods
kubectl get services

# Port forward for testing
kubectl port-forward service/omega-stack 8000:8000
```

#### Environment Variables

Set production environment variables:

```bash
# Production environment variables
export PRODUCTION=true
export DATABASE_URL="postgresql://user:password@prod-db:5432/omega_prod"
export REDIS_URL="redis://prod-redis:6379"
export SECRET_KEY="your-production-secret-key"
export DEBUG=false
```

### Monitoring and Observability

#### Health Checks

Implement health checks:

```python
from fastapi import APIRouter, HTTPException
from app.XNAi_rag_app.core.health_checker import HealthChecker

router = APIRouter()
health_checker = HealthChecker()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        status = await health_checker.get_health_status()
        if status["status"] == "healthy":
            return status
        else:
            raise HTTPException(status_code=503, detail=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        ready = await health_checker.is_ready()
        if ready:
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Metrics Collection

Implement metrics collection:

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('omega_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('omega_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('omega_active_connections', 'Active connections')

@router.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect metrics."""
    start_time = time.time()
    
    # Increment request count
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    
    # Track active connections
    ACTIVE_CONNECTIONS.inc()
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Record request duration
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        
        # Decrement active connections
        ACTIVE_CONNECTIONS.dec()
```

## Advanced Development

### Plugin Development

Create custom plugins:

```python
from omega_stack.plugins.base import BasePlugin
from typing import Dict, Any, Optional

class CustomAuthProvider(BasePlugin):
    """Custom authentication provider plugin."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.auth_url = config.get("auth_url")
        self.client_id = config.get("client_id")
    
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        # Plugin initialization logic
        return True
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user."""
        # Authentication logic
        return {"user_id": "123", "permissions": ["read", "write"]}
    
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

# Plugin registration
def register_plugin() -> CustomAuthProvider:
    return CustomAuthProvider
```

### Custom Provider Integration

Integrate custom providers:

```python
from app.XNAi_rag_app.core.base_provider import BaseProvider
from typing import Dict, Any, Optional

class CustomProvider(BaseProvider):
    """Custom provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
    
    async def dispatch(self, task: str, context_size: int = 10000,
                      task_type: str = "general", timeout_sec: float = 60.0) -> Dict[str, Any]:
        """Dispatch task to custom provider."""
        try:
            # Custom provider logic
            response = await self._make_api_call(task, context_size)
            
            return {
                "success": True,
                "provider": "custom",
                "output": response,
                "latency_ms": 1000,
                "tokens_used": 1000
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "custom",
                "error": str(e),
                "latency_ms": 1000
            }
    
    async def _make_api_call(self, task: str, context_size: int) -> str:
        """Make API call to custom provider."""
        # Implementation specific to your provider
        pass
```

### Custom Memory Backend

Create custom memory backend:

```python
from app.XNAi_rag_app.core.memory_provider import MemoryProvider
from typing import Dict, Any, List, Optional

class CustomMemoryProvider(MemoryProvider):
    """Custom memory backend implementation."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def connect(self):
        """Connect to custom memory backend."""
        # Connection logic
        pass
    
    async def save_state(self, state: AgentState) -> bool:
        """Save agent state."""
        # Save logic
        return True
    
    async def load_state(self, agent_id: str, session_id: str) -> Optional[AgentState]:
        """Load agent state."""
        # Load logic
        return None
    
    async def save_fact(self, fact: AgentFact) -> bool:
        """Save agent fact."""
        # Save logic
        return True
    
    async def load_facts(self, agent_id: str, category: Optional[str] = None) -> List[AgentFact]:
        """Load agent facts."""
        # Load logic
        return []
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### Redis Connection Issues

```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check connection
redis-cli -u $REDIS_URL ping
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Check system memory
free -h

# Monitor memory in Python
import psutil
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024} MB")
```

#### Performance Issues

```bash
# Check CPU usage
top

# Check disk I/O
iotop

# Profile Python code
python -m cProfile -o profile.stats your_script.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('tottime').print_stats(10)"
```

### Debug Commands

#### Docker Debug Commands

```bash
# View container logs
docker logs <container_id>

# Execute command in container
docker exec -it <container_id> bash

# Check container status
docker ps -a

# View container stats
docker stats <container_id>
```

#### Application Debug Commands

```bash
# Check application health
curl http://localhost:8000/health

# Check application readiness
curl http://localhost:8000/ready

# View application logs
docker-compose logs -f app

# Check database migrations
docker-compose exec app python scripts/check_migrations.py
```

### Getting Help

#### Documentation

- [Architecture Overview](ARCHITECTURE_OVERVIEW.md)
- [API Reference](API_REFERENCE.md)
- [Contributing Guide](CONTRIBUTING.md)

#### Community Support

- GitHub Issues: Report bugs and feature requests
- GitHub Discussions: Ask questions and share ideas
- Documentation: Check for answers first

#### Direct Support

- Create a detailed issue with reproduction steps
- Include environment information
- Provide relevant logs and error messages

This development guide provides comprehensive information for developing with the Omega Stack. For specific questions or issues, refer to the troubleshooting section or seek help from the community.