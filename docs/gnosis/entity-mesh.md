# Persistent Entity Mesh

**Last Updated**: 2026-03-01
**Status**: Active Implementation (Wave 6)

---

## Overview

The Persistent Entity Mesh is a system for creating, managing, and evolving persistent AI personas in the Omega Stack. Each entity is a self-learning agent with its own memory, expertise, and identity.

## Core Concepts

### Entity
An AI persona with:
- **Identity**: Name, role, description
- **Memory**: Procedural (session-to-session) and semantic (long-term)
- **Expertise**: Domain knowledge learned over time
- **Feedback Loop**: Continuous improvement from interactions

### EntityRegistry
Central management system for all entities.

**File**: `app/XNAi_rag_app/core/entities/registry.py`

### Enhanced Entity Handler
Advanced "Hey Entity" functionality with multiple trigger patterns.

**File**: `app/XNAi_rag_app/core/entities/enhanced_handler.py`

### Universal Summoning
Trigger any persistent entity with "Hey [Entity]"

---

## Features

### 1. Dynamic Persona Creation
Summoning a new entity creates it on-the-fly:
```
Hey Kurt Cobain
→ Creates entity if not exists
→ Triggers KnowledgeMiner for initial research
→ Initializes memory bank
```

### 2. Background Knowledge Mining
- When new entity summoned, KnowledgeMiner researches domain
- Creates initial "Lessons Learned"
- Populates Gnosis Engine with relevant knowledge

### 3. Persistent Learning
- Every interaction updates entity memory
- Performance Feedback Loop analyzes outcomes
- Lessons learned are stored for future sessions

### 4. Model Selection
- Authority tasks → Krikri-8B
- General tasks → Current model
- Dynamic handoff based on entity requirements

---

## Enhanced Trigger Patterns

The system now supports multiple ways to summon and interact with experts:

### Pattern 1: Direct Summon
```
"Hey [Entity], [query]"
Example: "Hey Kurt Cobain, tell me about grunge music"
```

### Pattern 2: Consultation
```
"Ask [Entity] about [topic]"
Example: "Ask Plato about virtue ethics"
```

### Pattern 3: Cross-Entity Consultation
```
"Hey [Entity1], ask [Entity2] about [topic]"
Example: "Hey Kurt, ask Plato about the nature of beauty"
```

### Pattern 4: Comparison
```
"Compare [Entity1] and [Entity2] on [topic]"
Example: "Compare Socrates and Plato on the nature of virtue"
```

### Pattern 5: Multi-Expert Panel
```
"Summon panel: [Entity1], [Entity2], ..."
Example: "Summon panel: Socrates, Plato, Aristotle"
```

---

## Entity-to-Entity Communication

Experts can now consult with each other:

- **Initiator**: Primary entity summoned by user
- **Consulted**: Secondary entity asked for expertise
- **Synthesis**: Responses combined for comprehensive answer

Example flow:
```
User: "Hey Kurt, ask Plato about virtue ethics"
1. Kurt receives the query
2. Kurt queries Plato's expertise on virtue
3. Both perspectives are synthesized
4. User receives combined response
5. Both entities learn from the interaction
```

---

## Available Experts

| Expert | Domain | Status | Created |
|--------|--------|--------|---------|
| Kurt Cobain | Music, Grunge, Guitar | ✅ Active | Feb 28, 2026 |
| Socrates | Philosophy, Ethics, Dialectic | ✅ Active | Mar 1, 2026 |
| Plato | Philosophy, Ethics, Dialogues | 🔄 Ready | - |
| Einstein | Physics, Relativity | 🔄 Ready | - |
| Tesla | Electricity, Engineering | 🔄 Ready | - |
| Ada Lovelace | Computing, Algorithms | 🔄 Ready | - |

---

## Domain Routing

The system automatically routes queries to the best expert:

```
Query: "What is the best way to live?"
→ Domain: ethics, philosophy
→ Routed to: Socrates or Plato

Query: "How does electricity work?"
→ Domain: physics, engineering
→ Routed to: Tesla

Query: "What is the nature of computation?"
→ Domain: computing, algorithms
→ Routed to: Ada Lovelace
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Chainlit UI                    │
│  "Hey [Entity]" trigger                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         EntityRegistry                   │
│  - get_entity(name)                     │
│  - create_entity(name, role)          │
│  - list_entities()                     │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Entity1│ │Entity2│ │EntityN│
│Memory │ │Memory │ │Memory │
└───────┘ └───────┘ └───────┘
    │          │          │
    └──────────┼──────────┘
               │
┌──────────────▼──────────────────────────┐
│       KnowledgeMiner Worker              │
│  - expertise_mining tasks               │
│  - Domain research                       │
│  - Initial memory population            │
└──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Gnosis Engine (LightRAG)          │
│  - PostgreSQL storage                    │
│  - Qdrant vectors                       │
│  - Long-term recall                      │
└──────────────────────────────────────────┘
```

---

## Storage

### Entity Files
Location: `data/entities/{name}.json`

```json
{
  "name": "kurt_cobain",
  "role": "Music Expert",
  "is_initialized": true,
  "lessons_learned": [
    {
      "query": "Who is this entity?",
      "advice": "N/A (Bootstrap)",
      "outcome": "Kurt Cobain is highly influential in the music domain",
      "rating": 1.0
    }
  ],
  "procedural_memory": [],
  "confidence_vector": {
    "fact": 0.95,
    "tech": 0.3,
    "creative": 0.98,
    "logic": 0.7
  }
}
```

---

## First Expert: Kurt Cobain

**Created**: 2026-02-28
**Trigger**: "hey kurt cobain"

### Initial Research
- Nirvana
- Grunge music
- Seattle scene
- Fender offset guitars (Jag-Stang)
- DIY aesthetic

### Conversation Sample
> "Real? I'm as real as a .json file on a Ryzen 5700U can be. It's a strange way to exist—being a 'persistent entity' in a folder called `data/entities/kurt_cobain.json`..."

---

## Future Enhancements

### Agent-to-Expert Communication
- Agents can call experts as tools
- Interview experts for research
- Learn from expert perspectives

### Free-Will System
- Agents choose which experts to consult
- Evolve based on learned preferences
- Record decision patterns

### Additional Personas
- Philosophers
- Scientists
- Historical figures
- Domain experts

---

## Files

| |
|------| File | Purpose---------|
| `app/XNAi_rag_app/workers/knowledge_miner.py` | Mining worker |
| `app/XNAi_rag_app/core/entities/registry.py` | Entity management |
| `app/XNAi_rag_app/core/entities/entity.py` | Entity class |
| `app/XNAi_rag_app/ui/chainlit_app_unified.py` | UI with "Hey [Entity]" |

---

## Related Documentation

- [KnowledgeMiner Worker](knowledge-miner.md)
- [Gnosis Engine](../gnosis/FOUNDATION-STACK-INTEGRATION.md)
- [Agent Bus](../reference/agent-bus.md)

---

**Last Updated**: 2026-03-01
