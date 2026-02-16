# URGENT: Vikunja Redis Configuration Blocker
## New Blocker After Password Fix - Deployment Still Failing

**Date**: February 9, 2026  
**Status**: BLOCKED - Redis Connection Failure  
**Previous Status**: Password authentication FIXED ✅  
**Current Blocker**: Redis "missing port in address" error ❌

---

## EXECUTIVE SUMMARY

**GOOD NEWS**: The environment variable password fix WORKED!  
- Database password authentication now succeeds
- Containers start without "password authentication failed" errors

**BAD NEWS**: New blocker appeared - Vikunja cannot connect to Redis  
- Error: `dial tcp: address redis: missing port in address`
- Container continuously restarts
- Cannot access http://localhost:8000/vikunja

---

## WHAT WAS FIXED ✅

### Blocker #1: Password Authentication - RESOLVED
**Solution Applied**: Environment variables instead of Podman secrets

**Changes Made**:
```yaml
# OLD (BROKEN):
POSTGRES_PASSWORD_FILE: /run/secrets/vikunja-db-pass
secrets:
  - vikunja-db-pass

# NEW (WORKS):
POSTGRES_PASSWORD: ${VIKUNJA_DB_PASSWORD}
# (no secrets section)
```

**Verification**:
- ✅ Database container starts healthy
- ✅ No "password authentication failed" errors
- ✅ Password properly passed via environment variable

---

## CURRENT BLOCKER ❌

### Blocker #2: Redis Connection - ACTIVE

**Error Message**:
```
2026-02-09T06:11:06.617449243Z: INFO    ▶ config/InitConfig 001 No config file found, using default or config from environment variables.
2026-02-09T06:11:06.617449243Z: CRITICAL  ▶ red/InitRedis 002 dial tcp: address redis: missing port in address
```

**Current Configuration**:
```yaml
environment:
  VIKUNJA_REDIS_ENABLED: "true"
  VIKUNJA_REDIS_HOST: redis
  VIKUNJA_REDIS_PORT: "6379"
  VIKUNJA_REDIS_PASSWORD: ${REDIS_PASSWORD}
  VIKUNJA_REDIS_DB: "5"
```

**Redis Container Status**:
```
82f4f67d0fea  docker.io/library/redis:7.4.1  redis-server
Up 47 minutes (healthy)  6379/tcp  xnai_redis
```

**Issue**: Vikunja reports "address redis: missing port in address" even though:
- VIKUNJA_REDIS_HOST is set to "redis"
- VIKUNJA_REDIS_PORT is set to "6379"
- Redis container is running and healthy
- Both containers are on the same network (xnai_network)

---

## HYPOTHESIS: What's Causing the Redis Error

### Hypothesis 1: Vikunja expects host:port format in single variable
Maybe Vikunja doesn't use separate HOST and PORT variables, but expects:
```yaml
VIKUNJA_REDIS_ADDRESS: "redis:6379"  # Combined format?
```

### Hypothesis 2: Wrong environment variable names
Maybe the variable names are different than documented:
```yaml
# Could be:
REDIS_HOST: redis
REDIS_PORT: 6379
# OR:
VIKUNJA_REDIS: redis:6379
# OR:
VIKUNJA_REDIS_SERVER: redis:6379
```

### Hypothesis 3: Port needs to be unquoted or different format
```yaml
# Maybe:
VIKUNJA_REDIS_PORT: 6379        # Without quotes
# Or:
VIKUNJA_REDIS_PORT: '6379'      # Single quotes
# Or:
VIKUNJA_REDIS_PORT: 6379/tcp    # With protocol
```

### Hypothesis 4: Redis needs to be disabled for initial startup
Maybe Vikunja can start without Redis and we enable it later:
```yaml
VIKUNJA_REDIS_ENABLED: "false"
```

### Hypothesis 5: Redis connection string format
```yaml
# Maybe:
VIKUNJA_REDIS: "redis://redis:6379/5"
# With password:
VIKUNJA_REDIS: "redis://:${REDIS_PASSWORD}@redis:6379/5"
```

---

## CURRENT DEPLOYMENT STATE

### Running Containers
| Container | Image | Status | Port |
|-----------|-------|--------|------|
| `xnai_vikunja_db` | postgres:16-alpine | ✅ healthy | 5432 |
| `xnai_redis` | redis:7.4.1 | ✅ healthy | 6379 |
| `xnai_vikunja` | vikunja/vikunja:0.24.1 | ❌ restarting | - |

### Container Logs Pattern
```
INFO    ▶ config/InitConfig 001 No config file found...
CRITICAL ▶ red/InitRedis 002 dial tcp: address redis: missing port in address
(repeats every ~0.5 seconds, container restarts)
```

---

## REQUESTED RESEARCH

### Question 1: Correct Redis Configuration Format
What is the EXACT format Vikunja 0.24.1 expects for Redis connection?

Options:
1. Separate HOST and PORT (current attempt):
   ```yaml
   VIKUNJA_REDIS_HOST: redis
   VIKUNJA_REDIS_PORT: "6379"
   ```

2. Combined ADDRESS:
   ```yaml
   VIKUNJA_REDIS_ADDRESS: "redis:6379"
   ```

3. Full URL:
   ```yaml
   VIKUNJA_REDIS: "redis://redis:6379/5"
   ```

4. Different variable names?

### Question 2: Can Redis be Disabled?
Can Vikunja run without Redis for initial testing?
```yaml
VIKUNJA_REDIS_ENABLED: "false"
```

### Question 3: Complete Working Configuration
Provide a complete, tested docker-compose configuration that includes:
- Database (working ✅)
- Redis connection (needs fix ❌)
- All correct environment variable names and formats

### Question 4: Debugging Steps
How can I verify what environment variables Vikunja is actually receiving?
```bash
podman exec xnai_vikunja env | grep REDIS
```

---

## FILES CURRENTLY IN USE

**docker-compose.yml** (current):
```yaml
version: '3.8'

services:
  vikunja-db:
    image: postgres:16-alpine
    container_name: xnai_vikunja_db
    restart: unless-stopped
    user: "1001:1001"
    environment:
      POSTGRES_USER: vikunja
      POSTGRES_PASSWORD: ${VIKUNJA_DB_PASSWORD}
      POSTGRES_DB: vikunja
    volumes:
      - ./data/vikunja/db:/var/lib/postgresql/data:Z,U
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vikunja -h 127.0.0.1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    networks:
      - xnai_network

  vikunja:
    image: vikunja/vikunja:0.24.1
    container_name: xnai_vikunja
    restart: unless-stopped
    user: "1001:1001"
    depends_on:
      vikunja-db:
        condition: service_healthy
    environment:
      VIKUNJA_DATABASE_TYPE: postgres
      VIKUNJA_DATABASE_HOST: vikunja-db
      VIKUNJA_DATABASE_PORT: 5432
      VIKUNJA_DATABASE_USER: vikunja
      VIKUNJA_DATABASE_PASSWORD: ${VIKUNJA_DB_PASSWORD}
      VIKUNJA_DATABASE_DATABASE: vikunja
      VIKUNJA_SERVICE_PUBLICURL: http://localhost:8000/vikunja
      VIKUNJA_SERVICE_JWTSECRET: ${VIKUNJA_JWT_SECRET}
      # REDIS CONFIGURATION (NEEDS FIX)
      VIKUNJA_REDIS_ENABLED: "true"
      VIKUNJA_REDIS_HOST: redis
      VIKUNJA_REDIS_PORT: "6379"
      VIKUNJA_REDIS_PASSWORD: ${REDIS_PASSWORD}
      VIKUNJA_REDIS_DB: "5"
    volumes:
      - ./data/vikunja/files:/app/vikunja/files:Z,U
    tmpfs:
      - /app/vikunja/.cache:size=50m
      - /tmp:size:100m
    networks:
      - xnai_network

networks:
  xnai_network:
    external: true
```

---

## DEPLOYMENT TIMELINE

| Step | Status | Time |
|------|--------|------|
| Password fix (env vars) | ✅ COMPLETE | 2 hours |
| Database startup | ✅ WORKING | - |
| Redis connection | ❌ BLOCKED | - |
| API endpoint test | ⏳ PENDING | - |
| Frontend access | ⏳ PENDING | - |

---

## NEXT ACTIONS NEEDED

1. **Identify correct Redis configuration format** for Vikunja 0.24.1
2. **Test the fix** by updating docker-compose.yml
3. **Verify deployment** - check if Vikunja container stays running
4. **Test API endpoint** - curl http://localhost:3456/api/v1/info
5. **Test via Caddy proxy** - http://localhost:8000/vikunja

---

## CONTEXT

- **Previous blocker**: Password authentication (FIXED ✅)
- **Current blocker**: Redis connection (ACTIVE ❌)
- **Database**: PostgreSQL 16 running healthy
- **Redis**: Redis 7.4.1 running healthy
- **Vikunja**: vikunja/vikunja:0.24.1 (restarting)
- **Network**: xnai_network (external, shared with Foundation)

---

**END OF RESEARCH REQUEST**

**Request**: Provide the correct Redis configuration format for Vikunja 0.24.1 that resolves the "missing port in address" error.
