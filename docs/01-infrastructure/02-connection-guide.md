---
title: Phase 1 Connection Guide
description: How to connect to PostgreSQL, Redis, and Qdrant services
last_updated: 2026-02-25
status: active
persona_focus: Developers, Operations, Database Administrators
---

# Phase 1 Connection Guide

Complete guide for connecting to all Phase 1 infrastructure services with connection pooling, configuration examples, and best practices.

---

## Overview

Phase 1 provides three main data services with different connection patterns:

| Service | Type | Port | Protocol | Pooling |
|---------|------|------|----------|---------|
| PostgreSQL | Relational DB | 5432 | TCP/SSL | Connection pooling required |
| Redis | Cache/Sessions | 6379 | TCP | Single persistent connection |
| Qdrant | Vector DB | 6333 (HTTP), 6334 (gRPC) | HTTP/gRPC | Connection pooling optional |

---

## PostgreSQL Connection

### Local Development Connection

```bash
# Direct connection (localhost)
psql -U postgres -h localhost -p 5432 -d xnai

# With password prompt
psql -U postgres -h localhost -p 5432 -d xnai -W

# With password in connection string
PGPASSWORD=your_password psql -U postgres -h localhost -p 5432 -d xnai
```

### Docker Container Connection

```bash
# From host machine to container
docker exec xnai_postgres psql -U postgres -d xnai

# Interactive shell
docker exec -it xnai_postgres psql -U postgres -d xnai
```

### Connection String Formats

**PEP 249 (Python):**
```
postgresql://postgres:password@localhost:5432/xnai
postgresql://postgres:password@localhost:5432/xnai?sslmode=require
```

**libpq (Command Line):**
```
host=localhost user=postgres password=yourpass dbname=xnai port=5432
```

**Node.js (pg):**
```javascript
const connectionString = 'postgresql://postgres:password@localhost:5432/xnai';

// or with options
const connection = {
  host: 'localhost',
  port: 5432,
  database: 'xnai',
  user: 'postgres',
  password: 'password'
};
```

**Python (psycopg2):**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="xnai",
    user="postgres",
    password="password"
)
```

**Python (SQLAlchemy):**
```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:password@localhost:5432/xnai')
```

---

## PostgreSQL Connection Pooling

### PgBouncer Configuration (Recommended)

PgBouncer is a lightweight connection pooler for PostgreSQL.

**Installation:**
```bash
apt-get install pgbouncer
```

**Configuration (/etc/pgbouncer/pgbouncer.ini):**
```ini
[databases]
xnai = host=localhost port=5432 dbname=xnai

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
max_user_connections = 50
server_lifetime = 3600
server_idle_timeout = 600

# Performance
server_connect_timeout = 15
query_timeout = 0
idle_in_transaction_session_timeout = 900

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

**Starting PgBouncer:**
```bash
pgbouncer -d /etc/pgbouncer/pgbouncer.ini

# Verify
psql -h localhost -p 6432 -U postgres -d pgbouncer -c "SHOW POOLS;"
```

### Application-Level Connection Pooling

**Python (SQLAlchemy with psycopg2):**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://postgres:password@localhost:5432/xnai',
    poolclass=QueuePool,
    pool_size=10,           # Connections to keep in pool
    max_overflow=20,        # Additional connections beyond pool_size
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Test connection before use
    echo=False
)
```

**Python (asyncpg with asyncio):**
```python
import asyncpg

# Create connection pool
pool = await asyncpg.create_pool(
    'postgresql://postgres:password@localhost:5432/xnai',
    min_size=10,
    max_size=20,
    command_timeout=60
)

# Use connection from pool
async with pool.acquire() as connection:
    result = await connection.fetch('SELECT * FROM documents')
```

**Node.js (pg with connection pooling):**
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'xnai',
  user: 'postgres',
  password: 'password',
  max: 20,                    // Size of pool
  idleTimeoutMillis: 30000,   // 30 seconds
  connectionTimeoutMillis: 2000
});

// Use connection from pool
const result = await pool.query('SELECT * FROM documents');
```

---

## PostgreSQL Connection Best Practices

### 1. Connection Health Monitoring

```sql
-- Check active connections
SELECT datname, usename, application_name, state, query
FROM pg_stat_activity
WHERE datname = 'xnai';

-- Check connection limits
SHOW max_connections;

-- Current connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = 'xnai';
```

### 2. Connection String Environment Variables

```bash
# .env file
export DATABASE_URL="postgresql://postgres:password@localhost:5432/xnai"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="xnai"
export DB_USER="postgres"
export DB_PASSWORD="password"

# Application usage (Python)
import os
from sqlalchemy import create_engine

engine = create_engine(os.getenv('DATABASE_URL'))
```

### 3. SSL/TLS Connections

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes

# PostgreSQL configuration
echo "ssl = on" >> /etc/postgresql/13/main/postgresql.conf
echo "ssl_cert_file = 'server.crt'" >> /etc/postgresql/13/main/postgresql.conf
echo "ssl_key_file = 'server.key'" >> /etc/postgresql/13/main/postgresql.conf

# Restart PostgreSQL
systemctl restart postgresql

# Connect with SSL
psql "host=localhost dbname=xnai user=postgres sslmode=require"
```

### 4. Timeout Configuration

```python
# Connection timeout
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    connect_timeout=10  # 10 seconds
)

# Query timeout (application level)
conn.set_isolation_level(0)  # Autocommit
cursor = conn.cursor()
cursor.execute("SET statement_timeout TO 5000;")  # 5 seconds per query
```

---

## Redis Connection

### Local Development Connection

```bash
# Direct connection
redis-cli -h localhost -p 6379

# With authentication
redis-cli -h localhost -p 6379 -a your_password

# Check connection
redis-cli ping
# Response: PONG
```

### Docker Container Connection

```bash
# Interactive connection
docker exec -it xnai_redis redis-cli -a $REDIS_PASSWORD ping

# Command execution
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD INFO memory
```

### Connection String Formats

**Python (redis-py):**
```python
import redis

# Direct connection
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password='your_password',
    decode_responses=True
)

# Connection pool
r = redis.Redis(
    connection_pool=redis.ConnectionPool(
        host='localhost',
        port=6379,
        password='your_password',
        db=0,
        max_connections=50
    )
)

# Connection string
r = redis.from_url('redis://:your_password@localhost:6379/0')
```

**Node.js (redis):**
```javascript
const redis = require('redis');

const client = redis.createClient({
  host: 'localhost',
  port: 6379,
  password: 'your_password',
  db: 0
});

// Async/await pattern
client.on('error', (err) => console.error('Redis error', err));
client.on('connect', () => console.log('Connected to Redis'));

await client.set('key', 'value', { EX: 3600 });
const value = await client.get('key');
```

**Python (aioredis for async):**
```python
import aioredis

# Create connection
redis = await aioredis.create_redis_pool(
    'redis://:your_password@localhost:6379',
    minsize=5,
    maxsize=50
)

# Use connection
value = await redis.get('key')
await redis.set('key', 'value', expire=3600)
```

---

## Redis Connection Pooling

### Python Connection Pool (redis-py)

```python
import redis

# Create connection pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    password='your_password',
    db=0,
    max_connections=50,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 3,  # TCP_KEEPINTVL
        3: 5   # TCP_KEEPCNT
    },
    decode_responses=True
)

# Create Redis client with pool
r = redis.Redis(connection_pool=pool)

# Use client
r.set('key', 'value', ex=3600)
```

### Node.js Connection Pool (redis)

```javascript
const redis = require('redis');

const client = redis.createClient({
  host: 'localhost',
  port: 6379,
  password: 'your_password',
  socket: {
    reconnectStrategy: (retries) => {
      if (retries > 10) return new Error('Max retries exceeded');
      return retries * 50;  // Exponential backoff
    }
  }
});

client.on('error', (err) => console.error('Redis error', err));
client.on('connect', () => console.log('Connected'));

await client.connect();
```

---

## Redis Connection Best Practices

### 1. Memory and Key Monitoring

```bash
# Check Redis memory usage
redis-cli info memory

# Monitor key growth
redis-cli --scan --pattern '*' | wc -l

# Check expiration
redis-cli --scan --pattern '*' | xargs redis-cli ttl

# Memory by key type
redis-cli --memkeys
```

### 2. Session Management

```bash
# Check active sessions
redis-cli SCAN 0 MATCH "session:*"

# Get session details
redis-cli GET "session:{session_id}"

# Check session TTL
redis-cli TTL "session:{session_id}"

# Clean expired sessions (if not using Redis expiration)
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'session:*')))" 0
```

### 3. Error Handling

```python
import redis
from redis.exceptions import ConnectionError, TimeoutError

def get_redis_safe():
    try:
        r = redis.Redis(
            host='localhost',
            port=6379,
            password='your_password',
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        r.ping()
        return r
    except (ConnectionError, TimeoutError) as e:
        print(f"Redis connection failed: {e}")
        return None

# Usage with fallback
r = get_redis_safe()
if r:
    r.set('key', 'value')
else:
    # Use in-memory cache fallback
    pass
```

---

## Qdrant Connection

### HTTP REST API Connection

```bash
# Direct connection
curl http://localhost:6333/health

# Check collections
curl http://localhost:6333/collections

# Specific collection info
curl http://localhost:6333/collections/embeddings
```

### Python (qdrant-client)

```python
from qdrant_client import QdrantClient

# Direct connection
client = QdrantClient(
    host="localhost",
    port=6333,
    api_key=None  # No API key in Phase 1
)

# Connection with timeout
client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=30.0
)

# Check health
try:
    collections = client.get_collections()
    print(f"Connected. Collections: {len(collections.collections)}")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Node.js (qdrant-js-client)

```javascript
const { QdrantClient } = require('@qdrant/js-client-rest');

const client = new QdrantClient({
  host: 'localhost',
  port: 6333,
  timeout: 30000
});

// Get collections
const collections = await client.getCollections();
console.log(collections);

// Search vectors
const result = await client.search('embeddings', {
  vector: [0.1, 0.2, ...],  // 384-dim for fastembed
  limit: 10
});
```

### Connection String Formats

**REST API:**
```
http://localhost:6333/collections
http://localhost:6333/collections/embeddings
```

**gRPC (Python):**
```python
from qdrant_client import QdrantClient

# gRPC connection (port 6334)
client = QdrantClient(
    host="localhost",
    port=6334,
    prefer_grpc=True
)
```

---

## Qdrant Connection Pooling & Best Practices

### 1. Connection Configuration

```python
from qdrant_client import QdrantClient
import aiohttp

# Async client with connection pooling
client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=30.0,
    # Internal connection pooling
)

# Check client health
def check_qdrant_health():
    try:
        collections = client.get_collections()
        return True, collections
    except Exception as e:
        return False, str(e)
```

### 2. Batch Operations

```python
from qdrant_client.models import PointStruct, VectorParams, Distance

# Upload vectors efficiently
points = [
    PointStruct(
        id=i,
        vector=embedding,
        payload={"chunk_id": chunk_id, "metadata": {...}}
    )
    for i, (embedding, chunk_id) in enumerate(data)
]

# Batch insert
client.upsert(
    collection_name="embeddings",
    points=points
)
```

### 3. Search Optimization

```python
# Search with multiple parameters
results = client.search(
    collection_name="embeddings",
    query_vector=query_embedding,
    limit=10,
    score_threshold=0.5,
    with_payload=True,
    with_vectors=False  # Don't return vectors (save bandwidth)
)

# Filtered search
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="embeddings",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="metadata.domain",
                match=MatchValue(value="technical")
            )
        ]
    ),
    limit=10
)
```

---

## Connection Troubleshooting

### PostgreSQL Connection Issues

| Issue | Symptoms | Resolution |
|-------|----------|-----------|
| Connection refused | `FATAL: remaining connection slots are reserved` | Check max_connections setting, kill idle connections |
| Connection timeout | Hangs for 30+ seconds | Check firewall, verify host/port, increase timeout |
| Authentication failed | `FATAL: Ident authentication failed` | Check pg_hba.conf, verify credentials |
| Pool exhausted | `Unable to get a connection, pool error` | Increase pool size, reduce connection hold time |
| Disk space | Connections accepted but queries fail | Check disk space, clean old logs/data |

**Diagnostic Commands:**
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Check connection status
docker exec xnai_postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Test connection
docker exec xnai_postgres pg_isready -h localhost -p 5432
```

### Redis Connection Issues

| Issue | Symptoms | Resolution |
|-------|----------|-----------|
| Connection refused | `ConnectionError: Connection refused` | Verify Redis running, check port 6379 |
| Authentication failed | `WRONGPASS invalid username-password pair` | Verify REDIS_PASSWORD, check auth config |
| Memory full | Commands fail, Redis won't accept data | Check maxmemory policy, flush if needed |
| High latency | Slow responses, timeouts | Check Redis memory usage, reduce operations |

**Diagnostic Commands:**
```bash
# Check Redis status
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD ping

# Check memory
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD info memory

# Check operations
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD info stats
```

### Qdrant Connection Issues

| Issue | Symptoms | Resolution |
|-------|----------|-----------|
| Connection refused | `Connection error: connection refused` | Verify Qdrant running, check port 6333 |
| Timeout | Operations hang | Increase timeout, check Qdrant memory |
| Collection not found | `404: collection not found` | Create collection first, check collection name |
| Memory pressure | Searches slow, timeouts | Check storage usage, reduce collection size |

**Diagnostic Commands:**
```bash
# Check Qdrant health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Check disk space
docker exec xnai_qdrant du -sh /qdrant/storage
```

---

## Environment Variables

### Required Variables

```bash
# PostgreSQL
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/xnai
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_secure_password
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Qdrant (no authentication in Phase 1)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

### Optional Variables

```bash
# Connection pooling
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# Timeouts
DB_CONNECT_TIMEOUT=10
DB_QUERY_TIMEOUT=30
REDIS_TIMEOUT=5

# Performance tuning
REDIS_MAX_CONNECTIONS=50
QDRANT_SEARCH_LIMIT=10
```

---

## Verification Checklist

Use this checklist to verify all connections are working:

```bash
# 1. PostgreSQL
echo "Testing PostgreSQL..."
docker exec xnai_postgres pg_isready -h localhost -p 5432
psql -h localhost -U postgres -d xnai -c "SELECT version();"

# 2. Redis
echo "Testing Redis..."
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD ping
docker exec xnai_redis redis-cli -a $REDIS_PASSWORD info server

# 3. Qdrant
echo "Testing Qdrant..."
curl -s http://localhost:6333/health | jq .
curl -s http://localhost:6333/collections | jq .

# 4. All services
echo "Testing all services..."
docker-compose ps
```

---

**Document Version:** 1.0
**Last Updated:** 2026-02-25
**Status:** Active
**Audience:** Developers, Operations, Database Administrators
