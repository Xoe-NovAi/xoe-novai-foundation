---
priority: critical
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Error Handling & Recovery Patterns

**Core Philosophy**: Fail fast, fail safely, recover gracefully. Every error is an opportunity to improve resilience.

## 🛡️ Circuit Breaker Pattern

### **Implementation**
- **External Calls**: Always wrap in circuit breakers
- **Exponential Backoff**: Base delay 1s, max delay 60s, jitter ±25%
- **Failure Threshold**: 3 consecutive failures trigger open state
- **Recovery Time**: 30 seconds before attempting half-open state

### **Code Example**
```python
from pycircuitbreaker import CircuitBreaker

@CircuitBreaker(failure_threshold=3, recovery_timeout=30)
async def external_api_call():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## 🔄 Rollback Strategies

### **Atomic Operations**
- **Database**: Use transactions with savepoints
- **File System**: Write to temp files, then atomic rename
- **Configuration**: Keep backup of previous state

### **Recovery Points**
- **Timestamped Backups**: `backup-20260120-112530.tar.gz`
- **Incremental Changes**: Git commits for each logical unit
- **State Snapshots**: Serialize current state before changes

### **Rollback Commands**
```bash
# Database rollback
python atomic_migrate.py --rollback

# File system rollback
tar -xzf backup-20260120-112530.tar.gz

# Git rollback (last commit only)
git reset --hard HEAD~1
```

## 📊 Logging Standards

### **Structured Logging**
```python
import structlog

logger = structlog.get_logger()

# Error with context
logger.error(
    "external_api_failure",
    url=url,
    status_code=response.status,
    retry_count=attempt,
    error=str(e),
    correlation_id=request_id
)
```

### **Log Levels**
- **DEBUG**: Internal state, performance metrics
- **INFO**: Normal operations, successful recoveries
- **WARNING**: Degraded functionality, manual intervention needed
- **ERROR**: System errors, automatic recovery failed
- **CRITICAL**: System down, immediate attention required

### **Correlation IDs**
- Generate UUID for each user request
- Propagate through all service calls
- Include in error responses and logs

## 🚨 Failure Scenarios & Recovery

### **Network Timeouts**
```python
# Recovery Strategy
try:
    result = await asyncio.wait_for(
        external_call(),
        timeout=30.0
    )
except asyncio.TimeoutError:
    logger.warning("network_timeout", url=url, timeout=30)
    # Fallback to cached data or degraded mode
    return cached_result
```

### **Disk Space Issues**
```python
# Detection & Recovery
def check_disk_space(min_free_gb=1):
    stat = os.statvfs('/')
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    if free_gb < min_free_gb:
        # Cleanup temp files
        cleanup_temp_files()
        # Alert monitoring
        logger.critical("low_disk_space", free_gb=free_gb)
        return False
    return True
```

### **Permission Errors**
```python
# Recovery Strategy
def ensure_permissions(path, expected_mode=0o755):
    try:
        current_mode = os.stat(path).st_mode & 0o777
        if current_mode != expected_mode:
            os.chmod(path, expected_mode)
            logger.info("permissions_fixed", path=path, mode=oct(expected_mode))
    except PermissionError:
        # Escalate to rootless container fix
        run_podman_chown(path)
```

### **Dependency Conflicts**
```python
# Recovery Strategy
def resolve_dependency_conflict():
    # 1. Check current environment
    check_current_versions()

    # 2. Try version overrides
    try_overrides = [
        "mkdocs==1.6.0",
        "mkdocs-material==9.5.0",
        "--override mkdocs-rss-plugin==1.1.0"
    ]

    # 3. Revert to known good state
    if not try_fixes(try_overrides):
        revert_to_backup_lockfile()
```

## 🏗️ Error Recovery Architecture

### **Layered Recovery**
1. **Immediate**: Retry with backoff (network issues)
2. **Component**: Restart failed service (database connection)
3. **System**: Failover to backup system (load balancer)
4. **Data**: Restore from backup (corrupted state)

### **Health Checks**
```python
async def health_check():
    """Comprehensive health verification"""
    checks = {
        "database": check_db_connection(),
        "filesystem": check_disk_space(),
        "network": check_external_connectivity(),
        "memory": check_memory_usage(),
        "dependencies": check_critical_imports()
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        logger.error("health_check_failed", failed_checks=failed)
        return False

    return True
```

## 📈 Monitoring & Alerting

### **Error Metrics**
- **Error Rate**: Errors per minute by type
- **Recovery Time**: Time to restore service
- **False Positives**: Incorrect error detections
- **MTTR**: Mean time to recovery

### **Alert Thresholds**
- **Warning**: Error rate > 1% in 5 minutes
- **Critical**: Error rate > 5% in 1 minute
- **Emergency**: Service unavailable for > 5 minutes

## 🔧 Best Practices

### **Do's**
- ✅ **Fail Fast**: Detect errors early, don't continue with corrupted state
- ✅ **Log Context**: Include all relevant information in error logs
- ✅ **Graceful Degradation**: Maintain partial functionality when possible
- ✅ **Circuit Breakers**: Protect downstream services from cascade failures
- ✅ **Retry Logic**: Implement exponential backoff for transient failures
- ✅ **Atomic Operations**: Ensure changes are all-or-nothing
- ✅ **Monitoring**: Track error rates, recovery times, and success rates

### **Don'ts**
- ❌ **Silent Failures**: Never ignore errors, always log and alert
- ❌ **Infinite Retries**: Always have maximum retry limits
- ❌ **Generic Exceptions**: Catch specific exceptions, not bare `except:`
- ❌ **Resource Leaks**: Always clean up resources in finally blocks
- ❌ **Blocking Operations**: Use async/await for I/O operations
- ❌ **Hardcoded Timeouts**: Make timeouts configurable
- ❌ **Single Points of Failure**: Design redundant systems

## 📚 Reference Patterns

### **Async Error Handling**
```python
async def robust_operation():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientTimeout:
        logger.error("timeout", url=url)
        raise ServiceUnavailable("Service timeout")
    except aiohttp.ClientError as e:
        logger.error("client_error", url=url, error=str(e))
        raise ServiceUnavailable("Service unavailable")
    except Exception as e:
        logger.error("unexpected_error", url=url, error=str(e))
        raise InternalServerError("Internal error")
```

### **Database Transaction Pattern**
```python
async def atomic_update(record_id, new_data):
    async with db.transaction():
        try:
            # Verify current state
            current = await db.fetch_one("SELECT * FROM table WHERE id = $1", record_id)
            if not current:
                raise NotFoundError()

            # Apply changes
            await db.execute(
                "UPDATE table SET data = $1, updated_at = NOW() WHERE id = $2",
                new_data, record_id
            )

            # Verify success
            updated = await db.fetch_one("SELECT * FROM table WHERE id = $1", record_id)
            if not updated:
                raise IntegrityError()

            await db.commit()
            return updated

        except Exception:
            await db.rollback()
            raise
```

### **File Operation Safety**
```python
def safe_file_write(path, content):
    """Atomic file write with backup"""
    backup_path = f"{path}.backup"

    # Create backup
    if os.path.exists(path):
        shutil.copy2(path, backup_path)

    try:
        # Write to temp file first
        temp_path = f"{path}.tmp"
        with open(temp_path, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename
        os.rename(temp_path, path)

        # Remove backup on success
        if os.path.exists(backup_path):
            os.remove(backup_path)

    except Exception as e:
        # Restore backup on failure
        if os.path.exists(backup_path):
            os.rename(backup_path, path)
        raise e
    finally:
        # Cleanup temp files
        for temp_file in [temp_path, backup_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass  # Ignore cleanup errors
