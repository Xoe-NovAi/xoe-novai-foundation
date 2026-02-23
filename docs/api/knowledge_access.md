# Knowledge Access Control API

> **Module**: `XNAi_rag_app.core.knowledge_access`
> **Version**: 1.0.0
> **Last Updated**: 2026-02-22

---

## Overview

Zero-trust access control for knowledge operations. Integrates IAM service with knowledge client to provide agent DID validation, task type authorization, and ABAC policy enforcement.

---

## Classes

### KnowledgeAccessControl

Main class for managing knowledge access permissions.

```python
from XNAi_rag_app.core.knowledge_access import KnowledgeAccessControl

# Initialize
access_control = KnowledgeAccessControl(
    iam_service=iam_service,  # Optional: defaults to new IAMService()
    iam_db=iam_db            # Optional: defaults to new IAMDatabase()
)
```

#### Methods

##### `check_access()`

Check if agent has permission for the requested action.

```python
result = await access_control.check_access(
    agent_did="did:xoe:agent:cline-1",
    action=KnowledgeAction.SEARCH,
    resource="knowledge_base",
    context={"priority": "high"}  # Optional
)

if result.is_allowed():
    # Proceed with knowledge operation
    pass
else:
    # Access denied
    logger.warning(f"Access denied: {result.reason}")
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `agent_did` | str | Yes | Decentralized identifier of the requesting agent |
| `action` | KnowledgeAction | Yes | The knowledge action being requested |
| `resource` | str | Yes | The resource being accessed |
| `context` | Dict[str, Any] | No | Additional context for ABAC evaluation |

**Returns:** `AccessResult`

---

##### `check_qdrant_write()`

Check if agent can write to Qdrant collection.

```python
result = await access_control.check_qdrant_write(
    agent_did="did:xoe:agent:cline-1",
    collection="xnai_knowledge"
)
```

---

##### `check_qdrant_read()`

Check if agent can read from Qdrant collection.

```python
result = await access_control.check_qdrant_read(
    agent_did="did:xoe:agent:cline-1",
    collection="xnai_knowledge"
)
```

---

##### `check_qdrant_delete()`

Check if agent can delete from Qdrant collection.

```python
result = await access_control.check_qdrant_delete(
    agent_did="did:xoe:agent:cline-1",
    collection="xnai_knowledge"
)
```

---

##### `register_knowledge_agent()`

Register a new agent with knowledge access permissions.

```python
identity = await access_control.register_knowledge_agent(
    agent_name="cline-production",
    agent_type=AgentType.SERVICE,
    permissions=[Permission.RAG_QUERY, Permission.RAG_INGEST],
    metadata={"environment": "production"}
)
```

---

## Enums

### KnowledgeAction

```python
from XNAi_rag_app.core.knowledge_access import KnowledgeAction

class KnowledgeAction(str, Enum):
    READ = "knowledge:read"        # Read knowledge documents
    WRITE = "knowledge:write"      # Write knowledge documents
    DELETE = "knowledge:delete"    # Delete knowledge documents
    SEARCH = "knowledge:search"    # Search knowledge base
    INDEX = "knowledge:index"      # Index new content
    ADMIN = "knowledge:admin"      # Administrative operations
```

### AccessDecision

```python
from XNAi_rag_app.core.knowledge_access import AccessDecision

class AccessDecision(str, Enum):
    ALLOWED = "allowed"              # Access granted
    DENIED = "denied"                # Access denied by policy
    NOT_AUTHORIZED = "not_authorized"  # Lacks required permission
    INVALID_IDENTITY = "invalid_identity"  # Agent not verified
    RATE_LIMITED = "rate_limited"    # Rate limit exceeded
```

---

## Data Classes

### AccessRequest

```python
@dataclass
class AccessRequest:
    agent_did: str
    action: KnowledgeAction
    resource: str
    context: Dict[str, Any]
    timestamp: str
```

### AccessResult

```python
@dataclass
class AccessResult:
    decision: AccessDecision
    request: AccessRequest
    reason: str
    user: Optional[User]
    agent: Optional[AgentIdentity]
    timestamp: str
    audit_id: str
    
    def is_allowed(self) -> bool:
        """Check if access was granted."""
        return self.decision == AccessDecision.ALLOWED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        ...
```

---

## Permission Mapping

| Action | Required Permission |
|--------|---------------------|
| READ | `RAG_QUERY` |
| SEARCH | `RAG_QUERY` |
| WRITE | `RAG_INGEST` |
| INDEX | `RAG_INGEST` |
| DELETE | `RAG_ADMIN` |
| ADMIN | `RAG_ADMIN` |

---

## ABAC Policies

The following Attribute-Based Access Control policies are enforced:

### 1. Verified Agents Only
Only agents that have completed Ed25519 handshake verification can access knowledge.

### 2. Service Account Write Restriction
Service accounts cannot delete without admin permission.

### 3. Knowledge Admin Full Access
Agents with `RAG_ADMIN` permission have full access to all operations.

---

## Integration Example

```python
import anyio
from XNAi_rag_app.core.knowledge_access import (
    KnowledgeAccessControl,
    KnowledgeAction,
)

async def query_with_access_control(agent_did: str, query: str):
    """Query knowledge base with access control."""
    access_control = KnowledgeAccessControl()
    
    # Check access
    result = await access_control.check_access(
        agent_did=agent_did,
        action=KnowledgeAction.SEARCH,
        resource="knowledge_base"
    )
    
    if not result.is_allowed():
        raise PermissionError(f"Access denied: {result.reason}")
    
    # Proceed with query
    # ... knowledge query logic ...
    return results

# Run
anyio.run(query_with_access_control, "did:xoe:agent:cline-1", "test query")
```

---

## Error Handling

```python
try:
    result = await access_control.check_access(agent_did, action, resource)
except Exception as e:
    logger.error(f"Access check failed: {e}")
    # Default deny on error
    return False
```

---

## Related Modules

- [`iam_service`](./iam_service.md) - IAM service integration
- [`core/sanitization`](./sanitization.md) - Content sanitization
- [`core/redis_streams`](./redis_streams.md) - Redis stream management

---

**Source**: `app/XNAi_rag_app/core/knowledge_access.py`
