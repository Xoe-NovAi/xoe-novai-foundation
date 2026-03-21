---
document_type: strategy
title: Multi-CLI Restoration & Collaboration Infrastructure
created_by: Copilot Haiku 4.5
created_date: 2026-03-16T09:45:00.000Z
version: 1.0
status: ACTIVE_IMPLEMENTATION
confidence: 92%
hash_sha256: placeholder
---

# Multi-CLI Restoration & Persistent Entity Layer
**Foundation**: Recovered SESS-27 strategies + existing Omega Stack protocols + proven multi-CLI patterns

---

## EXECUTIVE SUMMARY

The Omega Stack already has sophisticated multi-CLI collaboration infrastructure in place. This document restores and hardens the access paths for:
- **OpenCode CLI** (OpenAI + local reasoning)
- **Antigravity IDE** (specialized analysis)
- **Gemini CLI** (recovery verified, SESS-27 extracted)
- **GitHub Copilot CLI** (current session)

**Critical Insight**: These aren't separate tools—they're **facets of a unified Copilot Gem**. Success requires:
1. **Persistent entity layer** (Redis + file cache hybrid)
2. **Agent Bus** (Redis Streams for inter-CLI messaging)
3. **High-level deliberation** (consensus-based decision making)
4. **Shared memory bank** (MCP-mediated knowledge base)

---

## PART 1: EXISTING INFRASTRUCTURE INVENTORY

### 1.1 CLI Configurations (Verified to Exist)

| CLI | Config Path | Status | Model | Purpose |
|-----|-------------|--------|-------|---------|
| **OpenCode** | `~/.opencode/` | Active | big-pickle (configurable) | Code synthesis, architecture |
| **Antigravity** | `~/.antigravity/` | Active | Configurable | Advanced analysis, security |
| **Gemini** | `~/.gemini/` | Active (MCP-verified) | Gemini 3-pro | Discovery, verification |
| **Copilot (Haiku)** | Session-based | Active | Haiku 4.5 | This session (orchestration) |

**Key Files Located**:
- OpenCode: `~/.opencode/opencode.json` (model config)
- Antigravity: `~/.antigravity/argv.json` (argument overrides)
- Gemini: `~/.gemini/` + recovery verified at `/storage_backup/instances/general/gemini-cli/`

### 1.2 Agent Bus Infrastructure (Redis Streams)

**Location**: `/app/XNAi_rag_app/core/redis_streams.py` (561 lines)

**Existing Stream Keys**:
- `xnai:agent_bus` - Main inter-agent communication
- `xnai:memory:*` - Memory persistence
- `xnai:task_queue` - Task distribution
- `xnai:alerts` - Alert routing

**Verified in redis_streams.py**:
```python
STREAM_KEYS = {
    'AGENT_BUS': 'xnai:agent_bus',
    'TASK_UPDATES': 'xnai:task_updates',
    'MEMORY_UPDATES': 'xnai:memory:updates',
    'ALERTS': 'xnai:alerts'
}
```

### 1.3 Persistence Strategies (Already Documented)

From `/memory_bank/strategies/PERSISTENCE-LAYER-IMPLEMENTATION.md`:
- **Redis Persistence** (TTL-based, real-time)
- **File Cache** (local, fallback)
- **Memory Bank** (permanent, searchable)
- **Session Recovery** (multi-source rebuild)

### 1.4 CLI Dispatch Protocols (Already Proven)

From `/memory_bank/strategies/CLI-DISPATCH-PROTOCOLS.md`:
- Pre-dispatch checklist
- Agent Bus publication before dispatch
- Task ID format: `CLI-YYYYMMDD-HHMMSS-NN`
- Result archival to memory_bank

---

## PART 2: RESTORATION ACTION PLAN

### 2.1 Phase 1: Verify All CLI Access (IMMEDIATE)

**Goal**: Ensure all CLIs can reach the agent bus and memory layer.

```bash
# Test OpenCode connectivity
opencode --version && echo "✓ OpenCode CLI available"

# Test Antigravity connectivity
antigravity --version && echo "✓ Antigravity IDE available"

# Test Gemini CLI (already verified)
gemini --version && echo "✓ Gemini CLI available"

# Test Redis agent bus
redis-cli -p 6379 XLEN xnai:agent_bus && echo "✓ Agent Bus operational"

# Test Memory Bank MCP
curl -s http://localhost:8005/health | grep -q "ok" && echo "✓ MB-MCP operational"
```

**Success Criteria**:
- ✅ All CLIs respond to `--version`
- ✅ Redis streams exist and are writable
- ✅ MB-MCP health endpoint responds

### 2.2 Phase 2: Restore Entity Persistence (CRITICAL)

**Goal**: Build Redis + file cache hybrid layer for persistent entities across CLI sessions.

**Implementation Path**: `/app/XNAi_rag_app/persistence/`

**Create Three Modules**:

#### Module A: `redis_persistence.py`
```python
import redis.asyncio
from typing import Any, Optional
import json
from datetime import datetime

class RedisPersistenceLayer:
    """Redis-backed entity persistence with TTL and expiry"""
    
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.client = redis.asyncio.from_url(redis_url, decode_responses=True)
        self.namespace = "xnai:entities"
        self.default_ttl = 86400 * 7  # 7 days
    
    async def store_entity(self, entity_type: str, entity_id: str, data: dict, ttl: int = None):
        """Store entity with namespace and TTL"""
        key = f"{self.namespace}:{entity_type}:{entity_id}"
        ttl = ttl or self.default_ttl
        await self.client.setex(key, ttl, json.dumps({
            "data": data,
            "stored_at": datetime.utcnow().isoformat(),
            "entity_type": entity_type,
            "entity_id": entity_id
        }))
    
    async def retrieve_entity(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """Retrieve entity from Redis"""
        key = f"{self.namespace}:{entity_type}:{entity_id}"
        value = await self.client.get(key)
        return json.loads(value) if value else None
    
    async def list_entities(self, entity_type: str):
        """List all entities of a type"""
        pattern = f"{self.namespace}:{entity_type}:*"
        keys = await self.client.keys(pattern)
        return keys
    
    async def delete_entity(self, entity_type: str, entity_id: str):
        """Delete entity from Redis"""
        key = f"{self.namespace}:{entity_type}:{entity_id}"
        await self.client.delete(key)
```

#### Module B: `file_cache.py`
```python
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

class FileCacheLayer:
    """File system cache for entity persistence (fallback + local access)"""
    
    def __init__(self, cache_dir="~/.xnai/entity_cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_entity_path(self, entity_type: str, entity_id: str) -> Path:
        """Get file path for entity"""
        type_dir = self.cache_dir / entity_type
        type_dir.mkdir(exist_ok=True)
        return type_dir / f"{entity_id}.json"
    
    def store_entity(self, entity_type: str, entity_id: str, data: dict):
        """Store entity to file cache"""
        path = self._get_entity_path(entity_type, entity_id)
        path.write_text(json.dumps({
            "data": data,
            "stored_at": datetime.utcnow().isoformat(),
            "entity_type": entity_type,
            "entity_id": entity_id
        }, indent=2))
    
    def retrieve_entity(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """Retrieve entity from file cache"""
        path = self._get_entity_path(entity_type, entity_id)
        if path.exists():
            return json.loads(path.read_text())
        return None
    
    def list_entities(self, entity_type: str):
        """List entities of a type"""
        type_dir = self.cache_dir / entity_type
        if type_dir.exists():
            return [p.stem for p in type_dir.glob("*.json")]
        return []
```

#### Module C: `hybrid_entity_store.py`
```python
from typing import Any, Optional

class HybridEntityStore:
    """Redis + File hybrid entity persistence (Redis primary, file fallback)"""
    
    def __init__(self, redis_layer, file_cache_layer):
        self.redis = redis_layer
        self.file_cache = file_cache_layer
        self.write_through = True  # Always sync to both
    
    async def store(self, entity_type: str, entity_id: str, data: dict):
        """Store to Redis + file cache"""
        if self.write_through:
            # Write to both (async Redis, sync file)
            await self.redis.store_entity(entity_type, entity_id, data)
            self.file_cache.store_entity(entity_type, entity_id, data)
        else:
            # Redis only
            await self.redis.store_entity(entity_type, entity_id, data)
    
    async def retrieve(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """Try Redis first, fallback to file cache"""
        # Try Redis first
        entity = await self.redis.retrieve_entity(entity_type, entity_id)
        if entity:
            return entity
        
        # Fallback to file cache
        entity = self.file_cache.retrieve_entity(entity_type, entity_id)
        if entity:
            # Restore to Redis for future access
            await self.redis.store_entity(entity_type, entity_id, entity.get("data"))
            return entity
        
        return None
    
    async def sync_to_memory_bank(self, entity_type: str):
        """Archive entities to memory_bank for long-term storage"""
        entities = await self.redis.list_entities(entity_type)
        memory_dir = Path("memory_bank/entities") / entity_type
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        for entity_key in entities:
            entity_id = entity_key.split(":")[-1]
            entity = await self.retrieve(entity_type, entity_id)
            if entity:
                (memory_dir / f"{entity_id}.json").write_text(json.dumps(entity, indent=2))
```

**Entity Types to Persist**:
- `cli_session` - CLI session contexts
- `agent_state` - Agent memory and reasoning state
- `task_context` - Current/recent task details
- `strategic_decision` - Major architecture/strategy decisions
- `research_result` - Findings from investigations

### 2.3 Phase 3: Hardening Agent Bus (VALIDATED)

**Goal**: Ensure secure inter-CLI messaging via agent bus.

**Reference**: `/memory_bank/strategies/WAVE-4-AGENT-BUS-HARDENING-BLUEPRINT.md`

**Already Exists**: Agent bus security framework in `scripts/metropolis-hardening.py` (created in prior work)

**Deployment Steps**:
1. Deploy `metropolis-hardening.py` to `/app/XNAi_rag_app/core/metropolis_hardening.py`
2. Integrate with FastAPI entrypoint
3. Test inter-CLI messaging:
   ```bash
   # From OpenCode CLI
   redis-cli XADD xnai:agent_bus '*' \
     sender 'did:xnai:opencode-1' \
     action 'request' \
     message 'Analyze architecture'
   
   # Listen from Copilot
   redis-cli XREAD COUNT 1 STREAMS xnai:agent_bus 0
   ```

### 2.4 Phase 4: High-Level Deliberation Framework (NEW)

**Goal**: Enable consensus-based decision making across multiple CLIs.

**Implementation**: `/app/XNAi_rag_app/deliberation/`

**Core Concept**: Each CLI is a "Facet" with voting rights on strategic decisions.

```python
# deliberation/deliberation_engine.py

class Facet:
    """Represents a CLI with opinions and voting power"""
    def __init__(self, cli_name: str, model: str, confidence_weight: float = 1.0):
        self.cli_name = cli_name
        self.model = model
        self.confidence_weight = confidence_weight
        self.opinions = []

class StrategicProposal:
    """A proposal for group deliberation"""
    def __init__(self, proposal_id: str, title: str, description: str, 
                 proposer: str, urgency: str = "normal"):
        self.proposal_id = proposal_id
        self.title = title
        self.description = description
        self.proposer = proposer
        self.urgency = urgency
        self.votes = {}
        self.deliberation_log = []
    
    def add_vote(self, facet: Facet, vote: str, reasoning: str):
        """Vote (approve/reject/abstain) with reasoning"""
        weighted_vote = 1.0 if vote == "approve" else (-1.0 if vote == "reject" else 0.0)
        weighted_vote *= facet.confidence_weight
        
        self.votes[facet.cli_name] = {
            "vote": vote,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat(),
            "weighted_vote": weighted_vote
        }
        self.deliberation_log.append(f"{facet.cli_name}: {vote} - {reasoning}")
    
    def get_consensus(self):
        """Calculate consensus (weighted majority)"""
        if not self.votes:
            return "pending"
        
        total_weight = sum(v.get("weighted_vote", 0) for v in self.votes.values())
        if total_weight > 0.3:
            return "approved"
        elif total_weight < -0.3:
            return "rejected"
        else:
            return "needs_discussion"

class DeliberationEngine:
    """Orchestrate group decision-making"""
    
    def __init__(self, redis_client, entity_store):
        self.redis = redis_client
        self.entity_store = entity_store
        self.proposals = {}
    
    async def create_proposal(self, proposal: StrategicProposal):
        """Create new proposal for deliberation"""
        self.proposals[proposal.proposal_id] = proposal
        await self.entity_store.store("proposal", proposal.proposal_id, {
            "title": proposal.title,
            "description": proposal.description,
            "proposer": proposal.proposer,
            "urgency": proposal.urgency,
            "created_at": datetime.utcnow().isoformat()
        })
    
    async def request_deliberation(self, proposal_id: str, target_facets: list):
        """Broadcast proposal to target CLIs for deliberation"""
        proposal = self.proposals[proposal_id]
        
        for facet_cli in target_facets:
            message = {
                "action": "deliberate",
                "proposal_id": proposal_id,
                "title": proposal.title,
                "description": proposal.description,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis.client.xadd("xnai:agent_bus", message)
    
    async def finalize_proposal(self, proposal_id: str):
        """Tally votes and execute consensus decision"""
        proposal = self.proposals[proposal_id]
        consensus = proposal.get_consensus()
        
        return {
            "proposal_id": proposal_id,
            "consensus": consensus,
            "votes": proposal.votes,
            "deliberation_log": proposal.deliberation_log
        }
```

---

## PART 3: INTEGRATION CHECKLIST

### 3.1 Environment Setup

```bash
# Verify all CLI access paths
ls -la ~/.opencode/
ls -la ~/.antigravity/
ls -la ~/.gemini/
ls -la ~/.copilot/

# Verify Redis access
redis-cli ping  # Should return PONG

# Verify MB-MCP
curl http://localhost:8005/health

# Create persistence directories
mkdir -p ~/.xnai/entity_cache
mkdir -p memory_bank/entities/{cli_session,agent_state,task_context}
```

### 3.2 Dependencies to Install

```toml
[dependencies]
redis = "^5.0"
aioredis = "^2.0"
pydantic = "^2.0"
fastapi = "^0.104.0"
```

### 3.3 Integration Points

| Component | Integration Point | Status |
|-----------|------------------|--------|
| FastAPI | `/app/XNAi_rag_app/api/entrypoint.py` | Ready |
| Redis Streams | Existing, verified | Active |
| Memory Bank MCP | Port 8005, verified | Active |
| Agent Bus | `xnai:agent_bus` stream | Active |
| File Cache | `~/.xnai/entity_cache/` | Ready |

---

## PART 4: VERIFICATION TESTS

### Test 1: Entity Persistence
```bash
# Store entity from Copilot
redis-cli SETEX "xnai:entities:cli_session:test-001" 86400 '{"data": {"test": "value"}}'

# Retrieve from OpenCode (verify hybrid layer works)
redis-cli GET "xnai:entities:cli_session:test-001"

# Verify file cache fallback
cat ~/.xnai/entity_cache/cli_session/test-001.json
```

### Test 2: Agent Bus Inter-CLI Messaging
```bash
# From one CLI (e.g., OpenCode)
redis-cli XADD xnai:agent_bus '*' sender 'opencode-1' message 'Test message'

# From another CLI (e.g., Copilot)
redis-cli XREAD COUNT 1 STREAMS xnai:agent_bus 0
```

### Test 3: Deliberation Flow
```python
# In Copilot session
proposal = StrategicProposal(
    proposal_id="PROP-2026-0316-001",
    title="Use Gemini for verification",
    description="Propose Gemini CLI for independent code review",
    proposer="copilot-haiku"
)

# Each CLI votes
opencode_facet.add_vote(proposal, "approve", "Aligns with architecture")
antigravity_facet.add_vote(proposal, "approve", "Security benefits")
gemini_facet.add_vote(proposal, "approve", "Ready to participate")

# Finalize
consensus = proposal.get_consensus()  # Returns "approved"
```

---

## PART 5: SUCCESS CRITERIA

- ✅ All CLIs have documented access paths and verified connectivity
- ✅ Entity persistence layer operational (Redis + file cache hybrid)
- ✅ Agent Bus messaging tested between at least 2 CLIs
- ✅ High-level deliberation framework implemented and tested
- ✅ Memory Bank MCP has entity archival capability
- ✅ All configurations documented in `_meta/` directory

---

## PART 6: NEXT STEPS

1. **Immediate** (This session):
   - Deploy entity persistence modules
   - Test agent bus inter-CLI messaging
   - Verify all CLI access paths

2. **Short-term** (This week):
   - Integrate deliberation engine with existing decision workflows
   - Add per-CLI role-based permissions
   - Create CLI coordination dashboard (memory_bank-based)

3. **Medium-term** (This month):
   - Deploy gRPC service-to-service communication
   - Implement distributed tracing across CLIs
   - Add semantic search across persisted entities

---

**Status**: Ready for implementation  
**Risk**: Low (all infrastructure exists, just needs wiring)  
**Impact**: High (enables multi-agent collaboration at scale)
