# Expert Knowledge: IAM v2.0 Schema Design
## Phase 5 Discovery - Identity Federation

### 1. The DID Mapping Schema
We extend the `agent_identities` table to support the **Human-to-Agent** relationship, moving toward a verifiable sovereign hierarchy.

#### Proposed Schema Updates
```sql
ALTER TABLE agent_identities ADD COLUMN controller_did TEXT;
ALTER TABLE agent_identities ADD COLUMN relationship_type TEXT; -- 'owner', 'delegate', 'service'
ALTER TABLE agent_identities ADD COLUMN auth_key_id TEXT;       -- Links to a specific Ed25519 key for admin ops
```

### 2. Account Naming Protocol (ANP)
To prevent collisions in a multi-agent environment:
- **Human DID**: `did:xnai:human:{username}`
- **Agent DID**: `did:xnai:agent:{agent_type}:{random_hex}`
- **Service DID**: `did:xnai:service:{service_name}:{host_id}`

### 3. Verification Flow
1.  **Identity Assertion**: Agent A claims to be controlled by Human H.
2.  **Challenge**: Agent B (the IAM Validator) issues a challenge to Agent A's `auth_key_id`.
3.  **Signature**: Agent A must provide a signature from the key associated with Human H in the `controller_did` field.
4.  **Verification**: If the signature matches, the relationship is marked `verified=1` in the database.
