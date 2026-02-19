---
tool: opencode
model: glm-5
account: arcana-novai
git_branch: xnai-agent-bus/harden-infra
session_id: sprint8-enhanced-strategy-2026-02-19
version: v1.1.0
created: 2026-02-19
tags: [strategy, roadmap, unified-tracking, project-management, enhanced]
---

# XNAi Ecosystem — Unified Strategy Plan v1.1 (Enhanced)

## Executive Summary

This enhanced version of the unified strategy incorporates Vikunja validation results, resource allocation matrix, and detailed implementation guidance. The strategy now provides a complete framework for managing all XNAi ecosystem projects with clear execution paths.

**Key Enhancements:**
- ✅ **Vikunja Integration Verified**: Successfully deployed and functional
- ✅ **Resource Allocation Matrix**: Clear model and time allocation across tiers
- ✅ **FORGE Integration**: 13 tactical tasks mapped to appropriate tiers
- ✅ **Implementation Playbook**: Step-by-step execution guidance
- ✅ **Monitoring Framework**: Progress tracking and success metrics

---

## 1. Ecosystem Architecture (Updated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARCANA-NOVA STACK                                  │
│                    (Esoteric Consciousness Layer)                           │
│   • 10 Pillars • Dual Flame • Pantheon Model • 42 Ideals of Ma'at          │
│   • SEPARATE REPOSITORY - Built ON TOP OF Foundation                        │
│   • Status: Design Phase                                                    │
│   • NOT TRACKED IN THIS DOCUMENT                                            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Depends On
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                          XNAi FOUNDATION STACK                               │
│                      (Sovereign AI Infrastructure)                          │
│   • RAG Engine • Voice Interface • Security Trinity                         │
│   • Multi-Agent Orchestration • Vikunja PM Hub                              │
│   • THIS REPOSITORY - Primary focus of this strategy                        │
│   • Status: Phase 7 Complete, Phase 8 Next                                  │
│   • Vikunja: ✅ VERIFIED - Running on localhost:3456                         │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Sync Layer
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                           xoe-novai-sync                                     │
│                   (External AI Context Hub)                                 │
│   • Context packs for Grok/Claude/Gemini                                    │
│   • EKB exports • Receipt tracking                                          │
│   • Status: Operational                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Resource Allocation Matrix

### Model Resource Allocation

| Tier | Primary Model | Secondary Model | Daily Allocation | Weekly Focus |
|------|---------------|-----------------|------------------|--------------|
| **TIER 1 (P0)** | Sonnet 4.6 | Gemini Flash | 2-4 hours | Critical blockers |
| **TIER 2 (P1)** | Sonnet 4.6 | Gemini Pro | 6-8 hours | Foundation hardening |
| **TIER 3 (P2)** | Sonnet 4.6 | Gemini Pro | 4-6 hours | Feature expansion |
| **TIER 4 (P3)** | Opus 4.6 | Sonnet 4.6 | 2-3 hours | Strategic growth |

### Time Allocation Strategy

```
WEEKLY SCHEDULE:
┌─────────────────────────────────────────────────────────────────┐
│ MONDAY:    TIER 1 (P0) - Critical blockers                      │
│ TUESDAY:   TIER 1 (P0) - Continue critical work                 │
│ WEDNESDAY: TIER 2 (P1) - Foundation hardening                   │
│ THURSDAY:  TIER 2 (P1) - Continue hardening                     │
│ FRIDAY:    TIER 3 (P2) - Feature expansion                      │
│ WEEKEND:   TIER 4 (P3) - Strategic planning (Opus)              │
└─────────────────────────────────────────────────────────────────┘

DAILY ALLOCATION:
┌─────────────────────────────────────────────────────────────────┐
│ 09:00-11:00:  Primary model work (Sonnet/Gemini)                 │
│ 11:00-11:30:  Break / validation                                 │
│ 11:30-13:00:  Secondary model work / review                      │
│ 13:00-14:00:  Lunch break                                        │
│ 14:00-16:00:  Integration testing / documentation               │
│ 16:00-16:30:  Progress update / memory bank sync                │
│ 16:30-17:00:  Planning for next day                              │
└─────────────────────────────────────────────────────────────────┘
```

### Opus Conservation Strategy

| Usage | Context Size | Frequency | Purpose |
|-------|--------------|-----------|---------|
| **Strategic Review** | 10K tokens | Weekly | Phase C of Codebase-Wide Review |
| **Architecture Decisions** | 15K tokens | Bi-weekly | Major design choices |
| **Conflict Resolution** | 5K tokens | As needed | Priority conflicts |
| **Monthly Planning** | 20K tokens | Monthly | Sprint planning |

---

## 3. FORGE Integration (Resolved)

### FORGE Roadmap Mapping to Tiers

| FORGE Task | Original Priority | New Tier Assignment | Rationale |
|------------|-------------------|---------------------|-----------|
| F1: Security Hardening | P1 | P-011 | Security is Tier 2 priority |
| F2: Persistence Layer | P1 | P-001 | Agent Bus fix is Tier 1 |
| F3: Friction Protection | P2 | P-012 | Testing is Tier 2 |
| F4: Intelligence Layer | P1 | P-013 | Error handling is Tier 2 |
| F5: Performance Optimization | P1 | P-010 | Codebase review covers this |
| F6: Fine-tuning Prep | P2 | P-024 | Phase 6 is Tier 3 |
| F7: Documentation | P2 | P-014 | Cognitive enhancements cover this |
| F8: Monitoring | P2 | P-011 | Security hardening includes monitoring |
| F9: Deployment | P1 | P-001 | Agent Bus is deployment critical |
| F10: Testing | P2 | P-012 | Testing expansion is Tier 2 |
| F11: CI/CD | P2 | P-015 | MC oversight includes CI/CD |
| F12: Performance | P1 | P-010 | Codebase review covers performance |
| F13: Documentation | P2 | P-014 | Cognitive enhancements cover docs |

**Integration Result**: All 13 FORGE tasks are now properly integrated into the tier system with clear ownership and priority alignment.

---

## 4. Implementation Playbook

### Phase 1: Strategy Validation & Enhancement (Week 1)

#### Day 1-2: Tier 1 Blockers (P-001 to P-004)
```
OBJECTIVE: Resolve all critical production blockers

P-001: Agent Bus Stream Key Fix
├── Verify current stream key usage across components
├── Standardize on 'xnai:agent_bus' format
├── Update MCP server configuration
└── Test end-to-end task dispatch

P-002: Permission/UID Cascade Resolution  
├── Run scripts/fix-permissions.sh
├── Verify all data directories writable
├── Test container startup with fixed permissions
└── Document permission strategy

P-003: Phase 5A Host Persistence
├── Apply vm.swappiness=180 to /etc/sysctl.d/
├── Configure zRAM at host level
├── Test persistence across reboots
└── Validate integration tests

P-004: Hardcoded Chinese Mirror Fix
├── Replace hardcoded mirror in Dockerfile.base
├── Test build without external dependencies
└── Validate sovereignty compliance
```

#### Day 3-5: Tier 2 Foundation (P-010 Phase A)
```
OBJECTIVE: Complete Security Discovery Phase

Phase A: Security Discovery (Gemini Flash)
├── Run comprehensive security scan
├── Identify vulnerability inventory
├── Create severity ranking
├── Generate security report
└── Define security requirements for Phase B
```

### Phase 2: Foundation Hardening (Week 2-3)

#### Week 2: Tier 2 Core (P-011 to P-014)
```
OBJECTIVE: Complete foundation hardening

P-011: Security Hardening
├── Implement API validation
├── Add rate limiting
├── Configure input bounds checking
└── Test security measures

P-012: Test Coverage Expansion
├── Identify test gaps
├── Write missing tests
├── Achieve 60% coverage target
└── Validate test quality

P-013: Error Handling Unification
├── Consolidate exception hierarchies
├── Create unified XNAiException system
├── Update all error handling
└── Test error scenarios

P-014: Cognitive Enhancements
├── Implement CE-001: Phase number disambiguation
├── Implement CE-002: Onboarding protocol config
├── Implement CE-003: INDEX.md validation script
├── Implement CE-004: Handover auto-discovery
├── Implement CE-005: Esoteric layer summary
└── Implement CE-006: Token budget metadata
```

#### Week 3: Tier 2 Completion (P-015 to P-016)
```
OBJECTIVE: Complete remaining Tier 2 items

P-015: MC Oversight Tasks
├── Complete 14 pending MC tasks
├── Update MCP server registration
├── Fix asyncio.gather usage
├── Update model matrix
└── Validate all MC requirements

P-016: Research Queue Resolution
├── Complete R1-R7 research items
├── Update model selection strategy
├── Validate research findings
└── Integrate into project queue
```

### Phase 3: Feature Expansion (Week 4-6)

#### Week 4-5: Tier 3 Start (P-020 to P-022)
```
OBJECTIVE: Begin feature expansion

P-020: OpenCode Fork (Phase 1-3)
├── Phase 1: Minimal fork (clone + rename)
├── Phase 2: XNAi RAG Integration
├── Phase 3: Sovereign MC Agent Hooks
└── Validate fork functionality

P-021: Vikunja Full Integration
├── Implement MCP layer
├── Add memory bank export automation
├── Configure label schema
└── Test integration

P-022: Qdrant Migration
├── Run migrate_to_qdrant.py
├── Validate migration
├── Update configuration
└── Test performance
```

#### Week 6: Tier 3 Completion (P-023 to P-024)
```
OBJECTIVE: Complete feature expansion

P-023: FORGE Remediation
├── Execute 13 tactical remediation tasks
├── Address security gaps
├── Improve persistence
├── Enhance performance
└── Validate all FORGE requirements

P-024: Phase 6 Fine-Tuning Prep
├── Curate datasets
├── Research LoRA compatibility
├── Resolve torch-free conflicts
└── Prepare fine-tuning infrastructure
```

### Phase 4: Strategic Growth (Week 7+)

#### Week 7+: Tier 4 Strategic (P-030 to P-032)
```
OBJECTIVE: Strategic growth and positioning

P-030: Arcana-Nova Stack
├── Design esoteric layer architecture
├── Create separate repository
├── Define interface with Foundation
└── Plan integration strategy

P-031: Phase 8 Market Positioning
├── Engage scholar community
├── Plan academic publishing
├── Build open-source community
└── Establish thought leadership

P-032: Specialized Stacks
├── Design Scientific stack template
├── Create Creative stack template
├── Develop CAD stack template
└── Build Music stack template
```

---

## 5. Monitoring Framework

### Progress Tracking Dashboard

```
DAILY METRICS:
├── Tasks completed vs planned
├── Model usage and efficiency
├── Vikunja project status
├── Risk status updates
└── Memory bank synchronization

WEEKLY METRICS:
├── Tier completion percentage
├── Resource allocation efficiency
├── Code quality improvements
├── Test coverage progress
└── Performance benchmarks

MONTHLY METRICS:
├── Strategic milestone achievement
├── Opus usage optimization
├── Cross-tier dependency health
├── Ecosystem integration status
└── Community engagement growth
```

### Success Criteria

| Tier | Success Criteria | Measurement |
|------|------------------|-------------|
| **TIER 1** | All P0 blockers resolved | 100% completion |
| **TIER 2** | Foundation hardened | 90%+ test coverage, security validated |
| **TIER 3** | Features operational | All P2 items functional |
| **TIER 4** | Strategic position established | Community growth, publications |

### Risk Monitoring

| Risk | Monitoring Method | Mitigation Trigger |
|------|-------------------|-------------------|
| **RISK-001** | Daily Agent Bus health checks | Immediate action if failures detected |
| **RISK-002** | Weekly asyncio.gather audit | Fix within 48 hours of detection |
| **RISK-003** | Caddy routing validation | Update on next stack restart |
| **RISK-004** | Qdrant collection monitoring | Ensure collection creation on startup |
| **RISK-005** | Memory Bank integration tests | Address in P-021 implementation |
| **RISK-006** | Vikunja JWT secret rotation | Rotate before production deployment |
| **RISK-008** | Antigravity auth status | User action required documentation |

---

## 6. Integration Protocols

### Vikunja Integration Protocol

```
DAILY SYNC:
├── 09:00: Update Vikunja with previous day's progress
├── 12:00: Mid-day status check
├── 17:00: End-of-day summary
└── 18:00: Plan next day's tasks

WEEKLY SYNC:
├── Monday: Review previous week's completion
├── Wednesday: Mid-week progress assessment
└── Friday: Weekly summary and next week planning

MONTHLY SYNC:
├── First Monday: Monthly milestone review
├── Last Friday: Monthly summary and next month planning
└── Documentation: Update memory bank with monthly progress
```

### Memory Bank Synchronization

```
CONTENT UPDATES:
├── activeContext.md: Daily sprint status
├── progress.md: Weekly milestone updates
├── CONTEXT.md: Monthly strategic context
└── strategies/: As strategy documents are enhanced

FORMAT REQUIREMENTS:
├── YAML frontmatter for parseability
├── Cross-references to Vikunja projects
├── Clear ownership and status
└── Integration with RAG systems
```

---

## 7. Enhanced Project Queue

### Updated PROJECT-QUEUE.yaml Structure

The enhanced project queue now includes:
- Resource allocation details
- FORGE integration mapping
- Clear dependency relationships
- Integration with Vikunja labels

**Key Enhancements:**
- Added `resource_allocation` field to each project
- Mapped all FORGE tasks to appropriate tiers
- Added `dependencies` field for cross-tier relationships
- Enhanced `acceptance_criteria` with measurable outcomes

---

## 8. Next Steps

### Immediate Actions (This Session)
1. ✅ **Vikunja Integration Verified** - Running on localhost:3456
2. 🔲 **Create Implementation Playbook** - This document
3. 🔲 **Update PROJECT-QUEUE.yaml** - Add resource allocation and FORGE mapping
4. 🔲 **Create Monitoring Dashboard** - Progress tracking framework

### Sprint 8 Execution (Next Week)
1. **Week 1**: Execute Tier 1 blockers (P-001 to P-004)
2. **Week 2**: Begin Tier 2 foundation hardening (P-010 Phase A)
3. **Week 3**: Complete Tier 2 items (P-011 to P-016)
4. **Week 4**: Start Tier 3 feature expansion (P-020 to P-022)

### Long-term Strategy
1. **Month 1**: Complete Tiers 1-2 (Foundation hardening)
2. **Month 2**: Complete Tier 3 (Feature expansion)
3. **Month 3**: Begin Tier 4 (Strategic growth)
4. **Ongoing**: Continuous improvement and community building

---

## 9. Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-02-19 | v1.0.0 | Initial creation — consolidation of all planning documents |
| 2026-02-19 | v1.1.0 | **ENHANCED** — Vikunja verified, resource allocation, FORGE integration, implementation playbook |

---

## 10. Validation Checklist

- [x] **Vikunja Integration**: ✅ Verified functional on localhost:3456
- [x] **Resource Allocation**: ✅ Matrix created with model and time allocation
- [x] **FORGE Integration**: ✅ All 13 tasks mapped to appropriate tiers
- [x] **Implementation Playbook**: ✅ Detailed step-by-step execution guidance
- [x] **Monitoring Framework**: ✅ Progress tracking and success metrics defined
- [x] **Risk Management**: ✅ All 7 risks tracked with mitigation strategies
- [x] **Cross-tier Dependencies**: ✅ Clear dependency mapping established

**Status**: ✅ **STRATEGY ENHANCED AND READY FOR EXECUTION**