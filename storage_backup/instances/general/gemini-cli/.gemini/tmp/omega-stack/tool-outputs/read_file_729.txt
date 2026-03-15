# Memory Bank MCP Server - Fallback Integration Guide

**Location**: `mcp-servers/memory-bank-mcp/`  
**Status**: ✅ Integrated  
**Version**: 1.0.0

## 📦 What's Here

This directory contains the memory-bank MCP server with integrated fallback system:

| File | Purpose |
|------|---------|
| **server.py** | Main MCP server (integrates fallback automatically) |
| **memory_bank_store.py** | SQLite fallback backend |
| **memory_bank_fallback.py** | Circuit breaker & failover orchestrator |
| **pyproject.toml** | Dependencies (includes aiosqlite) |

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -e .

# Or manually:
pip install aiosqlite>=3.13.0
```

### Running the Server

```bash
# Start server (uses MCP stdio protocol)
python server.py

# Or via the package script:
xnai-memory-bank
```

### Expected Output

```
✅ Memory Bank MCP Server Initializing...
✅ Redis connection: ESTABLISHED
✅ SQLite fallback: INITIALIZED at ~/.xnai/memory_bank.db
✅ Circuit breaker: CLOSED (normal operation)
✅ Memory Bank MCP Server FULLY INITIALIZED (Redis + Fallback)
```

## 🔄 How It Works

### Transparent Failover

**Normal Operation** (Redis available):
```
Agent Call → MCP Server → Try Redis → Success → Return Response
```

**Fallback Active** (Redis down):
```
Agent Call → MCP Server → Try Redis → FAIL (3x) → Use SQLite → Return Response
```

**Auto-Recovery** (Testing reconnection):
```
After 60s timeout → Test Redis connection → If success: back to normal
                  → If fail: stay in fallback
```

### Key Tools

All standard memory-bank tools are automatically wrapped with fallback protection:

- `register_agent` - Register agent with capabilities
- `get_context` - Retrieve context (auto-routes through fallback)
- `set_context` - Store context (dual-write to both systems)
- `update_context` - Modify context
- `delete_context` - Remove context
- **`get_fallback_status`** - NEW: Check system health

## 🎯 For Agents: Using the Fallback System

### Check System Health

```python
status = await client.call_tool("get_fallback_status", {})

# Response:
{
    "fallback_mode_active": false,          # Using Redis (false) or SQLite (true)
    "circuit_breaker_state": "closed",      # closed/open/half_open
    "consecutive_failures": 0,
    "last_primary_attempt": "2026-03-07T17:04:22Z",
    "metrics": {
        "total_operations": 1234,
        "successful": 1233,
        "failed": 1,
        "fallback_ops": 0
    }
}
```

### Understanding Status Fields

| Field | Meaning |
|-------|---------|
| `fallback_mode_active: false` | ✅ System healthy, using Redis (fast) |
| `fallback_mode_active: true` | ⚠️ Redis down, using SQLite (slower but safe) |
| `circuit_breaker_state: closed` | ✅ Normal operation |
| `circuit_breaker_state: open` | ⚠️ Fallback active after failures |
| `circuit_breaker_state: half_open` | 🔄 Testing reconnection, auto-recovering |
| `consecutive_failures: 0` | ✅ No errors |
| `consecutive_failures: >= 3` | 🟡 Fallback mode will activate |

### Example Agent Code

```python
from mcp.client import ClientSession

async def my_agent_task():
    async with ClientSession() as session:
        # 1. Register agent (automatic fallover protection)
        await session.call_tool("register_agent", {
            "agent_id": "my-analyzer",
            "capabilities": ["analyze", "synthesize", "generate"],
            "memory_limit_gb": 2.0
        })
        
        # 2. Store context (dual-write: always safe)
        await session.call_tool("set_context", {
            "agent_id": "my-analyzer",
            "context_type": "project",
            "tier": "hot",
            "content": {"analysis": "..."}
        })
        
        # 3. Retrieve context (automatic failover if needed)
        result = await session.call_tool("get_context", {
            "agent_id": "my-analyzer",
            "context_type": "project",
            "tier": "hot"
        })
        
        # 4. Optional: Check system health
        status = await session.call_tool("get_fallback_status", {})
        if status["fallback_mode_active"]:
            print("Note: Running on SQLite fallback (Redis down)")
        else:
            print("Running on primary Redis (optimal performance)")
```

## ⚙️ Configuration

### Environment Variables

```bash
# Database path (default: ~/.xnai/memory_bank.db)
export FALLBACK_DB_PATH=/var/lib/xnai/memory_bank.db

# Logging level (default: INFO)
export LOG_LEVEL=DEBUG

# Circuit breaker timeout (default: 60000 ms)
export FALLBACK_RECOVERY_TIMEOUT_MS=60000

# Failure threshold (default: 3)
export FALLBACK_FAILURE_THRESHOLD=3
```

### Programmatic Configuration

Edit `memory_bank_fallback.py` to adjust circuit breaker behavior:

```python
class FallbackCircuitBreaker:
    # Number of consecutive failures before opening circuit
    FAILURE_THRESHOLD = 3
    
    # Milliseconds to wait before attempting recovery (HALF_OPEN)
    RECOVERY_TIMEOUT = 60000
    
    # Max test calls while HALF_OPEN
    HALF_OPEN_TEST_CALLS = 2
```

## 🧪 Testing

### Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/test_memory_bank_fallback.py -v

# Run specific test
pytest tests/test_memory_bank_fallback.py::TestMemoryBankStore::test_store_context -v

# Run with coverage
pytest tests/test_memory_bank_fallback.py --cov=mcp-servers/memory-bank-mcp -v
```

### Manual Failover Test

```bash
# Terminal 1: Start server
python mcp-servers/memory-bank-mcp/server.py

# Terminal 2: Register agent (Redis working)
python -c "
import asyncio
from mcp.client import ClientSession

async def test():
    async with ClientSession() as session:
        await session.call_tool('register_agent', {
            'agent_id': 'test-agent',
            'capabilities': ['test'],
            'memory_limit_gb': 1.0
        })
        print('✅ Agent registered (Redis active)')

asyncio.run(test())
"

# Terminal 3: Stop Redis
redis-cli shutdown

# Terminal 2: Try to use system (should fallback to SQLite)
python -c "
import asyncio
from mcp.client import ClientSession

async def test():
    async with ClientSession() as session:
        status = await session.call_tool('get_fallback_status', {})
        print('Status:', status)
        if status['fallback_mode_active']:
            print('✅ Fallback active (as expected)')
        else:
            print('❌ Fallback NOT active (unexpected)')

asyncio.run(test())
"

# Terminal 4: Restart Redis
redis-server

# Terminal 2: Wait 60s, then check recovery
python -c "
import asyncio
from mcp.client import ClientSession

async def test():
    async with ClientSession() as session:
        status = await session.call_tool('get_fallback_status', {})
        print('Status:', status)
        if not status['fallback_mode_active']:
            print('✅ Recovered to primary (as expected)')

asyncio.run(test())
"
```

## 📊 Monitoring

### Health Check Endpoint

Check system status regularly:

```bash
# In your monitoring script
curl http://localhost:YOUR_MCP_PORT/health

# Or via tool call
python -c "
import asyncio
from mcp.client import ClientSession

async def monitor():
    async with ClientSession() as session:
        status = await session.call_tool('get_fallback_status', {})
        
        # Alert if fallback active
        if status['fallback_mode_active']:
            print('⚠️ ALERT: Fallback mode active')
            # Send alert to monitoring system
        
        # Alert if high error rate
        total = status['metrics']['total_operations']
        failed = status['metrics']['failed']
        if total > 0 and failed / total > 0.05:
            print('⚠️ ALERT: High error rate')

asyncio.run(monitor())
"
```

### Log Monitoring

```bash
# Watch logs for errors
LOG_LEVEL=DEBUG python server.py | grep -i "error\|fail\|fallback"

# Check for state transitions
tail -f logs/memory_bank.log | grep "Circuit breaker"
```

## 🐛 Troubleshooting

### Server won't start

```
Error: ModuleNotFoundError: No module named 'aiosqlite'
```

**Fix**:
```bash
pip install aiosqlite>=3.13.0
```

### Fallback not initializing

```
Error: PermissionError: Permission denied: '~/.xnai/memory_bank.db'
```

**Fix**:
```bash
mkdir -p ~/.xnai
chmod 700 ~/.xnai
```

### Database error

```
Error: sqlite3.DatabaseError: database disk image is malformed
```

**Fix**:
```bash
# Check integrity
sqlite3 ~/.xnai/memory_bank.db "PRAGMA integrity_check;"

# Repair if possible
sqlite3 ~/.xnai/memory_bank.db "VACUUM;"

# Or restore from backup
cp ~/.xnai/memory_bank.db.backup ~/.xnai/memory_bank.db

# Last resort (data loss)
rm ~/.xnai/memory_bank.db
# Server will recreate empty database
```

### Circuit breaker stuck in HALF_OPEN

```
Problem: System stays in HALF_OPEN for hours
```

**Fix**:
```bash
# Check logs
LOG_LEVEL=DEBUG python server.py

# Restart server (resets state)
systemctl restart xnai-memory-bank

# Verify recovery
python -c "
import asyncio
from mcp.client import ClientSession

async def test():
    async with ClientSession() as session:
        status = await session.call_tool('get_fallback_status', {})
        print('Circuit breaker:', status['circuit_breaker_state'])

asyncio.run(test())
"
```

## 📚 Additional Resources

### Full Documentation

See main documentation:
- **Full Technical Details**: `/docs/MEMORY_BANK_FALLBACK_SYSTEM.md`
- **Memory Bank MCP Server**: `/docs/mcp-servers/memory-bank-mcp/README.md`
- **Agent Registration Protocol**: `/docs/AGENT_ACCOUNT_PROTOCOL.md`

### Test Examples

See test suite:
- **Unit Tests**: `/tests/test_memory_bank_fallback.py`
- **Test Coverage**: All components (Store, CircuitBreaker, Wrapper)

### Related Systems

- **Redis Configuration**: `/docs/01-infrastructure/02-connection-guide.md`
- **Agent Protocol**: `/docs/AGENT_ACCOUNT_PROTOCOL.md`
- **Monitoring**: `/docs/knowledge-management/04-operational-procedures.md`

## 🚀 Deployment Checklist

- [ ] `pip install -e .` succeeded (or `pip install aiosqlite`)
- [ ] Server starts without errors
- [ ] Sees "FULLY INITIALIZED" message
- [ ] Database created at `~/.xnai/memory_bank.db`
- [ ] Tests pass: `pytest tests/test_memory_bank_fallback.py -v`
- [ ] `get_fallback_status` tool responds
- [ ] Can register agents with `register_agent` tool
- [ ] Can store/retrieve contexts
- [ ] Monitoring system configured for alerts
- [ ] Backup strategy in place for database

## ✅ Health Check Procedure

Run this weekly or after any Redis maintenance:

```bash
#!/bin/bash
echo "Memory Bank Health Check"
echo "========================"

# 1. Server running?
if systemctl is-active --quiet xnai-memory-bank; then
    echo "✅ Server running"
else
    echo "❌ Server NOT running - restart with: systemctl start xnai-memory-bank"
fi

# 2. Database exists?
if [ -f ~/.xnai/memory_bank.db ]; then
    echo "✅ Database exists"
    sqlite3 ~/.xnai/memory_bank.db "PRAGMA integrity_check;" | grep ok && echo "✅ Database healthy" || echo "⚠️ Database integrity issue"
else
    echo "❌ Database missing - server will recreate on restart"
fi

# 3. Redis connected?
redis-cli ping > /dev/null && echo "✅ Redis connected" || echo "⚠️ Redis not responding"

# 4. Fallback status
python3 -c "
import asyncio
from mcp.client import ClientSession

async def check():
    try:
        async with ClientSession() as session:
            status = await session.call_tool('get_fallback_status', {})
            mode = 'fallback' if status['fallback_mode_active'] else 'primary'
            state = status['circuit_breaker_state']
            print(f'✅ Mode: {mode} | State: {state}')
    except:
        print('⚠️ Could not check fallback status')

asyncio.run(check())
" 2>/dev/null || echo "⚠️ Could not check fallback status"
```

---

**Questions?** See `/docs/MEMORY_BANK_FALLBACK_SYSTEM.md` for detailed documentation.

**Version**: 1.0.0 | **Status**: ✅ Production-Ready | **Last Updated**: 2026-03-07
