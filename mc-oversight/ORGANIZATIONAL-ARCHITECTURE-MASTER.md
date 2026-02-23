# Xoe-NovAi Organizational Architecture - Master Strategy

## Status: STAGING IN PROGRESS
**Created**: 2026-02-22
**Owner**: MC-Overseer Agent

---

## Executive Summary

**XNAi = Xoe-NovAi** (brand abbreviation)
**XNAi Foundation** = Core ML platform stack
**Arcana-NovAi** = Esoteric layer stack (future)
**Nova Voice App** = External ML project (Mac-specific)

---

## Clarified Requirements

### Organization Structure
```
Xoe-NovAi/                          # Organization root
├── projects/
│   ├── xnai-foundation/            # Core AI platform
│   ├── arcana-nova/                # Esoteric layer (future)
│   ├── nova-voice/                 # Voice app (Mac)
│   ├── tarot-deck/                 # Custom deck project
│   ├── websites/                   # Web design projects
│   │   ├── xnae-org-site/
│   │   └── entertainment-site/
│   └── research/                   # Research projects
│       ├── ancient-classics/
│       └── cross-domain/
├── shared/
│   ├── memory_bank/                # Shared memory across projects
│   ├── expert-knowledge/           # Shared knowledge base
│   ├── templates/                  # Project templates
│   └── configs/                    # Shared configurations
└── mc-oversight/                   # MC agent management
    ├── org-level/                  # COO-level MC
    ├── ml-tech/                    # ML tech MC
    └── project-specific/           # Project-level agents
```

### MC Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                 TIER 1: ORG-LEVEL MC (COO)                  │
│                                                              │
│  • Complete visibility across ALL projects                  │
│  • Organization strategy and coordination                   │
│  • Resource allocation and prioritization                   │
│  • Cross-project relationship management                   │
│  • Dedicated memory: org-mc-memory                         │
│  • Knowledge base: org-level-kb                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              TIER 2: DOMAIN-LEVEL MC (ML Tech)              │
│                                                              │
│  • Visibility: Foundation + Nova + Arcana-NovAi            │
│  • ML technology coordination                              │
│  • Stack integration and evolution                         │
│  • Research-to-implementation pipeline                     │
│  • Dedicated memory: ml-tech-mc-memory                     │
│  • Knowledge base: ml-tech-kb                              │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   TIER 3: PROJECT-LEVEL MCs                               │
│                                                            │
│  Foundation MC    │  Arcana-NovAi MC   │  Nova Voice MC   │
│  • Stack dev      │  • Esoteric layer  │  • Mac voice app │
│  • Infrastructure │  • Ancient wisdom  │  • Accessibility │
│  • RAG pipeline   │  • Symbolic AI     │  • Audio routing │
│                                                            │
│  Dedicated memory per project                             │
└───────────────────┴───────────────────┴───────────────────┘
```

### Context Switching Architecture

```python
# mc_context_switcher.py
class MCContextSwitcher:
    """
    Seamless context switching between MC levels.
    Preserves long-term memory per context while enabling transitions.
    """
    
    CONTEXTS = {
        "org-coo": {
            "visibility": "all_projects",
            "memory_bank": "shared/memory_bank/org-mc/",
            "knowledge_base": "shared/expert-knowledge/org-level/",
            "projects": "*"
        },
        "ml-tech": {
            "visibility": ["xnai-foundation", "arcana-nova", "nova-voice"],
            "memory_bank": "shared/memory_bank/ml-tech-mc/",
            "knowledge_base": "shared/expert-knowledge/ml-tech/",
            "projects": ["xnai-foundation", "arcana-nova", "nova-voice"]
        },
        "foundation": {
            "visibility": ["xnai-foundation"],
            "memory_bank": "projects/xnai-foundation/memory_bank/",
            "knowledge_base": "projects/xnai-foundation/expert-knowledge/",
            "projects": ["xnai-foundation"]
        },
        "arcana-nova": {
            "visibility": ["arcana-nova", "xnai-foundation"],
            "memory_bank": "projects/arcana-nova/memory_bank/",
            "knowledge_base": "projects/arcana-nova/expert-knowledge/",
            "projects": ["arcana-nova"]
        },
        "nova-voice": {
            "visibility": ["nova-voice"],
            "memory_bank": "projects/nova-voice/memory_bank/",
            "knowledge_base": "projects/nova-voice/expert-knowledge/",
            "projects": ["nova-voice"]
        }
    }
    
    async def switch_context(self, from_context: str, to_context: str):
        """Switch MC context while preserving state"""
        # Save current context state
        await self._save_context_state(from_context)
        
        # Load new context
        await self._load_context_state(to_context)
        
        # Notify relevant systems
        await self._broadcast_context_change(from_context, to_context)
```

---

## Memory Bank Architecture

### Shared + Dedicated Hybrid Model

```
shared/memory_bank/
├── org-mc/                    # Org-level MC memory
│   ├── activeContext.md
│   ├── projectRegistry.md     # All projects overview
│   ├── resourceAllocation.md
│   └── crossProjectRelations.md
│
├── ml-tech-mc/                # ML tech MC memory
│   ├── activeContext.md
│   ├── stackEvolution.md
│   ├── researchPipeline.md
│   └── integrationStatus.md
│
└── templates/                 # Project templates
    ├── project-brief.md
    ├── tech-context.md
    └── system-patterns.md

projects/xnai-foundation/memory_bank/
├── core/                      # Core memory (always loaded)
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   └── progress.md
├── recall/                    # Searchable sessions
├── archival/                  # Long-term reference
└── strategies/                # Strategic planning
```

---

## Project Categories

### Category A: Core Technology (ML Tech MC Domain)
| Project | Type | Status | Integration Level |
|---------|------|--------|-------------------|
| xnai-foundation | Platform | Active | Core stack |
| arcana-nova | Platform | Planned | Future stack |
| nova-voice | External | Active | Integration target |

### Category B: Research & Development
| Project | Type | Status | Domain |
|---------|------|--------|--------|
| ancient-classics | Research | Planned | Classics, Greek BERT |
| cross-domain | Research | Ongoing | Multi-domain synthesis |
| 42-laws-maat | Implementation | Planned | Ethical AI framework |

### Category C: Creative Projects
| Project | Type | Status | Domain |
|---------|------|--------|--------|
| tarot-deck | Creative | In Progress | Divination, symbolism |
| arcana-nova | Platform | Planned | Esoteric AI |

### Category D: Client Projects
| Project | Type | Status | Visibility |
|---------|------|--------|------------|
| xnae-org-site | Website | Future | Org-level MC only |
| entertainment-site | Website | Future | Org-level MC only |

---

## Implementation Staging

### Stage 1: Foundation (Week 1-2)
**Goal**: Establish core organizational structure

1. **Directory Migration**
   - Create `Xoe-NovAi/` organization root
   - Move `xnai-foundation/` to `projects/`
   - Create shared directories
   - Set up MC oversight structure

2. **MC Agent Framework**
   - Implement context switcher
   - Create memory bank architecture
   - Set up visibility controls

3. **Consolidation Planning**
   - Inventory all scattered folders
   - Create migration checklist
   - Plan Xubuntu to Ubuntu migration

### Stage 2: MC Hierarchy (Week 3-4)
**Goal**: Implement multi-tier MC system

1. **Org-Level MC**
   - Complete project visibility
   - Resource allocation
   - Cross-project coordination

2. **ML-Tech MC**
   - Foundation + Nova + Arcana visibility
   - Stack integration
   - Research pipeline

3. **Project-Level MCs**
   - Foundation-specific MC
   - Nova-specific MC (future)

### Stage 3: Consolidation (Week 5-8)
**Goal**: Complete Xubuntu migration and consolidation

1. **Partition Repair**
   - Fix 17GB partition for tarot deck project
   - Recover scattered project files

2. **Migration Execution**
   - Consolidate all codebases
   - Format Xubuntu partition
   - Implement new storage strategy

3. **ARM-64 Setup**
   - Create ARM-64 VM/partition
   - Cross-platform development environment

### Stage 4: Advanced Features (Month 2+)
**Goal**: Implement advanced cross-domain features

1. **Ancient Greek BERT**
   - Embedding for classics research
   - Cross-domain integration

2. **42 Laws of Ma'at**
   - Ethical AI framework
   - Foundation stack integration

3. **Arcana-NovAi Stack**
   - Esoteric layer development
   - Symbolic AI integration

---

## Research Needed

### Immediate (This Session)
- [ ] Vikunja structure options
- [ ] Memory bank hybrid model best practices
- [ ] Context switching implementation patterns

### Near-Term (This Week)
- [ ] Partition repair tools and process
- [ ] ARM-64 Ubuntu Server setup
- [ ] Cross-platform development strategies
- [ ] Ancient Greek BERT availability

### Long-Term (Month 2+)
- [ ] Symbolic AI integration patterns
- [ ] Cross-domain knowledge graph
- [ ] Autonomous expert evolution
- [ ] Ethical AI framework implementation

---

**Status**: Staging plan complete, awaiting immediate research
**Next**: Research Vikunja structure and memory bank hybrid model