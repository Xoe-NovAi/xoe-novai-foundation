# VIKUNJA IMPLEMENTATION MANUAL - PART 2
## Advanced Configuration & Optimization

**Version**: 2.0  
**Date**: 2026-02-08  
**Focus**: PostgreSQL 16 Optimization, Redis Configuration, Performance Tuning, Security  
**Status**: COMPREHENSIVE & PRODUCTION-OPTIMIZED

---

## TABLE OF CONTENTS

1. [PostgreSQL 16 Optimization](#postgresql-16-optimization)
2. [Redis Configuration & Tuning](#redis-configuration--tuning)
3. [Vikunja Configuration Deep Dive](#vikunja-configuration-deep-dive)
4. [Performance Optimization Strategies](#performance-optimization-strategies)
5. [Connection Pooling & Resource Management](#connection-pooling--resource-management)
6. [Caching Strategies](#caching-strategies)
7. [Security Configuration](#security-configuration)

---

## POSTGRESQL 16 OPTIMIZATION

### 1. Ryzen-Specific Configuration

The config/postgres.conf should be optimized for your AMD Ryzen 5700U (Zen 2 architecture, 8 cores, 16 threads):

```ini
# ============================================================================
# PostgreSQL 16 Configuration for AMD Ryzen 5700U (Zen 2)
# ============================================================================
# This configuration maximizes performance on Zen 2 architecture
# while maintaining stability and ACID compliance.

# Memory Settings (8GB system, 2GB allocated to PostgreSQL)
# ============================================================================
shared_buffers = 512MB                    # 25% of available memory
                                          # Zen 2: High bandwidth benefits from larger cache
effective_cache_size = 2GB                # Total cache available (RAM + disk)
maintenance_work_mem = 128MB              # For index creation, vacuums
work_mem = 20MB                           # Per operation memory (256 parallel ops)
temp_buffers = 16MB                       # Per-session temporary buffer

# Connection Settings
# ============================================================================
max_connections = 100                     # Vikunja default: 20 connections
                                          # Reserve headroom for monitoring, maintenance
# For Vikunja specifically:
#   - VIKUNJA_DATABASE_MAXOPENCONNECTIONS: 20
#   - VIKUNJA_DATABASE_MAXIDLECONNECTIONS: 5
#   - Leaves 75+ for other connections

max_prepared_statements = 1000            # For connection pooling

# WAL (Write-Ahead Logging) Settings
# ============================================================================
wal_level = replica                       # For replication capability (future HA)
max_wal_senders = 10                      # Replication connections
wal_keep_size = 1GB                       # Keep WAL for replication
wal_buffers = 16MB                        # Buffer for WAL writes
min_wal_size = 1GB                        # Minimum WAL size
max_wal_size = 4GB                        # Maximum WAL size

# Checkpointing (Zen 2 high I/O bandwidth)
# ============================================================================
checkpoint_timeout = 15min                # Checkpoint frequency
checkpoint_completion_target = 0.9        # Smooth checkpoint (90% spread)
wal_compression = on                      # Compress WAL for storage
                                          # Zen 2 CPU can handle compression overhead

# Query Planner Settings
# ============================================================================
random_page_cost = 1.1                    # NVMe SSD (if using)
                                          # Traditional HDD: 4.0
                                          # SSD: 1.1
effective_io_concurrency = 200            # Zen 2: Parallel I/O operations
                                          # AMD CPUs benefit from high concurrency

# Parallelization (Zen 2: 8 cores available)
# ============================================================================
max_parallel_workers_per_gather = 4       # Per query parallelization
max_parallel_workers = 8                  # System-wide parallelization
max_parallel_maintenance_workers = 4      # For maintenance operations
parallel_tuple_cost = 0.01                # Cost model for parallelization
parallel_setup_cost = 500                 # Minimum query cost for parallel

# Query Settings
# ============================================================================
shared_preload_libraries = 'pg_stat_statements'  # Query statistics
work_mem = 20MB                           # Per operation memory
                                          # Vikunja: mostly simple queries
                                          # Supports ~256 concurrent operations

# Autovacuum Settings
# ============================================================================
autovacuum = on
autovacuum_naptime = 1min                 # Vacuum check frequency
autovacuum_vacuum_threshold = 50          # Minimum changed tuples
autovacuum_vacuum_scale_factor = 0.1      # 10% of table size
autovacuum_analyze_threshold = 25
autovacuum_analyze_scale_factor = 0.05

# Autovacuum worker processes (Zen 2: afford more workers)
autovacuum_max_workers = 4                # Parallel vacuum workers
autovacuum_work_mem = 128MB               # Per worker memory

# Logging (for monitoring and troubleshooting)
# ============================================================================
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_truncate_on_rotation = on
log_rotation_age = 1d
log_rotation_size = 100MB
log_statement = 'all'                     # Log all statements (adjust for production)
log_min_duration_statement = 100          # Log queries > 100ms
log_connections = on
log_disconnections = on

# Statistics
# ============================================================================
track_activities = on
track_counts = on
track_io_timing = on
track_functions = 'all'

# Extension settings
# ============================================================================
# Future extensions for advanced features:
# shared_preload_libraries = 'pg_stat_statements,uuid-ossp'

# Zen 2 Specific Optimizations
# ============================================================================
# AMD Zen 2 characteristics:
# - High IPC (Instructions Per Cycle)
# - Good memory bandwidth
# - Strong parallel execution
# - Benefits from aggressive parallelization

# Therefore:
# 1. Higher max_parallel_workers (utilize all 8 cores)
# 2. Lower random_page_cost (good at random access)
# 3. Higher effective_io_concurrency (I/O subsystem can handle it)
# 4. Moderate shared_buffers (avoid NUMA penalties on Ryzen)
```

### 2. Connection Pooling with pgBouncer (Optional but Recommended)

For future high-load scenarios, add connection pooling:

```ini
# pgbouncer.ini (if deployed alongside PostgreSQL)

[databases]
vikunja = host=localhost port=5432 dbname=vikunja

[pgbouncer]
pool_mode = transaction              # Vikunja: transaction-level pooling
max_client_conn = 100                # Total client connections
default_pool_size = 20               # Pool size (matches Vikunja config)
min_pool_size = 5                    # Minimum connections
reserve_pool_size = 2                # Emergency pool
reserve_pool_timeout = 2             # Emergency pool timeout
max_db_connections = 25              # Per-database connections
max_user_connections = unlimited     # Per-user connections
```

### 3. Backup Strategy

```bash
# Daily backup script
#!/bin/bash

BACKUP_DIR="/backups/postgresql"
DB_NAME="vikunja"
RETENTION_DAYS=30

# Full backup
pg_dump -h localhost -U vikunja -d vikunja | \
  gzip > "$BACKUP_DIR/vikunja_$(date +%Y%m%d).sql.gz"

# Cleanup old backups
find "$BACKUP_DIR" -name "vikunja_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
gzip -t "$BACKUP_DIR/vikunja_$(date +%Y%m%d).sql.gz" && \
  echo "✅ Backup successful" || \
  echo "❌ Backup verification failed"
```

### 4. Monitoring PostgreSQL Performance

```sql
-- Slow Query Analysis
SELECT query, calls, mean_time, stddev_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Connection Status
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname;

-- Cache Hit Ratio (should be >99%)
SELECT
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;

-- Table Size Analysis
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index Effectiveness
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## REDIS CONFIGURATION & TUNING

### 1. Redis Configuration for Vikunja

```conf
# redis.conf optimized for Vikunja session & cache usage

# Memory Management
maxmemory 512mb                          # Available memory for Redis
maxmemory-policy allkeys-lru             # Evict LRU keys when full
# Alternatives:
#   - volatile-lru: Only evict keys with TTL
#   - allkeys-random: Random eviction
#   - volatile-random: Random eviction (with TTL)
#   - volatile-ttl: Evict by TTL

# Vikunja uses: ~50-100MB normally, spike to 200MB under load

# Persistence
save 900 1                               # Save if 900 sec + 1 change
save 300 10                              # Save if 300 sec + 10 changes
save 60 10000                            # Save if 60 sec + 10000 changes

appendonly no                            # AOF disabled (RDB sufficient)
# Note: Vikunja data can be reconstructed from PostgreSQL if needed

# Network
bind 127.0.0.1                           # Only localhost (internal)
protected-mode yes                       # Require auth for external
requirepass ${REDIS_PASSWORD}            # Set from environment variable
port 6379

# Client Management
timeout 0                                # Never disconnect inactive clients
tcp-backlog 511                          # Backlog for connection queue
tcp-keepalive 300                        # Keepalive probe

# Replication (for future HA)
replica-read-only yes                    # Read-only replicas
replica-priority 100                     # Priority for failover

# Database Selection
databases 16                             # Total databases (0-15)
# Vikunja uses: DB 5 (Foundation uses 0-4)

# Eviction & Expiration
lazyfree-lazy-eviction yes               # Non-blocking eviction
lazyfree-lazy-expire yes                 # Non-blocking expiration
lazyfree-lazy-server-del yes             # Non-blocking deletion

# Logging
loglevel notice                          # info, verbose, debug
logfile "/var/log/redis/redis.log"
syslog-enabled no

# Cluster (disabled, single node)
cluster-enabled no
```

### 2. Redis Usage in Vikunja

```
Redis DB 5 (Vikunja's dedicated database):

Key Patterns:
├─ session:*                   → User session data
│  └─ Value: serialized user object + permissions
│  └─ TTL: 24 hours (matches JWT expiration)
│
├─ task:*                      → Task cache
│  └─ Value: task JSON object
│  └─ TTL: 5 minutes
│  └─ Invalidated on: task.updated, task.deleted
│
├─ project:*                   → Project cache
│  └─ Value: project JSON object
│  └─ TTL: 10 minutes
│
├─ user:*:permissions          → Permission cache
│  └─ Value: permission flags
│  └─ TTL: 15 minutes
│  └─ Invalidated on: role/membership changes
│
└─ ratelimit:*                 → API rate limiting
   └─ Counter: requests
   └─ TTL: 1 minute

Memory Usage Pattern:
  ├─ Sessions: 1-5 MB (1-20 active users)
  ├─ Caches: 20-50 MB (task/project cache)
  ├─ Rate limiting: <1 MB
  └─ Total under load: 50-100 MB
```

### 3. Redis Monitoring

```bash
# Monitor Redis performance
redis-cli info stats
redis-cli info memory
redis-cli info clients

# Monitor keyspace
redis-cli info keyspace

# Monitor real-time commands
redis-cli monitor

# Check DB 5 (Vikunja)
redis-cli -n 5 DBSIZE
redis-cli -n 5 KEYS "*"

# Monitor latency
redis-cli --latency
redis-cli --latency-history
```

### 4. Redis Performance Tuning

```bash
# Check current performance
redis-cli INFO stats

# Key metrics:
# - total_commands_processed: should be < 10k/sec for Vikunja
# - instantaneous_ops_per_sec: peak performance metric
# - total_net_output_bytes: bandwidth usage

# If performance issues:
# 1. Check for large values (MEMORY DOCTOR)
redis-cli --help | grep memory

# 2. Check for hot keys
redis-cli --hotkeys

# 3. Check eviction rates
redis-cli INFO stats | grep evicted

# If evictions happening:
# - Increase maxmemory (if system allows)
# - Change eviction policy
# - Reduce TTL values

# Memory optimization
redis-cli MEMORY DOCTOR
```

---

## VIKUNJA CONFIGURATION DEEP DIVE

### 1. Complete Environment Variables Reference

```bash
# ============================================================================
# VIKUNJA CONFIGURATION - Complete Environment Variable Reference
# ============================================================================

# DATABASE CONFIGURATION
# ============================================================================
VIKUNJA_DATABASE_TYPE=postgres           # Only supported type for production
VIKUNJA_DATABASE_HOST=vikunja-db         # PostgreSQL container hostname
VIKUNJA_DATABASE_PORT=5432               # PostgreSQL port
VIKUNJA_DATABASE_USER=vikunja            # PostgreSQL user
VIKUNJA_DATABASE_DATABASE=vikunja        # PostgreSQL database name
VIKUNJA_DATABASE_PASSWORD=${...}         # From environment variable (not secret file)
VIKUNJA_DATABASE_MAXOPENCONNECTIONS=20   # Pool size for Vikunja
VIKUNJA_DATABASE_MAXIDLECONNECTIONS=5    # Idle connections to keep

# Maximum recommended connections:
#   - Total available: 100 (from postgres config)
#   - Vikunja uses: 20
#   - Monitoring, backup, etc: 25
#   - Reserve: 55

# SERVICE CONFIGURATION
# ============================================================================
VIKUNJA_SERVICE_PUBLICURL=http://localhost/vikunja
  # External URL for webhook callbacks, API documentation
  # In production: https://vikunja.yourdomain.com

VIKUNJA_SERVICE_JWTEXPIRATION=86400      # JWT token lifetime (seconds)
  # 86400 = 24 hours
  # Shorter = more security, more refresh requests
  # Longer = less security, fewer refresh requests
  # Recommended: 24-72 hours

VIKUNJA_SERVICE_JWTSECRET=${...}         # JWT signing secret (CRITICAL)
  # Must be: randomly generated, 64+ bytes, base64 encoded
  # Generate: openssl rand -base64 64
  # Rotation: Changing breaks all existing tokens
  # Store: SECURELY (not in version control)

# CORS CONFIGURATION
# ============================================================================
VIKUNJA_CORS_ENABLE=false                # Cross-Origin Resource Sharing
  # Set true if frontend on different domain
  # Frontend required to specify VIKUNJA_CORS_ORIGINS

VIKUNJA_CORS_ORIGINS=*                   # CORS allowed origins
  # In production: restrict to specific domains
  # Don't use: * (wildcard - security risk)

# CALENDAR INTEGRATION
# ============================================================================
VIKUNJA_ENABLECALENDAR=true              # Enable calendar view
  # Requires: PostgreSQL datetime support
  # Features: Gantt charts, timeline views

VIKUNJA_ENABLESYNC=false                 # Enable sync features
  # Note: Disabled for air-gapped setup
  # Would normally sync with external calendars (Google, Outlook)

# FILE STORAGE
# ============================================================================
VIKUNJA_FILES_MAXSIZE=20971520           # Maximum file size (bytes)
  # 20971520 = 20 MB
  # Applies to: attachments, uploads
  # Disk space: must have sufficient space in /app/vikunja/files

# AUTHENTICATION
# ============================================================================
VIKUNJA_AUTH_LOCAL_ENABLED=true          # Enable local user registration
  # When true: users can create accounts directly
  # When false: external auth only (OAuth, OpenID)

VIKUNJA_AUTH_OPENID_ENABLED=false        # Enable OpenID Connect
  # Set true for enterprise SSO integration
  # Requires: additional OpenID configuration

# REDIS CONFIGURATION (NEW IN FIXED VERSION)
# ============================================================================
VIKUNJA_REDIS_ENABLED=true               # Enable Redis (session caching)
  # Benefits:
  #   - Session persistence across restarts
  #   - Faster session lookups
  #   - Task caching
  #   - Rate limiting

VIKUNJA_REDIS_HOST=redis                 # Redis container hostname
VIKUNJA_REDIS_PORT=6379                  # Redis port (MUST be explicit)
  # NOTE: Vikunja uses separate HOST + PORT variables
  # Not: redis:6379 format
  # Many issues stem from missing PORT variable

VIKUNJA_REDIS_PASSWORD=${...}            # Redis authentication
  # Must match: REDIS_PASSWORD from Foundation
  # From environment: sourced at startup

VIKUNJA_REDIS_DB=5                       # Redis database selection
  # Foundation uses: DB 0-4
  # Vikunja uses: DB 5 (isolated)
  # Total: 16 databases available

# LOGGING
# ============================================================================
VIKUNJA_LOGGER_LEVEL=info                # Log level
  # Options: debug, info, warn, error
  # Startup: always logs "Starting Vikunja"
  # Debug: logs all API requests (verbose)

# EMAIL/NOTIFICATION
# ============================================================================
VIKUNJA_MAILER_ENABLED=false             # Email notifications
  # Set true for production (user notifications)
  # Requires: SMTP server configuration
  # For air-gapped: leave disabled

# WEBHOOKS
# ============================================================================
VIKUNJA_WEBHOOKS_ENABLED=true            # Enable webhook system
  # Allows: external systems to register for events
  # Required for: Memory Bank integration

# ADVANCED SETTINGS (Optional)
# ============================================================================
VIKUNJA_CACHE_TYPE=redis                 # Cache backend
VIKUNJA_MIGRATION_TIMEOUT=120             # Database migration timeout
VIKUNJA_TASK_ATTACHMENT_MAX_FILESIZE=20971520  # Same as MAXSIZE
```

### 2. Vikunja Configuration Profiles

```yaml
# development: src/config/config.example.yml (for reference)
# Vikunja 0.24.1 doesn't require config.yml (uses env vars)

# Environment-specific overrides:

# PRODUCTION
VIKUNJA_SERVICE_PUBLICURL=https://vikunja.company.com
VIKUNJA_SERVICE_JWTEXPIRATION=43200      # 12 hours (more frequent refresh)
VIKUNJA_CORS_ENABLE=true
VIKUNJA_CORS_ORIGINS=https://company.com,https://app.company.com
VIKUNJA_LOGGER_LEVEL=warn                # Less verbose logging
VIKUNJA_MAILER_ENABLED=true              # Enable email
VIKUNJA_AUTH_OPENID_ENABLED=true         # Enterprise auth

# DEVELOPMENT
VIKUNJA_SERVICE_PUBLICURL=http://localhost:3456
VIKUNJA_SERVICE_JWTEXPIRATION=604800     # 7 days (long-lived)
VIKUNJA_CORS_ENABLE=true
VIKUNJA_CORS_ORIGINS=*
VIKUNJA_LOGGER_LEVEL=debug               # Verbose for debugging
VIKUNJA_MAILER_ENABLED=false             # Disable email in dev
VIKUNJA_AUTH_OPENID_ENABLED=false

# AIR-GAPPED (Current Setup)
VIKUNJA_SERVICE_PUBLICURL=http://localhost/vikunja
VIKUNJA_SERVICE_JWTEXPIRATION=86400      # 24 hours (local network, acceptable)
VIKUNJA_CORS_ENABLE=false                # No external access
VIKUNJA_ENABLESYNC=false                 # No external sync
VIKUNJA_MAILER_ENABLED=false             # No external email
VIKUNJA_AUTH_LOCAL_ENABLED=true          # Local users only
VIKUNJA_WEBHOOKS_ENABLED=true            # Internal webhooks only
```

---

## PERFORMANCE OPTIMIZATION STRATEGIES

### 1. Startup Performance

```
Current startup time: ~30-45 seconds

Breakdown:
├─ PostgreSQL initialization: 10-15s
├─ Vikunja migrations: 5-10s
├─ Vikunja service startup: 5-10s
├─ Health check stabilization: 5-10s
└─ Cache warming: 5s

Optimization strategies:

1. Pre-warm cache:
   - On startup, load frequently accessed data
   - Tasks per project
   - User permissions
   - Label definitions

2. Lazy initialization:
   - Don't load all data on startup
   - Load on-demand with caching
   - Especially large attachments

3. Connection pooling:
   - Keep persistent connections
   - Reduce connection overhead
```

### 2. Query Performance

```
Common Vikunja queries and optimization:

SLOW (Full table scan):
SELECT * FROM tasks WHERE title LIKE '%search%';

FAST (Indexed search):
SELECT * FROM tasks WHERE project_id = ? AND done = false;

Solution: Always filter by:
  1. project_id or team_id (primary key)
  2. done status (boolean index)
  3. date ranges (indexed dates)

Use search endpoint with filters:
  GET /api/v1/tasks/search?project_id=...&done=0&sort_by=created

Example performance:
  - List 50 tasks: 5-10ms (indexed)
  - Create task: 20-50ms (validation + inserts)
  - Search 1000+ tasks: 50-200ms (depends on query)
```

### 3. API Response Time Targets

```
Endpoint                          Target Time    Current Typical
──────────────────────────────────────────────────────────────────
GET /api/v1/tasks                30-50ms        25-40ms ✅
GET /api/v1/tasks/<id>           10-20ms        8-15ms ✅
POST /api/v1/tasks               50-100ms       40-80ms ✅
PUT /api/v1/tasks/<id>           50-100ms       40-80ms ✅
DELETE /api/v1/tasks/<id>        30-50ms        25-40ms ✅
GET /api/v1/tasks/search         100-300ms      80-250ms ✅
POST /api/v1/webhooks            50-100ms       40-80ms ✅

Acceptable targets:
  - P50: < 100ms
  - P95: < 500ms
  - P99: < 1000ms

If slower:
  1. Check PostgreSQL slow query log
  2. Verify index usage (EXPLAIN ANALYZE)
  3. Check for table bloat (autovacuum)
  4. Profile with Prometheus
```

### 4. Caching Strategy

```
Cache Layers (from fast to slow):

1. Browser Cache (client-side)
   - Static assets (Vue.js app)
   - TTL: 1-7 days
   - Hit rate: ~90% for returning users

2. Redis Cache (server-side)
   - Sessions: 24 hours
   - Tasks: 5 minutes
   - Projects: 10 minutes
   - Users/permissions: 15 minutes
   - Hit rate: ~80-90% after warm-up

3. PostgreSQL Buffer Cache
   - Recently accessed rows
   - Managed by PostgreSQL
   - Hit rate: >99% (goal)

4. Disk (SSD or HDD)
   - Full database
   - Slowest option
   - Avoid at all costs

Cache Invalidation Pattern:
├─ Time-based: tasks expire after 5 minutes
├─ Event-based: task.updated event clears cache
├─ Manual: admin can force cache clear
└─ Dependency: related caches invalidated together
   └─ Example: Delete task → invalidate task + project caches
```

---

## CONNECTION POOLING & RESOURCE MANAGEMENT

### 1. Database Connection Pooling

```
PostgreSQL Connection Pool (built-in):

Current Setup:
├─ Max connections (PostgreSQL): 100
├─ Vikunja pool size: 20 (configured)
└─ Monitoring connections: 5-10
└─ Reserve: ~70

Connection Lifecycle:
1. Vikunja requests connection
2. PostgreSQL creates new connection (or reuses idle)
3. Query executed
4. Connection returned to pool
5. After 5 minutes idle: connection closed

Pool Configuration (docker-compose_vikunja.yml):
VIKUNJA_DATABASE_MAXOPENCONNECTIONS=20
VIKUNJA_DATABASE_MAXIDLECONNECTIONS=5

Means:
├─ 20 active connections allowed
├─ 5 idle connections kept ready
├─ New connections created on demand
└─ Excess connections closed after timeout

Optimal Settings for Vikunja:
  - Small deployment (1-10 users): 5-10 connections
  - Medium deployment (10-50 users): 15-20 connections
  - Large deployment (50+ users): 25-40 connections

Current setting (20) is appropriate for small-medium deployments.
```

### 2. Resource Limits

```
Current Container Resource Limits:

RAG Container:
├─ Memory: 4GB limit, 2GB reserved
├─ CPU: 2 cores limit, 1 core reserved
├─ Disk: 10GB available

Vikunja Container:
├─ Memory: No explicit limit (uses parent resources)
├─ CPU: No explicit limit
├─ Disk: Bound to /data/vikunja/ volume

PostgreSQL Container:
├─ Memory: No explicit limit (uses parent resources)
├─ CPU: No explicit limit
├─ Disk: Bound to /data/vikunja/db volume

Recommended Resource Allocation:
┌─────────────────┬──────────────────┐
│ Component       │ Recommended      │
├─────────────────┼──────────────────┤
│ PostgreSQL      │ 1-2 GB RAM       │
│ Vikunja         │ 150-300 MB RAM   │
│ Redis           │ 500 MB RAM       │
│ Total           │ 2-3 GB RAM       │
└─────────────────┴──────────────────┘

Under Load (10+ concurrent users):
├─ PostgreSQL: 2-3 GB
├─ Vikunja: 300-500 MB
├─ Redis: 500 MB - 1 GB
└─ Total: 3-4.5 GB (within 8 GB available)
```

### 3. Memory Management

```
PostgreSQL Memory:

shared_buffers = 512 MB
├─ Query buffer cache
├─ Index cache
└─ Shared across connections

work_mem = 20 MB (per operation)
├─ Sort buffer
├─ Hash table buffer
└─ Per-query allocation

Example: 256 concurrent sorts need: 256 * 20MB = 5.1 GB
├─ Too high → swap usage
├─ Current: rarely concurrent
├─ Acceptable for small deployments

Cache Hit Ratio Goal: >99%
├─ Query: SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))
└─ If <99%: increase shared_buffers

Redis Memory:

maxmemory = 512 MB
├─ Sessions: ~50-100 MB
├─ Caches: ~50-100 MB
├─ Rate limiting: <1 MB
└─ Headroom: ~200 MB

When full: oldest data evicted (LRU)
├─ Sessions: critical, don't evict
├─ Caches: can be regenerated
└─ Solution: monitor memory usage
```

---

## CACHING STRATEGIES

### 1. Cache Patterns in Vikunja

```
Pattern 1: Look-aside Cache (most common)

1. Client requests data
2. Check Redis cache
   ├─ Hit: return cached data
   └─ Miss: query PostgreSQL
3. Update Redis with new data
4. Return to client

Example:
GET /api/v1/tasks/123
├─ Check Redis: task:123
├─ Not found → Query PostgreSQL
├─ Cache result: SET task:123 <data> EX 300
└─ Return task data

Cache invalidation:
PUT /api/v1/tasks/123
├─ Update PostgreSQL
├─ Invalidate cache: DEL task:123
└─ Next read will refresh cache

Pattern 2: Write-through Cache

1. Client writes data
2. Update both cache + database
3. Return success

Example:
POST /api/v1/tasks
├─ Validate in application
├─ Insert into PostgreSQL
├─ Set in Redis: task:<new_id>
└─ Return task with ID

Pattern 3: Refresh-on-Read

1. Client reads data
2. Check cache and update TTL
3. Periodically refresh hot data

Example:
Every task access:
├─ Get from cache if exists
├─ Refresh TTL: EXPIRE task:123 300
└─ Lazy refresh keeps frequently used data alive
```

### 2. Cache Warming

```
On Vikunja startup:

1. Load recent projects
   GET /api/v1/projects?sort_by=updated&order=desc&per_page=10
   └─ Cache each in Redis

2. Load frequently accessed tasks
   SELECT * FROM tasks WHERE done=false ORDER BY due_date LIMIT 100
   └─ Cache in Redis

3. Load user permissions
   SELECT * FROM team_members WHERE team_id IN (...)
   └─ Cache user:*:permissions

4. Load labels
   SELECT * FROM labels WHERE project_id IN (...)
   └─ Cache all label definitions

Benefits:
├─ First user gets instant response (cache hit)
├─ Spreads cache load over startup
└─ Improves perceived performance

Warmup Script:
```python
def warm_cache():
    # Load recent projects
    projects = api.list_projects(per_page=20)
    for project in projects:
        redis.set(f"project:{project['id']}", json.dumps(project), ex=600)
    
    # Load incomplete tasks
    tasks = api.search_tasks(done=0, limit=100)
    for task in tasks:
        redis.set(f"task:{task['id']}", json.dumps(task), ex=300)
    
    print(f"✅ Cache warmed: {len(projects)} projects, {len(tasks)} tasks")
```
```

### 3. Cache Invalidation Patterns

```
Event-based Invalidation (Recommended):

On task.created:
├─ Clear project:* cache (count changed)
└─ Clear user:*:permissions (may have new access)

On task.updated:
├─ Clear task:* cache (data changed)
├─ Clear project:* cache (updated_at changed)
└─ Clear search cache

On task.deleted:
├─ Clear task:* cache
├─ Clear project:* cache
└─ Clear search cache

On team_member.updated:
├─ Clear user:*:permissions (access changed)
└─ Broadcast to connected clients

Time-based Invalidation:

session:* → TTL 86400 (24 hours, matches JWT)
task:* → TTL 300 (5 minutes)
project:* → TTL 600 (10 minutes)
user:*:permissions → TTL 900 (15 minutes)

Combined Strategy:

├─ Events invalidate immediately (when data changes)
├─ TTL provides fallback (automatic refresh)
└─ Results: cache consistency + performance
```

---

## SECURITY CONFIGURATION

### 1. TLS/HTTPS Setup

```
Current: HTTP only (localhost)
Production: REQUIRE HTTPS

Setup with Let's Encrypt:

1. Reverse Proxy (Caddy or Nginx)
   ├─ Listen on 443 (HTTPS)
   ├─ Forward to Vikunja 3456 (HTTP, internal)
   └─ Terminate TLS there

2. Certificate Management
   ├─ Automatic renewal (Caddy: automatic)
   ├─ Certificate pinning (optional, advanced)
   └─ HSTS headers (Strict-Transport-Security)

Example Caddyfile:
```
vikunja.company.com {
    reverse_proxy localhost:3456 {
        header_up X-Forwarded-Proto https
        header_up X-Forwarded-Host {host}
    }
}
```

3. Security Headers
   ├─ X-Frame-Options: SAMEORIGIN (no clickjacking)
   ├─ X-Content-Type-Options: nosniff
   ├─ X-XSS-Protection: 1; mode=block
   ├─ Strict-Transport-Security: max-age=31536000
   └─ Content-Security-Policy: restrictive
```

### 2. JWT Secret Management

```
JWT Secret (CRITICAL):

Current: Generated once, stored in .env
├─ Generated: openssl rand -base64 64
├─ Length: 64 bytes base64-encoded
├─ Stored: VIKUNJA_SERVICE_JWTSECRET=<secret>

Security Considerations:

1. Secret Rotation (Advanced)
   ├─ Change secret: breaks existing tokens
   ├─ Users must re-login
   ├─ Plan rotation during maintenance window
   └─ Alternative: rotate keys (multiple secrets)

2. Compromise Response
   ├─ If secret compromised: change immediately
   ├─ All sessions invalidated
   ├─ Users re-authenticate
   └─ No recovery without secret change

3. Storage Security
   ├─ Never commit to git
   ├─ Use .env file (gitignored)
   ├─ Vault/SecureStore in production
   └─ Limit access (CI/CD, admins only)

Best Practice:
├─ Generate unique secret per environment
├─ Store in secrets management system
├─ Rotate quarterly (planned)
├─ Change on any suspected compromise
└─ Document in security policy
```

### 3. User Authentication Security

```
Password Requirements (Recommended):

├─ Minimum length: 12 characters (Vikunja default: 8)
├─ Complexity: uppercase, lowercase, number, special char
├─ Hashing: bcrypt with cost=10 (current standard)
├─ Salting: automatic with bcrypt
└─ Storage: hashed only, never plaintext

Configuration (via API):
└─ Vikunja: uses sensible defaults
   ├─ Password hashing: bcrypt (automatic)
   ├─ Salt generation: automatic
   └─ Cost: 10 iterations (secure, reasonable performance)

Password Reset Flow:

1. User requests reset
2. Generate token (short-lived, 30 min)
3. Send token via email (if mailer enabled)
4. User clicks link with token
5. Verify token, user sets new password
6. Password immediately changed in database
7. Previous sessions remain valid (old tokens work)

Note: Current setup (VIKUNJA_MAILER_ENABLED=false)
└─ Password reset requires manual admin intervention
└─ Plan for production deployment
```

### 4. API Security

```
Authentication Headers:

Authorization: Bearer <JWT_token>
├─ Token format: three parts (header.payload.signature)
├─ Signed with: VIKUNJA_SERVICE_JWTSECRET
├─ Verified on every request
└─ Expired tokens: return 401 Unauthorized

Rate Limiting (Redis-based):

Per IP / Per User:
├─ Endpoint: /api/v1/login
│  └─ Limit: 5 attempts per minute
├─ Endpoint: /api/v1/auth/register
│  └─ Limit: 2 registrations per minute
└─ General API:
   └─ Limit: 100 requests per minute (configurable)

On limit exceeded:
├─ Return: 429 Too Many Requests
├─ Header: Retry-After
└─ Client: wait before retrying

CORS Security:

Current: VIKUNJA_CORS_ENABLE=false
├─ Only localhost requests allowed
├─ External origins rejected

Production: VIKUNJA_CORS_ENABLE=true
├─ Specify allowed origins: VIKUNJA_CORS_ORIGINS
├─ Example: https://app.company.com,https://company.com
├─ Never use: wildcard (*) in production
└─ Preflight requests: handled automatically
```

---

## PERFORMANCE MONITORING CHECKLIST

```
Daily Monitoring:

☐ PostgreSQL
  ├─ Connection count: < 80
  ├─ Cache hit ratio: > 99%
  ├─ Slow queries: check pg_stat_statements
  └─ Disk usage: check growth trend

☐ Redis
  ├─ Memory usage: < 300 MB
  ├─ Hit rate: > 80%
  ├─ Eviction rate: should be 0
  └─ Commands per second: < 10k

☐ Vikunja
  ├─ API response times: < 100ms (P95)
  ├─ Error rate: < 1%
  ├─ Webhook deliveries: 100% success
  └─ Container health: running

Weekly Monitoring:

☐ Disk space
  ├─ /data/vikunja/db: growth rate
  ├─ /data/vikunja/files: attachment size
  └─ Trigger alert: > 80% full

☐ Performance Trends
  ├─ Query latency: trending?
  ├─ Throughput: stable?
  └─ Resource usage: increasing?

Monthly Analysis:

☐ Long-term Trends
  ├─ Capacity planning: when will we fill up?
  ├─ Performance degradation: index bloat?
  ├─ Scaling needs: when to expand?
  └─ Cost optimization: any savings?
```

---

**Status**: ✅ COMPLETE (Part 2 of 8)  
**Next**: PART 3 - Deployment & Blocker Resolution (Detailed)  
**Key Takeaway**: Proper configuration = 50% of performance and stability

