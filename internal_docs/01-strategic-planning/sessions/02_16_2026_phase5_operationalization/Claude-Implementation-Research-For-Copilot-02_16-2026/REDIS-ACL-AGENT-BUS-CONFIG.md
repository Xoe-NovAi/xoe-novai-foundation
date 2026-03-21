# Redis ACL Configuration for XNAi Agent Bus

**For**: Xoe-NovAi Phase 11 - Security Audit Enhancement  
**Target**: Zero-trust agent communication via Redis Streams  
**Version**: Redis 7.4.1 (configured in docker-compose.yml)

---

## 🎯 Executive Summary

**Objective**: Implement fine-grained access control for agent channels in XNAi Agent Bus, enforcing principle of least privilege.

**Key Principles**:
- **Restrictive by Default**: Agents blocked from all channels except explicitly granted
- **Channel Isolation**: Each agent DID mapped to specific stream patterns
- **Command Restrictions**: Limit to only necessary Redis commands
- **Password Protection**: Individual passwords per agent (hashed SHA256)

---

## 🏗️ XNAi Agent Bus Architecture

### Current Stream Structure
```
XNAi Agent Bus (Redis Streams):
├─ agent:inbox:{DID}        # Individual agent message queue
├─ agent:outbox:{DID}       # Agent response queue
├─ task:queue:*             # Task distribution channels
├─ heartbeat:*              # Agent health monitoring
└─ broadcast:all            # System-wide announcements
```

**Access Control Requirements**:
| Agent Type | Read Access | Write Access | Commands |
|-----------|-------------|--------------|----------|
| Coordinator (Copilot) | All channels | All channels | Full |
| Worker (Cline, Gemini) | Own inbox, task queue | Own outbox, heartbeat | Limited |
| Service (RAG API) | Task queue | Task queue | Stream only |
| Monitor (Prometheus) | Heartbeat, metrics | None | Read-only |

---

## 📋 ACL Implementation Strategy

### Phase 11.1: Default User Hardening

**Current (Vulnerable)**:
```redis
# Default user has full access
ACL LIST
> user default on nopass ~* +@all
```

**Hardened**:
```redis
# Default user disabled for applications
ACL SETUSER default on >new_strong_password ~* +@all
ACL SETUSER default off  # Disable after agent users created
```

### Phase 11.2: Agent-Specific Users

#### Coordinator User (Copilot CLI)
```redis
ACL SETUSER coordinator \
  on \
  >${COORDINATOR_PASSWORD} \
  ~agent:* \
  ~task:* \
  ~heartbeat:* \
  ~broadcast:* \
  &agent:* \
  &task:* \
  &heartbeat:* \
  &broadcast:* \
  +@all \
  -@dangerous

# Explanation:
# on                   = User enabled
# >password            = Set password (hashed automatically)
# ~agent:*             = Access keys matching agent:*
# ~task:*              = Access keys matching task:*
# &agent:*             = Pub/Sub access to agent:* channels
# +@all                = All commands allowed
# -@dangerous          = Except: FLUSHALL, FLUSHDB, KEYS, CONFIG, SHUTDOWN
```

#### Worker User (Cline, Gemini)
```redis
ACL SETUSER worker_cline \
  on \
  >$(CLINE_PASSWORD} \
  ~agent:inbox:did:xnai:cline:* \
  ~agent:outbox:did:xnai:cline:* \
  ~task:queue:* \
  ~heartbeat:did:xnai:cline:* \
  &agent:inbox:did:xnai:cline:* \
  &agent:outbox:did:xnai:cline:* \
  &task:queue:* \
  &heartbeat:did:xnai:cline:* \
  +@read \
  +@write \
  +@stream \
  -@dangerous \
  -@admin

# Explanation:
# Limited to own inbox/outbox (DID-specific)
# Can read task queue (shared)
# Can write to heartbeat (monitoring)
# Cannot access other agents' channels
# Stream commands only (XADD, XREAD, XACK, etc.)
# No admin commands (CONFIG, ACL, etc.)
```

#### Service User (RAG API)
```redis
ACL SETUSER service_rag \
  on \
  >$(RAG_SERVICE_PASSWORD} \
  ~task:queue:rag:* \
  &task:queue:rag:* \
  +@read \
  +@write \
  +@stream \
  -@dangerous \
  -@admin \
  -XDEL

# Explanation:
# Read-only on task queue (no deletion)
# Cannot modify other streams
# Limited to stream operations
```

#### Monitor User (Read-Only)
```redis
ACL SETUSER monitor_prometheus \
  on \
  >$(PROMETHEUS_PASSWORD} \
  ~heartbeat:* \
  ~metrics:* \
  resetchannels \
  &heartbeat:* \
  &metrics:* \
  +@read \
  +INFO \
  +PING \
  -@write \
  -@dangerous \
  -@admin

# Explanation:
# Read-only access
# Heartbeat and metrics streams only
# INFO and PING for health checks
# No write operations
```

---

## 🔧 Implementation for XNAi Stack

### Step 1: ACL Configuration File

Create `/data/redis/users.acl`:
```acl
# XNAi Agent Bus ACL Configuration
# Generated: 2026-02-16
# Redis version: 7.4.1

# Default user - DISABLED after agent users created
user default on >change_this_password ~* &* +@all

# Coordinator - Full access (Copilot CLI)
user coordinator on >{{COORDINATOR_PASSWORD}} ~agent:* ~task:* ~heartbeat:* ~broadcast:* &agent:* &task:* &heartbeat:* &broadcast:* +@all -@dangerous

# Workers - Limited access
user worker_cline on >{{CLINE_PASSWORD}} ~agent:inbox:did:xnai:cline:* ~agent:outbox:did:xnai:cline:* ~task:queue:* ~heartbeat:did:xnai:cline:* &agent:inbox:did:xnai:cline:* &agent:outbox:did:xnai:cline:* &task:queue:* &heartbeat:did:xnai:cline:* +@read +@write +@stream -@dangerous -@admin

user worker_gemini on >{{GEMINI_PASSWORD}} ~agent:inbox:did:xnai:gemini:* ~agent:outbox:did:xnai:gemini:* ~task:queue:* ~heartbeat:did:xnai:gemini:* &agent:inbox:did:xnai:gemini:* &agent:outbox:did:xnai:gemini:* &task:queue:* &heartbeat:did:xnai:gemini:* +@read +@write +@stream -@dangerous -@admin

user worker_grok on >{{GROK_PASSWORD}} ~agent:inbox:did:xnai:grok:* ~agent:outbox:did:xnai:grok:* ~task:queue:* ~heartbeat:did:xnai:grok:* &agent:inbox:did:xnai:grok:* &agent:outbox:did:xnai:grok:* &task:queue:* &heartbeat:did:xnai:grok:* +@read +@write +@stream -@dangerous -@admin

# Services - Stream-only access
user service_rag on >{{RAG_SERVICE_PASSWORD}} ~task:queue:rag:* &task:queue:rag:* +@read +@write +@stream -@dangerous -@admin -XDEL

user service_vikunja on >{{VIKUNJA_PASSWORD}} ~task:queue:vikunja:* &task:queue:vikunja:* +@read +@write +@stream -@dangerous -@admin -XDEL

# Monitoring - Read-only
user monitor_prometheus on >{{PROMETHEUS_PASSWORD}} ~heartbeat:* ~metrics:* resetchannels &heartbeat:* &metrics:* +@read +INFO +PING -@write -@dangerous -@admin
```

### Step 2: Docker Compose Integration

Update `docker-compose.yml`:
```yaml
redis:
  image: redis:7.4.1
  container_name: xnai_redis
  init: true
  user: "${APP_UID:-1001}:${APP_GID:-1001}"
  command: >
    redis-server 
    --requirepass "${REDIS_PASSWORD}"
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
    --aclfile /data/users.acl
    --save ""
    --appendonly no
  volumes:
    - ./data/redis:/data:Z
    - ./configs/redis/users.acl:/data/users.acl:ro
  environment:
    - REDIS_PASSWORD
    - COORDINATOR_PASSWORD
    - CLINE_PASSWORD
    - GEMINI_PASSWORD
    - GROK_PASSWORD
    - RAG_SERVICE_PASSWORD
    - VIKUNJA_PASSWORD
    - PROMETHEUS_PASSWORD
  ports:
    - "6379:6379"
  networks:
    - xnai_network
  restart: unless-stopped
```

### Step 3: Environment Variables

Update `.env`:
```bash
# Redis Master Password (fallback)
REDIS_PASSWORD=your_secure_master_password_here

# Agent ACL Passwords (unique per agent)
COORDINATOR_PASSWORD=copilot_secure_pass_$(openssl rand -hex 16)
CLINE_PASSWORD=cline_secure_pass_$(openssl rand -hex 16)
GEMINI_PASSWORD=gemini_secure_pass_$(openssl rand -hex 16)
GROK_PASSWORD=grok_secure_pass_$(openssl rand -hex 16)

# Service ACL Passwords
RAG_SERVICE_PASSWORD=rag_secure_pass_$(openssl rand -hex 16)
VIKUNJA_PASSWORD=vikunja_secure_pass_$(openssl rand -hex 16)

# Monitoring
PROMETHEUS_PASSWORD=prometheus_secure_pass_$(openssl rand -hex 16)
```

### Step 4: Agent Bus Client Update

Update `/app/XNAi_rag_app/core/agent_bus.py`:
```python
import redis
from typing import Optional
import os

class AgentBusClient:
    """
    Redis Streams client with ACL authentication.
    Each agent uses their own ACL user for zero-trust communication.
    """
    
    def __init__(self, agent_did: str, password: Optional[str] = None):
        self.agent_did = agent_did
        self.username = self._did_to_username(agent_did)
        self.password = password or self._get_password_from_env()
        
        # Redis connection with ACL auth
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            username=self.username,  # ACL username
            password=self.password,  # Agent-specific password
            decode_responses=True
        )
        
        # Validate access on init
        self._validate_access()
    
    def _did_to_username(self, did: str) -> str:
        """
        Convert DID to Redis ACL username.
        Example: did:xnai:cline:001 -> worker_cline
        """
        parts = did.split(':')
        if len(parts) >= 3:
            agent_type = parts[2]  # cline, gemini, grok, etc.
            
            if agent_type == 'copilot':
                return 'coordinator'
            elif agent_type in ['cline', 'gemini', 'grok']:
                return f'worker_{agent_type}'
            elif agent_type in ['rag', 'vikunja']:
                return f'service_{agent_type}'
            elif agent_type == 'prometheus':
                return 'monitor_prometheus'
        
        raise ValueError(f"Unknown agent type in DID: {did}")
    
    def _get_password_from_env(self) -> str:
        """Get agent-specific password from environment"""
        username = self.username.upper().replace('_', '_')
        password_key = f"{username}_PASSWORD"
        
        password = os.getenv(password_key)
        if not password:
            raise ValueError(f"Password not found: {password_key}")
        
        return password
    
    def _validate_access(self):
        """Verify agent has correct permissions"""
        try:
            # Test ping
            self.redis.ping()
            
            # Test inbox access (should succeed for own inbox)
            inbox_key = f"agent:inbox:{self.agent_did}"
            self.redis.xinfo_stream(inbox_key)
            
            # Test unauthorized access (should fail for other agents)
            if self.username.startswith('worker_'):
                try:
                    other_inbox = "agent:inbox:did:xnai:other:001"
                    self.redis.xinfo_stream(other_inbox)
                    raise RuntimeError("Security breach: worker accessed other agent inbox!")
                except redis.exceptions.NoPermissionError:
                    pass  # Expected
            
            print(f"✅ Agent {self.username} authenticated with correct permissions")
            
        except redis.exceptions.AuthenticationError as e:
            raise RuntimeError(f"Authentication failed for {self.username}: {e}")
        except redis.exceptions.NoPermissionError as e:
            raise RuntimeError(f"Permission denied for {self.username}: {e}")
    
    async def send_task(self, target_did: str, task_type: str, payload: dict) -> str:
        """Send task to target agent's inbox (ACL-enforced)"""
        inbox_key = f"agent:inbox:{target_did}"
        
        message = {
            'from': self.agent_did,
            'to': target_did,
            'type': task_type,
            'payload': payload,
            'timestamp': time.time()
        }
        
        try:
            message_id = self.redis.xadd(inbox_key, message)
            return message_id
        except redis.exceptions.NoPermissionError:
            raise RuntimeError(f"Agent {self.username} not authorized to send to {target_did}")
    
    async def read_inbox(self, count: int = 10, block: int = 1000) -> list:
        """Read from own inbox (ACL-enforced)"""
        inbox_key = f"agent:inbox:{self.agent_did}"
        
        try:
            messages = self.redis.xread({inbox_key: '0'}, count=count, block=block)
            return messages
        except redis.exceptions.NoPermissionError:
            raise RuntimeError(f"Agent {self.username} not authorized to read inbox")
```

---

## 🧪 Testing & Validation

### Test 1: Agent Isolation
```python
# tests/test_redis_acl.py

import pytest
import redis

def test_worker_cannot_access_other_inbox():
    """Verify worker agents cannot read other agents' inboxes"""
    # Cline tries to read Gemini's inbox
    cline_client = redis.Redis(
        host='redis',
        port=6379,
        username='worker_cline',
        password=os.getenv('CLINE_PASSWORD')
    )
    
    with pytest.raises(redis.exceptions.NoPermissionError):
        cline_client.xinfo_stream("agent:inbox:did:xnai:gemini:001")

def test_worker_can_access_own_inbox():
    """Verify worker can access own inbox"""
    cline_client = redis.Redis(
        host='redis',
        port=6379,
        username='worker_cline',
        password=os.getenv('CLINE_PASSWORD')
    )
    
    # Should succeed
    cline_client.xinfo_stream("agent:inbox:did:xnai:cline:001")

def test_coordinator_has_full_access():
    """Verify coordinator can access all channels"""
    coordinator = redis.Redis(
        host='redis',
        port=6379,
        username='coordinator',
        password=os.getenv('COORDINATOR_PASSWORD')
    )
    
    # Should access all agent inboxes
    coordinator.xinfo_stream("agent:inbox:did:xnai:cline:001")
    coordinator.xinfo_stream("agent:inbox:did:xnai:gemini:001")
    coordinator.xinfo_stream("task:queue:general")

def test_monitor_is_read_only():
    """Verify monitor cannot write"""
    monitor = redis.Redis(
        host='redis',
        port=6379,
        username='monitor_prometheus',
        password=os.getenv('PROMETHEUS_PASSWORD')
    )
    
    # Read should succeed
    monitor.get("heartbeat:did:xnai:cline:001")
    
    # Write should fail
    with pytest.raises(redis.exceptions.NoPermissionError):
        monitor.set("test_key", "value")
```

### Test 2: Command Restrictions
```bash
# Verify dangerous commands blocked for workers
redis-cli -u redis://worker_cline:${CLINE_PASSWORD}@redis:6379
> FLUSHALL
(error) NOPERM this user has no permissions to run the 'flushall' command

> CONFIG GET *
(error) NOPERM this user has no permissions to run the 'config' command

> XADD agent:inbox:did:xnai:cline:001 * msg "test"
OK  # Stream commands work
```

### Test 3: Pub/Sub Channel Isolation
```bash
# Cline subscribes to own channel (should work)
redis-cli -u redis://worker_cline:${CLINE_PASSWORD}@redis:6379
> SUBSCRIBE agent:inbox:did:xnai:cline:001
OK

# Cline tries other channel (should fail)
> SUBSCRIBE agent:inbox:did:xnai:gemini:001
(error) NOPERM Pub/Sub channel access denied
```

---

## 📊 Security Audit Checklist (Phase 11)

| Check | Status | Validation |
|-------|--------|------------|
| ACL file created | ☐ | File exists at `/data/redis/users.acl` |
| Unique passwords per agent | ☐ | `.env` has 7+ unique passwords |
| Default user disabled | ☐ | `ACL LIST` shows `default off` |
| Workers isolated | ☐ | Test suite passes |
| Dangerous commands blocked | ☐ | FLUSHALL fails for workers |
| Channel patterns enforced | ☐ | Workers can't access other inboxes |
| Monitoring read-only | ☐ | Prometheus can't write |
| Password rotation docs | ☐ | `/docs/runbooks/redis-password-rotation.md` |

---

## 🔄 Password Rotation Procedure

### Step 1: Generate New Password
```bash
NEW_PASSWORD=$(openssl rand -hex 32)
echo "worker_cline:${NEW_PASSWORD}" >> /secure/redis_passwords.txt
```

### Step 2: Update ACL
```redis
ACL SETUSER worker_cline >new_password
# Old password still valid during transition
```

### Step 3: Update Application
```bash
# Update .env
sed -i "s/CLINE_PASSWORD=.*/CLINE_PASSWORD=${NEW_PASSWORD}/" .env

# Restart agent service
docker-compose restart cline_agent
```

### Step 4: Revoke Old Password
```redis
ACL DELUSER worker_cline
ACL SETUSER worker_cline on >new_password <old_password_hash> ~agent:inbox:did:xnai:cline:* ...
# Remove old password after verification
```

---

## 🎯 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| ACL users created | 7 | `ACL LIST | wc -l` |
| Default user disabled | Yes | `ACL GETUSER default | grep off` |
| Test pass rate | 100% | `pytest tests/test_redis_acl.py` |
| Zero cross-agent access | 0 violations | Audit logs |
| Password entropy | >128 bits | `openssl rand -hex 16` |

---

## 📚 References

- Redis ACL provides Pub/Sub channels access management starting from version 6.2
- Redis 7.0 defaults to restrictive pub/sub permissions (resetchannels) for better security
- Redis ACL rules use pattern matching for channels: &pattern for PUBLISH/SUBSCRIBE
- Redis stores passwords hashed with SHA256; ACL LIST shows hex strings, not plaintext
- Command categories like +@read, +@write don't include module commands; use +@all or list individually

---

**Status**: Ready for Phase 11 Implementation  
**Priority**: P1 (security-critical)  
**Validation**: Full test suite required  
**Compliance**: Zero-trust architecture, Ma'at-aligned
