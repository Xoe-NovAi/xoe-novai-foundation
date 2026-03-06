# KnowledgeMiner Worker

**Last Updated**: 2026-03-01
**Status**: Active Implementation

---

## Overview

The KnowledgeMiner is an autonomous worker that researches and builds the Expert Memory Bank for persistent personas in the Omega Stack.

## Purpose

1. Receive 'expertise_mining' tasks from the Agent Bus
2. Trigger deep research on persona domains
3. Synthesize findings into high-value "Lessons Learned"
4. Inject into Gnosis Engine (LightRAG) for long-term recall

## Implementation

### File Location
`app/XNAi_rag_app/workers/knowledge_miner.py`

### Class: KnowledgeMinerWorker

```python
class KnowledgeMinerWorker(AgentBusClient):
    def __init__(self, agent_did: str = "worker:knowledge_miner:001"):
        super().__init__(agent_did)
```

### Workflow

1. **Task Receipt**: Listen for `expertise_mining` tasks on the Agent Bus
2. **Research**: Use crawler/RAG to research persona and domains
3. **Synthesis**: Create "Lessons Learned" from findings
4. **Injection**: Update entity memory via EntityRegistry
5. **Confirmation**: Mark entity as initialized

## Usage

### Trigger Mining
```python
# Via Agent Bus
task = {
    "type": "expertise_mining",
    "payload": {
        "name": "Kurt Cobain",
        "role": "Music Expert"
    }
}
await agent_bus.publish_task(task)
```

### Entity Initialization
When a new entity is summoned for the first time:
1. EntityRegistry creates `data/entities/{name}.json`
2. KnowledgeMiner receives expertise_mining task
3. Researches persona and related domains
4. Creates initial "Lessons Learned"
5. Entity marked as `is_initialized = True`

## Example: Kurt Cobain

First summoned: "hey kurt cobain"

### Research Domains
- Nirvana
- Grunge
- Seattle Scene
- Fender offsets (guitars)
- DIY aesthetic

### Initial Lessons Learned
- "Kurt Cobain is highly influential in the music domain"
- "Key related domains include Grunge, Seattle, and DIY aesthetic"
- "Known for defining the sound of a generation"

---

## Integration

### Agent Bus
- Stream: `xnai:agent_bus`
- Task Type: `expertise_mining`

### EntityRegistry
- Storage: `data/entities/{name}.json`
- Memory: Procedural and semantic memory layers

### Gnosis Engine
- Storage: PostgreSQL (via LightRAG)
- Vector: Qdrant

---

**Last Updated**: 2026-03-01
