---
last_updated: 2026-02-15
status: COMPLETE
persona_focus: Security Architects, Cryptography Engineers, Multi-Agent System Designers
title: "Sovereign Handshake Protocol: Ed25519 Zero-Trust Agent Communication"
---

# Sovereign Handshake Protocol: Ed25519 Zero-Trust Agent Communication

**Version**: 1.0.0  
**Pattern**: Zero-Trust Agent Communication (Phase 4.2.6)  
**Location**: `app/XNAi_rag_app/core/iam_handshake.py` (443 lines)

---

## Taxonomy & Purpose

The Sovereign Handshake Protocol implements **cryptographic inter-agent authentication** using Ed25519 digital signatures and file-based challenge-response exchange. This module establishes zero-trust communication patterns where no agent is assumed trustworthy without explicit verification.

### Ma'at Alignment
This module embodies four of the 42 Ideals:
- **Ideal #2 (Wisdom)**: Cryptographic signatures provide verifiable knowledge of agent identity
- **Ideal #13 (Communication)**: File-based protocol enables async, cross-process messaging
- **Ideal #26 (Justice)**: Verification flags prevent unauthorized agents from accessing resources
- **Ideal #38 (Sovereignty)**: Ed25519 ensures self-custody of agent credentials

---

## Concepts & Architecture

### Challenge-Response Protocol Flow

```
Agent A (Initiator)          Communication Hub          Agent B (Responder)
     │                              │                            │
     ├─ initiate_handshake() ───→  [challenges/nonce_A.json]  ──┤
     │                              │                            │
     │                              │  respond_to_challenge() ←──┤
     │                           [responses/nonce_B.json]        │
     │                              │                            │
     └─ verify_response() ───────→  [verified/nonce_A.json]  ──→ [verified/nonce_B.json]
     │                              │                            │
     └─ Update IAM DB: verified=true                            └─ Update IAM DB: verified=true
```

**Key Properties**:
- **Asynchronous**: No blocking network calls; file-based exchange allows agents to operate independently
- **Auditable**: All challenges and responses are persistent; enables replay attack detection
- **Self-Contained**: No external CA required; each agent verifies signatures directly
- **Timeout-Protected**: Challenges expire in 5 minutes; prevents stale credential attacks

### Ed25519 Signature Scheme

**Key Size**: 32 bytes private + 32 bytes public (64 total when serialized)  
**Signature Size**: 64 bytes per signature  
**Hash Function**: SHA-512 (implicit in Ed25519)  
**Collision Resistance**: 2^256 bits (post-quantum secure against known attacks)

### Configuration Tuning

```python
class SovereignHandshakeConfig:
    CHALLENGE_EXPIRY = 300      # 5 minutes (Ryzen CPU overhead minimal)
    HANDSHAKE_TIMEOUT = 600     # 10 minutes (full protocol window)
    KEY_ENCODING = "hex"        # Filesystem-friendly hex strings
```

---

## Core Components

### 1. KeyManager: Cryptographic Operations

Wrapper around the cryptography library providing Ed25519 key lifecycle:

#### Generate Keypair
```python
from app.XNAi_rag_app.core.iam_handshake import KeyManager

private_key_hex, public_key_hex = KeyManager.generate_keypair()
# Both are 64-char hex strings (32 bytes each)
```

**Output Format**:
```
private_key_hex: "a3b2c1d0..." (64 chars)
public_key_hex:  "f4e5d6c7..." (64 chars)
```

#### Load Keys from Hex

```python
# For signing operations (private)
private_key = KeyManager.load_private_key("a3b2c1d0...")

# For verification (public)
public_key = KeyManager.load_public_key("f4e5d6c7...")
```

#### Sign Message

```python
message = b"challenge_nonce_value"
signature_hex = KeyManager.sign_message(private_key_hex, message)
# Returns: "signature_hex_string" (128 chars = 64 bytes)
```

#### Verify Signature

```python
is_valid = KeyManager.verify_signature(
    public_key_hex,
    message,
    signature_hex
)
# Returns: True if signature matches, False otherwise
```

### 2. ChallengeData: Challenge Structure

Immutable challenge message that initiator sends:

```python
challenge = ChallengeData.create(
    challenger_did="did:xnai:copilot-001"
    # challenge_nonce auto-generated as 64-char hex (32 random bytes)
)

# Output structure:
{
    "type": "challenge",
    "challenger_did": "did:xnai:copilot-001",
    "challenge_nonce": "a3b2c1d0...",  # 64-char hex
    "timestamp": "2026-02-15T12:00:00Z",
    "expires_at": "2026-02-15T12:05:00Z",  # 5 minutes
    "signature": "signed_by_initiator"  # Added later
}
```

**Serialization for Cryptography**:
```python
challenge_bytes = ChallengeData.to_bytes(challenge)
# JSON-serialized with sorted keys for canonical form
# Prevents signature validation failures due to key ordering
```

### 3. ResponseData: Response Structure

Responder's signed acknowledgment including challenge echo:

```python
response = ResponseData.create(
    responder_did="did:xnai:gemini-001",
    challenge_nonce="a3b2c1d0...",
    challenge_signature="signature_from_challenge"  # Echo back
)

# Output structure:
{
    "type": "response",
    "responder_did": "did:xnai:gemini-001",
    "challenge_nonce": "a3b2c1d0...",
    "challenge_signature": "...",  # Proves responder verified challenge
    "timestamp": "2026-02-15T12:01:00Z",
    "signature": "signed_by_responder"  # Added by responder
}
```

### 4. SovereignHandshake: Protocol Controller

Orchestrates the three-phase handshake:

#### Phase 1: Initiate Challenge

```python
from app.XNAi_rag_app.core.iam_db import IAMDatabase
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake

iam_db = IAMDatabase()
handshake = SovereignHandshake(iam_db)

# Agent A initiates handshake with Agent B
challenge_nonce = handshake.initiate_handshake(
    initiator_did="did:xnai:copilot-001",
    responder_did="did:xnai:gemini-001",
    initiator_private_key_hex="a3b2c1d0..."
)

if challenge_nonce:
    print(f"✓ Challenge created: {challenge_nonce}")
    # File written to: communication_hub/state/challenges/{nonce}_copilot-001.json
else:
    print("✗ Initiation failed (agent not found or I/O error)")
```

**What Happens**:
1. Verifies both agents exist in IAM DB
2. Generates random challenge nonce (32 bytes)
3. Signs challenge with initiator's private key
4. Writes challenge file: `challenges/{nonce}_{initiator_did}.json`
5. Returns nonce for tracking

#### Phase 2: Respond to Challenge

```python
# Agent B (running asynchronously) polls challenges/ or is notified
success = handshake.respond_to_challenge(
    challenge_nonce="a3b2c1d0...",
    initiator_did="did:xnai:copilot-001",
    responder_did="did:xnai:gemini-001",
    responder_private_key_hex="f4e5d6c7..."
)

if success:
    print("✓ Challenge response created")
    # File written to: communication_hub/state/responses/{nonce}_gemini-001.json
else:
    print("✗ Response failed (challenge expired or signature invalid)")
```

**What Happens**:
1. Loads challenge file from disk
2. Verifies challenge hasn't expired (5-min window)
3. Verifies challenge signature using initiator's public key
4. Creates response object including challenge signature echo
5. Signs response with responder's private key
6. Writes response file: `responses/{nonce}_{responder_did}.json`

#### Phase 3: Verify Response

```python
# Agent A verifies responder's response
success = handshake.verify_response(
    challenge_nonce="a3b2c1d0...",
    initiator_did="did:xnai:copilot-001",
    responder_did="did:xnai:gemini-001"
)

if success:
    print("✓ Handshake verified! Both agents marked as verified in IAM DB")
    # Files moved to: communication_hub/state/verified/
    # IAM DB updated: verified=true for both agents
else:
    print("✗ Verification failed (response missing or signature invalid)")
```

**What Happens**:
1. Loads response file from disk
2. Verifies response signature using responder's public key
3. Marks both agents as `verified=true` in IAM DB
4. Updates `last_seen` timestamps
5. Moves challenge and response files to `verified/` directory
6. Handshake complete; agents can now communicate

#### Status Query

```python
status = handshake.get_handshake_status("did:xnai:copilot-001", "did:xnai:gemini-001")

# Output:
{
    "status": "verified",
    "initiator": {
        "did": "did:xnai:copilot-001",
        "verified": true,
        "last_seen": "2026-02-15T12:05:00Z"
    },
    "responder": {
        "did": "did:xnai:gemini-001",
        "verified": true,
        "last_seen": "2026-02-15T12:01:00Z"
    }
}
```

---

## Instructions: Implementing Agent Handshakes

### 1. **Initialize Both Agents**

```python
# Agent A startup
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake, KeyManager

iam_db = IAMDatabase()

# Generate keypair (do this once during agent provisioning)
private_key_a, public_key_a = KeyManager.generate_keypair()

# Register in IAM DB
agent_a = AgentIdentity(
    did="did:xnai:copilot-001",
    agent_name="copilot",
    agent_type=AgentType.COPILOT,
    public_key_ed25519=public_key_a,
    metadata={"region": "local"},
    created_at=datetime.now(timezone.utc).isoformat()
)
iam_db.register_agent(agent_a)

# Similarly for Agent B
private_key_b, public_key_b = KeyManager.generate_keypair()
agent_b = AgentIdentity(
    did="did:xnai:gemini-001",
    agent_name="gemini",
    agent_type=AgentType.GEMINI,
    public_key_ed25519=public_key_b,
    metadata={"region": "local"},
    created_at=datetime.now(timezone.utc).isoformat()
)
iam_db.register_agent(agent_b)
```

**Store Credentials Securely**:
```bash
# Write private keys to secure files (read-only to agent process)
echo "$private_key_a" > secrets/copilot-001.key
chmod 0400 secrets/copilot-001.key

# Environment variable injection (Docker/Kubernetes)
export COPILOT_PRIVATE_KEY="$(cat secrets/copilot-001.key)"
```

### 2. **Initiate Handshake (Agent A)**

```python
handshake = SovereignHandshake(iam_db)

challenge_nonce = handshake.initiate_handshake(
    initiator_did="did:xnai:copilot-001",
    responder_did="did:xnai:gemini-001",
    initiator_private_key_hex=private_key_a
)

if challenge_nonce:
    # Store nonce for later verification
    with open("communication_hub/state/my_challenge.txt", "w") as f:
        f.write(challenge_nonce)
```

### 3. **Respond to Challenge (Agent B)**

```python
# Agent B polls or watches communication_hub/state/challenges/
import os
import time

challenges_dir = "communication_hub/state/challenges"
while True:
    challenges = os.listdir(challenges_dir)
    for challenge_file in challenges:
        if challenge_file.endswith(".json"):
            # Extract nonce and initiator DID from filename
            parts = challenge_file[:-5].split("_")  # Remove .json
            challenge_nonce = parts[0]
            initiator_did = "_".join(parts[1:]).replace("-", ":")
            
            success = handshake.respond_to_challenge(
                challenge_nonce=challenge_nonce,
                initiator_did=initiator_did,
                responder_did="did:xnai:gemini-001",
                responder_private_key_hex=private_key_b
            )
            
            if success:
                print(f"✓ Responded to challenge {challenge_nonce}")
    
    time.sleep(5)  # Poll interval
```

### 4. **Verify Response (Agent A)**

```python
# Agent A polls responses/ directory
import os

nonce = "a3b2c1d0..."  # From initiate_handshake()
response_file = f"communication_hub/state/responses/{nonce}_gemini-001.json"

while not os.path.exists(response_file):
    time.sleep(1)  # Wait for response

success = handshake.verify_response(
    challenge_nonce=nonce,
    initiator_did="did:xnai:copilot-001",
    responder_did="did:xnai:gemini-001"
)

if success:
    print("✓ Handshake successful! Agents can now communicate securely.")
```

---

## Reference: Cryptographic Security Properties

### Ed25519 Advantages
| Property | Value | Benefit |
|----------|-------|---------|
| Key Size | 32 bytes | Small, portable, low memory |
| Signature Size | 64 bytes | Efficient for file-based exchange |
| Hash Function | SHA-512 | Post-quantum secure (NIST approved) |
| Attack Resistance | 2^256 | Equivalent to AES-256 strength |

### Vulnerability Mitigations

| Attack | Mitigation | Implementation |
|--------|------------|-----------------|
| **Replay** | Challenge nonce is random, expires in 5 min | `secrets.token_hex(32)` + timestamp |
| **Forgery** | Signature verification requires private key | Ed25519 cryptographic scheme |
| **MITM** | Each agent verifies counterpart's signature | Bidirectional verification |
| **Impersonation** | DIDs tied to public keys in IAM DB | `AgentIdentity.public_key_ed25519` |

### Key Rotation Protocol

```python
# Step 1: Generate new keypair
new_private, new_public = KeyManager.generate_keypair()

# Step 2: Create new identity with v2 suffix
new_agent = AgentIdentity(
    did="did:xnai:copilot-002",  # New version
    agent_name="copilot",
    agent_type=AgentType.COPILOT,
    public_key_ed25519=new_public,
    metadata={"version": "2.0", "previous_did": "did:xnai:copilot-001"},
    created_at=datetime.now(timezone.utc).isoformat()
)
iam_db.register_agent(new_agent)

# Step 3: Re-handshake with all connected agents using new DID
for peer_did in connected_peers:
    handshake.initiate_handshake(
        initiator_did="did:xnai:copilot-002",
        responder_did=peer_did,
        initiator_private_key_hex=new_private
    )

# Step 4: After grace period (30 days), revoke old identity
iam_db.delete_agent("did:xnai:copilot-001")
```

---

## Troubleshooting Guide

### Issue: "Challenge signature verification failed"
**Causes**:
1. Initiator's public key doesn't match the private key used to sign
2. Challenge file was modified after signing
3. Key encoding mismatch (hex vs. binary)

**Solution**:
```python
# Verify key pair consistency
private_hex, public_hex = KeyManager.generate_keypair()
test_message = b"test"
signature = KeyManager.sign_message(private_hex, test_message)
assert KeyManager.verify_signature(public_hex, test_message, signature)
print("✓ Keypair is valid")
```

### Issue: "Challenge not found" or "Challenge expired"
**Causes**:
1. Responder polling too late (> 5 minutes)
2. Filesystem permissions prevent reading challenge file
3. Race condition in file creation

**Solution**:
```python
# Increase expiry for slower environments
# In SovereignHandshakeConfig:
CHALLENGE_EXPIRY = 600  # 10 minutes for high-latency systems

# Add file existence check before respond
import os
challenge_path = os.path.join(
    SovereignHandshakeConfig.CHALLENGES_DIR,
    f"{nonce}_{initiator_did.replace(':', '-')}.json"
)
if not os.path.exists(challenge_path):
    print(f"Challenge file not found: {challenge_path}")
    # Check filesystem permissions
    parent_dir = SovereignHandshakeConfig.CHALLENGES_DIR
    print(f"Directory permissions: {oct(os.stat(parent_dir).st_mode)}")
```

### Issue: "Response not found" or "Response signature invalid"
**Causes**:
1. Responder process didn't complete successfully
2. Responder's public key in IAM DB doesn't match actual key
3. Response file corruption

**Solution**:
```python
# Log all handshake steps
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check IAM DB has correct public key
responder = iam_db.get_agent("did:xnai:gemini-001")
print(f"IAM DB public key: {responder.public_key_ed25519}")

# Verify file exists and is readable
response_path = "communication_hub/state/responses/..."
if os.path.exists(response_path):
    with open(response_path, "r") as f:
        response_data = json.load(f)
    print(f"Response file intact: {json.dumps(response_data, indent=2)}")
```

---

## Integration Points

### With FastAPI Authentication
```python
from fastapi import FastAPI, HTTPException, Header
from app.XNAi_rag_app.core.iam_handshake import KeyManager

app = FastAPI()

@app.post("/secure-endpoint")
async def secure_endpoint(
    agent_did: str = Header(...),
    signature: str = Header(...),
    message: str = Header(...)
):
    # Verify signature
    iam_db = get_iam_database()
    agent = iam_db.get_agent(agent_did)
    
    if not agent or not agent.verified:
        raise HTTPException(status_code=401, detail="Agent not verified")
    
    if not KeyManager.verify_signature(agent.public_key_ed25519, message.encode(), signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    return {"message": "Authorized"}
```

### With Circuit Breaker Guards
```python
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreaker

async def guarded_service_call(agent_did: str, func):
    agent = iam_db.get_agent(agent_did)
    if not agent.verified:
        raise Exception(f"Agent {agent_did} not verified")
    
    # Proceed with circuit breaker protection
    return await circuit_breaker.call(func)
```

---

## Testing

### Integration Test Example
```python
import pytest
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake, KeyManager
from datetime import datetime, timezone

@pytest.fixture
def setup_agents():
    iam_db = IAMDatabase(db_path=":memory:")
    
    # Setup Agent A
    privA, pubA = KeyManager.generate_keypair()
    agentA = AgentIdentity(
        did="did:test:a", agent_name="a", agent_type=AgentType.COPILOT,
        public_key_ed25519=pubA, metadata={},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    iam_db.register_agent(agentA)
    
    # Setup Agent B
    privB, pubB = KeyManager.generate_keypair()
    agentB = AgentIdentity(
        did="did:test:b", agent_name="b", agent_type=AgentType.GEMINI,
        public_key_ed25519=pubB, metadata={},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    iam_db.register_agent(agentB)
    
    return iam_db, (privA, "did:test:a"), (privB, "did:test:b")

def test_complete_handshake(setup_agents, tmp_path):
    iam_db, (privA, didA), (privB, didB) = setup_agents
    
    # Override communication hub path
    import os
    os.environ["COMMUNICATION_HUB_PATH"] = str(tmp_path)
    
    handshake = SovereignHandshake(iam_db)
    
    # Phase 1: Initiate
    nonce = handshake.initiate_handshake(didA, didB, privA)
    assert nonce is not None
    
    # Phase 2: Respond
    assert handshake.respond_to_challenge(nonce, didA, didB, privB) is True
    
    # Phase 3: Verify
    assert handshake.verify_response(nonce, didA, didB) is True
    
    # Check IAM DB
    agentA = iam_db.get_agent(didA)
    agentB = iam_db.get_agent(didB)
    assert agentA.verified is True
    assert agentB.verified is True
```

---

## Related Documentation

- **[IAM Database Management](04-iam-database-management.md)** - Stores agent identities
- **[Redis State Management](06-redis-state-management.md)** - Distributes handshake state across services
- **[Circuit Breaker Architecture](circuit-breaker-architecture.md)** - Guards services from unverified agents
- **[Phase 4.2 Completion Report](../../PHASE-4.2-COMPLETION-REPORT.md)** - Implementation milestone

---

**Last Reviewed**: 2026-02-15  
**Next Review**: 2026-03-15 (Multi-agent handshake scaling with 5+ agents)
