---
last_updated: 2026-02-15
status: COMPLETE
persona_focus: Software Architects, Identity Engineers, Security Researchers
title: "IAM Database Management: Sovereign Agent Identity Persistence"
---

# IAM Database Management: Sovereign Agent Identity Persistence

**Version**: 1.0.0  
**Pattern**: Sovereign Identity Management (Phase 4.2.6)  
**Location**: `app/XNAi_rag_app/core/iam_db.py` (338 lines)

---

## Taxonomy & Purpose

The IAM Database module provides **persistent SQLite storage for agent identities** in the Xoe-NovAi Foundation. It implements the foundational layer of the Sovereign Trinity, storing Decentralized Identifiers (DIDs), Ed25519 public keys, and agent metadata required for zero-trust inter-agent communication.

### Ma'at Alignment
This module embodies three of the 42 Ideals:
- **Ideal #1 (Truth)**: Immutable agent identity records enable cryptographic verification
- **Ideal #15 (Alignment)**: Sovereign agents maintain aligned authorization through persistent verification flags
- **Ideal #31 (Stewardship)**: Local SQLite database ensures data sovereignty without external dependency

---

## Concepts & Architecture

### Agent Types Enum
Defines five supported agent roles in the system:

```python
class AgentType(str, Enum):
    COPILOT = "copilot"      # GitHub Copilot CLI agents
    GEMINI = "gemini"        # Google Gemini API agents
    CLAUDE = "claude"        # Anthropic Claude agents
    CLINE = "cline"          # Cline code editor agents
    SERVICE = "service"      # Internal microservices
```

Each type can have independent credential chains for role-based access control.

### AgentIdentity Dataclass
Represents a single agent's cryptographic identity:

| Field | Type | Purpose |
|-------|------|---------|
| `did` | `str` | Decentralized Identifier (unique primary key) |
| `agent_name` | `str` | Human-readable name (e.g., "copilot-001") |
| `agent_type` | `AgentType` | Role classification for authorization |
| `public_key_ed25519` | `str` | Hex-encoded Ed25519 public key for signature verification |
| `metadata` | `Dict[str, Any]` | Custom attributes (version, region, capabilities) |
| `created_at` | `str` | ISO-8601 timestamp of registration |
| `last_seen` | `Optional[str]` | ISO-8601 timestamp of last activity |
| `verified` | `bool` | True after successful handshake protocol |

#### JSON Serialization
```python
identity.to_dict()  # → database-ready dictionary
AgentIdentity.from_row(db_row)  # → restore from SQLite
```

### IAMDatabase Class
Core persistence layer using WAL (Write-Ahead Logging) SQLite for concurrent access:

#### Performance Tuning (Ryzen 7 5700U)
```python
PRAGMA journal_mode=WAL;           # Concurrent readers
PRAGMA synchronous=NORMAL;          # Balance durability/speed
PRAGMA mmap_size=268435456;         # 256MB memory-mapped I/O
```

These settings optimize for the 6GB Ryzen iGPU constraint while maintaining crash-safety.

---

## Instructions: Using the IAM Database

### 1. **Initialize the Database**

#### Automatic (Recommended)
```python
from app.XNAi_rag_app.core.iam_db import get_iam_database

# Lazy-loads on first call, uses env variable or default path
iam_db = get_iam_database()  # Opens data/iam_agents.db
```

#### Explicit Initialization
```python
from app.XNAi_rag_app.core.iam_db import IAMDatabase

# With custom path
iam_db = IAMDatabase(db_path="/custom/path/agents.db")

# With in-memory (testing)
iam_db = IAMDatabase(db_path=":memory:")
```

#### Context Manager Support
```python
with IAMDatabase() as iam_db:
    # Use iam_db...
    pass  # Auto-closes on exit
```

### 2. **Register an Agent**

```python
from app.XNAi_rag_app.core.iam_db import AgentIdentity, AgentType
from datetime import datetime, timezone

# Create identity with Ed25519 public key (from handshake or manual setup)
agent = AgentIdentity(
    did="did:xnai:copilot-001",
    agent_name="copilot",
    agent_type=AgentType.COPILOT,
    public_key_ed25519="<64-char hex string>",
    metadata={"version": "1.0", "region": "local", "capabilities": ["chat", "code"]},
    created_at=datetime.now(timezone.utc).isoformat()
)

# Register in database
success = iam_db.register_agent(agent)
if success:
    print(f"Agent {agent.did} registered successfully")
else:
    print(f"Failed: DID already exists (unique constraint)")
```

### 3. **Retrieve Agent Identity**

#### By DID
```python
agent = iam_db.get_agent("did:xnai:copilot-001")
if agent:
    print(f"Public key: {agent.public_key_ed25519}")
    print(f"Verified: {agent.verified}")
```

#### By Name and Type
```python
agent = iam_db.get_agent_by_name("copilot", AgentType.COPILOT)
if agent:
    print(f"Found: {agent.did}")
```

#### List All Agents
```python
# All agents
all_agents = iam_db.list_agents()

# Filtered by type
copilots = iam_db.list_agents(AgentType.COPILOT)
for agent in copilots:
    print(f"{agent.agent_name}: {agent.did}")
```

### 4. **Update Verification Status**

After successful handshake (see `iam_handshake.py`):

```python
# Mark agent as verified
success = iam_db.update_agent_verification("did:xnai:copilot-001", verified=True)

# Update last seen timestamp
iam_db.update_agent_last_seen("did:xnai:copilot-001")
```

### 5. **Delete Agent Identity**

Admin operation for credential rotation or offboarding:

```python
# Revoke agent
success = iam_db.delete_agent("did:xnai:copilot-001")
if success:
    print("Agent revoked from IAM database")
```

---

## Reference: Schema Design

### Table: `agent_identities`

```sql
CREATE TABLE agent_identities (
    did TEXT PRIMARY KEY,                    -- Unique identifier
    agent_name TEXT NOT NULL,                -- e.g., "copilot"
    agent_type TEXT NOT NULL,                -- COPILOT|GEMINI|CLAUDE|CLINE|SERVICE
    public_key_ed25519 TEXT NOT NULL,        -- 64-char hex string
    metadata TEXT NOT NULL,                  -- JSON object
    created_at TEXT NOT NULL,                -- ISO-8601
    last_seen TEXT,                          -- ISO-8601 or NULL
    verified INTEGER DEFAULT 0               -- 0 or 1 (bool)
)
```

### Indices for Performance

```sql
CREATE UNIQUE INDEX idx_agent_name_type
ON agent_identities(agent_name, agent_type)
-- Fast lookup by name+type pair

CREATE INDEX idx_agent_type
ON agent_identities(agent_type)
-- Efficient filtering by agent type
```

---

## Troubleshooting Guide

### Issue: "Database is locked"
**Cause**: WAL mode with concurrent writers exceeding connection pool  
**Solution**: Increase `max_connections` or reduce write frequency

```python
# In docker-compose.yml:
# Set SQLITE_TIMEOUT environment variable (milliseconds)
environment:
  SQLITE_TIMEOUT: "5000"  # 5 seconds
```

### Issue: "DID already exists"
**Cause**: Attempting to register duplicate agent  
**Solution**: Use `get_agent()` to check first, or implement upsert pattern

```python
existing = iam_db.get_agent(did)
if existing:
    print(f"Agent {did} already exists")
else:
    iam_db.register_agent(agent)
```

### Issue: "Public key verification failed"
**Cause**: Ed25519 public key not stored in correct hex format  
**Solution**: Validate key with KeyManager (see `iam_handshake.py`)

```python
from app.XNAi_rag_app.core.iam_handshake import KeyManager

# Verify key format
try:
    pub_key = KeyManager.load_public_key(public_key_hex)
    print("✓ Valid Ed25519 public key")
except Exception as e:
    print(f"✗ Invalid key: {e}")
```

---

## Integration Points

### With Sovereign Handshake Protocol
The handshake module uses IAMDatabase to:
1. **Verify agent identities** exist before challenging
2. **Retrieve public keys** for signature verification
3. **Update verification flags** upon successful authentication

```python
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake

handshake = SovereignHandshake(iam_db)  # Pass database instance
```

### With FastAPI Dependency Injection
```python
from fastapi import FastAPI, Depends
from app.XNAi_rag_app.core.dependencies import get_iam_database

app = FastAPI()

@app.get("/agents/{did}")
async def get_agent_endpoint(did: str, iam_db = Depends(get_iam_database)):
    agent = iam_db.get_agent(did)
    return agent.to_dict() if agent else {"error": "not found"}
```

### With Circuit Breaker Health Checks
Agent verification status can gate service access:

```python
# In circuit breaker callback
def check_agent_authorized(agent_did: str) -> bool:
    agent = iam_db.get_agent(agent_did)
    return agent and agent.verified  # Only verified agents pass through
```

---

## Best Practices

### 1. **Key Rotation Strategy**
- Use versioned DIDs: `did:xnai:agent-v1`, `did:xnai:agent-v2`
- Store old keys in metadata for grace periods
- Coordinate rotation with all dependent systems

### 2. **Metadata Conventions**
```python
metadata = {
    "version": "1.0",                    # Agent code version
    "region": "local",                   # Deployment region
    "capabilities": ["chat", "code"],    # Authorized operations
    "rate_limit_requests_per_min": 60,   # Auth-based throttling
    "max_context_tokens": 2048,          # Resource allocation
    "pgp_key_id": "0x1234567890ABCDEF"  # Optional GPG integration
}
```

### 3. **Lifecycle Management**
- **Active**: `created_at` recent, `verified: true`, `last_seen` current
- **Stale**: `last_seen` > 30 days ago → mark inactive
- **Revoked**: `delete_agent()` to remove entirely

### 4. **Security Hardening**
```bash
# Ensure database file permissions (after initialization)
chmod 0600 data/iam_agents.db
chmod 0700 data/

# Consider encryption at rest
sudo cryptsetup luksFormat /dev/sdX  # Full-disk encryption for production
```

---

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| `register_agent()` | O(1) | Write-ahead logging ensures durability |
| `get_agent()` | O(1) | Primary key lookup |
| `get_agent_by_name()` | O(1) | Unique index on (name, type) |
| `list_agents()` | O(n) | Full table scan with optional filter |
| `update_agent_verification()` | O(1) | Single row update |
| `delete_agent()` | O(1) | Single row deletion |

For n=1000 agents on Ryzen 7 5700U:
- **Read-heavy**: <5ms per operation
- **Write-heavy**: <20ms per operation
- **Concurrent access**: WAL allows 5+ parallel readers

---

## Testing

### Unit Test Example
```python
import pytest
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType

@pytest.fixture
def iam_db():
    db = IAMDatabase(db_path=":memory:")
    yield db
    db.close()

def test_register_and_retrieve(iam_db):
    agent = AgentIdentity(
        did="test:agent:001",
        agent_name="test",
        agent_type=AgentType.COPILOT,
        public_key_ed25519="aa" * 32,
        metadata={},
        created_at="2026-02-15T00:00:00Z"
    )
    
    assert iam_db.register_agent(agent) is True
    retrieved = iam_db.get_agent("test:agent:001")
    assert retrieved.agent_name == "test"
    assert retrieved.verified is False
```

---

## Migration & Versioning

### Schema Evolution
If adding new fields in future phases:

```python
# Add migration in _initialize_schema()
cursor.execute("""
    ALTER TABLE agent_identities 
    ADD COLUMN multi_sig_threshold INTEGER DEFAULT 1
""")
```

SQLite supports safe ALTER TABLE for most operations. For breaking changes, create a new table and migrate data.

---

## Related Documentation

- **[Sovereign Handshake Protocol](05-sovereign-handshake-protocol.md)** - Uses this database for agent verification
- **[Redis State Management](06-redis-state-management.md)** - Complements with distributed caching
- **[Circuit Breaker Architecture](circuit-breaker-architecture.md)** - Guards against unauthorized access
- **[Phase 4.2 Completion Report](../../PHASE-4.2-COMPLETION-REPORT.md)** - Implementation milestone

---

**Last Reviewed**: 2026-02-15  
**Next Review**: 2026-03-15 (Agent onboarding metrics analysis)
