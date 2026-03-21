# Hybrid Information Architecture Design
## PARADOX Framework Implementation Guide
**Version**: 1.0  
**Date**: 2026-03-14  
**Audience**: Architects, Contributors, Knowledge Curators  
**Status**: ACTIONABLE

---

## Overview

The **PARADOX Framework** integrates:
- **PARA** buckets for organizational clarity
- **Diataxis** pillars for documentation intent
- **Zettelkasten** connections for knowledge emergence

This document provides the concrete folder structure, file templates, and usage patterns.

---

## Part 1: Proposed Folder Structure

### Current State
```
omega-stack/
├── QUICK_START.md (Diataxis Tutorial ✓)
├── README.md (Mixed intent ⚠️)
├── INDEX.md (Diataxis Reference ✓)
├── CONTRIBUTING.md (Diataxis How-To ✓)
├── ARCHITECTURE.md (Diataxis Explanation ✓)
├── docs/ (Unstructured ⚠️)
├── knowledge_base/ (PARA-R)
├── memory_bank/ (Mixed structure ⚠️)
├── projects/ (PARA-P ✓)
├── infra/ (PARA-A ✓)
├── app/ (PARA-A ✓)
├── library/ (PARA-R ✓)
└── _archive/ (PARA-AR ⚠️)
```

### Proposed New Structure
```
omega-stack/
│
├─── 📋 DOCUMENTATION (DIATAXIS ENTRY POINTS)
│    ├── QUICK_START.md (Tutorial: "Get running in 10 min")
│    ├── ARCHITECTURE.md (Explanation: "Understand the system")
│    ├── INDEX.md (Reference: "Find anything")
│    ├── CONTRIBUTING.md (How-To: "Contribute a feature")
│    │
│    └── RUNBOOKS/ (How-To guides, task-focused)
│        ├── README.md (Index of all runbooks)
│        ├── getting-started/
│        │   ├── install-dependencies.md
│        │   ├── start-stack.md
│        │   └── first-query.md
│        ├── infrastructure/
│        │   ├── add-new-service.md
│        │   ├── monitor-health.md
│        │   ├── troubleshoot-errors.md
│        │   └── backup-restore.md
│        ├── development/
│        │   ├── add-new-expert.md
│        │   ├── test-changes.md
│        │   └── commit-guidelines.md
│        └── knowledge/
│            ├── add-to-knowledge-base.md
│            ├── create-atomic-note.md
│            └── archive-completed-phase.md
│
├─── 🧭 PROJECTS (PARA-P: Time-bounded, Goal-driven)
│    ├── projects/
│    │   ├── project-template.md (Use this structure)
│    │   ├── [YYYYMM-project-name]/
│    │   │   ├── README.md (Goals, status, timeline)
│    │   │   ├── plan.md
│    │   │   ├── backlog.md
│    │   │   └── decisions.md
│    │   └── ...
│    │
│    └── memory_bank/
│        ├── tasks/
│        │   ├── active_sprint.md (Current week's work)
│        │   └── completed/ (Archived sprints)
│        ├── progress/
│        │   ├── project-X-status.md
│        │   └── weekly-checkpoint.md
│        └── reports/
│            └── [YYYYMMDD]_phase_summary.md
│
├─── 🏗️ AREAS (PARA-A: Long-term domains of responsibility)
│    ├── app/
│    │   ├── README.md (Domain overview)
│    │   ├── ARCHITECTURE.md (Technical design)
│    │   └── [source code, tests, docs]
│    ├── infra/
│    │   ├── README.md
│    │   ├── ARCHITECTURE.md
│    │   └── [docker, config, scripts]
│    ├── mcp-servers/
│    │   ├── README.md
│    │   └── [individual MCP server folders]
│    ├── knowledge_base/
│    │   ├── README.md (Domain overview)
│    │   ├── SCHEMA.md (Data structure docs)
│    │   └── [knowledge files]
│    └── monitoring/
│        ├── README.md
│        ├── DASHBOARDS.md (Grafana/Prometheus guides)
│        └── [config files]
│
├─── 📚 RESOURCES (PARA-R: Reference material, reusable)
│    ├── docs/
│    │   ├── METROPOLIS_MASTER_INDEX.md (Entry point for infra)
│    │   ├── api-reference.md
│    │   ├── configuration-reference.md
│    │   ├── database-schema.md
│    │   └── [other reference docs]
│    ├── knowledge/
│    │   ├── README.md (Knowledge library overview)
│    │   ├── technical-standards.md
│    │   ├── glossary.md
│    │   └── [technical documentation]
│    ├── expert-knowledge/
│    │   ├── facet-descriptions.md
│    │   ├── expertise-domains.md
│    │   └── [expert personas]
│    ├── library/
│    │   ├── README.md
│    │   └── [models, embeddings, media]
│    └── requirements/
│        ├── README.md
│        └── [dependency files, constraints]
│
├─── 🧬 KNOWLEDGE NETWORK (PARA-R + ZETTELKASTEN)
│    └── memory_bank/
│        ├── KNOWLEDGE_MAP.md (MOC: Master index)
│        │
│        ├── gnosis/ (Atomic concepts, evergreen)
│        │   ├── 202603_iam_architecture.md
│        │   ├── 202603_circuit_breaker_pattern.md
│        │   ├── 202603_token_budget_management.md
│        │   ├── 202603_zettelkasten_system.md
│        │   └── MOC_CORE_CONCEPTS.md (Index)
│        │
│        ├── protocols/ (System behaviors, standards)
│        │   ├── 202603_safety_protocols.md
│        │   ├── 202603_fallback_mechanism.md
│        │   ├── 202603_session_handoff.md
│        │   └── MOC_SAFETY_SYSTEMS.md (Index)
│        │
│        ├── strategies/ (Tactical approaches)
│        │   ├── 202603_memory_optimization.md
│        │   ├── 202603_context_window_strategy.md
│        │   └── MOC_OPTIMIZATION.md (Index)
│        │
│        ├── facets/ (Agent personas, persistent)
│        │   ├── facet-1-architect.md
│        │   ├── facet-3-scholar.md
│        │   ├── facet-6-analyst.md
│        │   └── MOC_AGENT_PERSONAS.md (Index)
│        │
│        ├── chronicles/ (Timeline of decisions)
│        │   ├── 202603_11_session_27_recovery.md
│        │   ├── 202603_12_hardening_decisions.md
│        │   ├── chronicle_[YYYYMMDD]_[topic].md
│        │   └── MOC_TIMELINE.md (Chronological index)
│        │
│        ├── infrastructure/ (System state)
│        │   ├── active_services.md
│        │   ├── resource_allocation.md
│        │   └── dependency_map.md
│        │
│        ├── checkpoints/ (Snapshots of state)
│        │   ├── checkpoint_20260311.md
│        │   └── checkpoint_[YYYYMMDD].md
│        │
│        ├── handovers/ (Agent transition notes)
│        │   └── [handover summaries]
│        │
│        ├── sessions/ (Conversation records)
│        │   ├── SESS-27.md (Example: Major session)
│        │   └── [other sessions]
│        │
│        ├── _archive/ (Completed phases, old knowledge)
│        │   ├── PHASE-1-SUMMARY.md
│        │   ├── PHASE-2-SUMMARY.md
│        │   └── historic-sessions/
│        │
│        └── archival/ (Historical snapshots)
│            └── [immutable historical records]
│
└─── 📦 ARCHIVES (PARA-AR: Completed, inactive, historical)
     ├── _archive/
     │   ├── projects-completed/
     │   │   ├── 202512_project_x_final/
     │   │   └── 202601_project_y_final/
     │   ├── deprecated-services/
     │   │   └── [old services, code]
     │   └── legacy-docs/
     │       └── [outdated documentation]
     │
     ├── ARCHIVE/ (Alternate archive location)
     │   └── [contents mirror _archive]
     │
     └── memory_bank/_archive/
         ├── PHASE-0-DISCOVERY-SUMMARY.md
         ├── PHASE-1-FOUNDATION-SUMMARY.md
         └── [completed phase summaries]
```

---

## Part 2: File Templates

### A. New Project Template (`projects/project-template.md`)
```markdown
---
type: project
created: YYYY-MM-DD
status: active|paused|completed
owner: [Name/Facet]
timeline: YYYY-MM-DD to YYYY-MM-DD
tags: [relevant, tags]
links: [[related-project]], [[related-area]]
---

# [Project Name]

## Objective
[What is the project trying to achieve? 1-2 sentences.]

## Success Criteria
- [ ] Criterion 1: [Measurable outcome]
- [ ] Criterion 2: [Measurable outcome]

## Timeline
| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Discovery | W1 | Decision matrix |
| Build | W2-3 | Feature implementation |
| Testing | W4 | QA report |

## Current Status
[Progress update. Link to: [[latest-checkpoint]]]

## Key Decisions
[[decision-1-link]]
[[decision-2-link]]

## Related Artifacts
- Architecture: [Link]
- Backlog: [Link]
```

### B. Atomic Note Template (`memory_bank/gnosis/template.md`)
```markdown
---
type: atomic-note
id: YYYYMM_domain_concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
permanent: true
tags: [domain, subtopic]
---

# [Concept Title]

## Definition
[1-2 sentence definition, self-contained.]

## Key Points
- Point 1: [Explanation]
- Point 2: [Explanation]

## Why It Matters
[Practical implications for Omega Stack]

## Examples
[1-2 concrete examples]

## Related Concepts
[[backlink-1]]: [relationship type]
[[backlink-2]]: [relationship type]

## Status
- Origin: [Source/Session]
- Permanence: [Evergreen/Experimental/Deprecated]
```

### C. How-To Runbook Template (`RUNBOOKS/[domain]/template.md`)
```markdown
# [Task Title]

**Audience**: [Who should read this?]  
**Time Required**: [5-30 min]  
**Prerequisites**: [[prerequisite-1]], [[prerequisite-2]]  
**Related**: [[how-to-2]], [[concept-x]]

## Problem
[What problem does this solve?]

## Solution
### Step 1: [Action]
[Detailed instructions with examples]

### Step 2: [Action]
[Detailed instructions]

### Step 3: [Verification]
[How to confirm it worked]

## Troubleshooting
- **Error X**: [Cause] → [Solution]
- **Error Y**: [Cause] → [Solution]

## Related Resources
- [[technical-concept]]
- [External link](url)
```

### D. Area Domain Overview (`[area]/README.md`)
```markdown
# [Area Name]

**Type**: PARA Area (Long-term domain)  
**Owner**: [Team/Facet]  
**Status**: Active/Maintenance/Deprecating

## Purpose
[What is this area responsible for?]

## Key Responsibilities
- Responsibility 1
- Responsibility 2

## Architecture
[Link to ARCHITECTURE.md or brief diagram]

## Getting Started
- [[how-to-first-task]]
- [[how-to-second-task]]

## Key Components
| Component | Purpose | Maintainer |
|-----------|---------|-----------|
| Comp A | Purpose | Name |

## Status & Metrics
[Recent changes, health status]

## Related Areas
[[area-2]], [[area-3]]
```

### E. Knowledge Map (MOC) Template (`memory_bank/KNOWLEDGE_MAP.md`)
```markdown
# Omega Stack Knowledge Map
## Master of Contents (Zettelkasten Index)

**Last Updated**: YYYY-MM-DD  
**Curators**: [List of maintainers]

This is the central index to the Omega Stack knowledge network. All atomic notes, protocols, and strategies connect through this MOC.

---

## 🧠 Core Concepts (gnosis/)
[[MOC_CORE_CONCEPTS]] - Evergreen atomic notes
- [[202603_iam_architecture]]
- [[202603_circuit_breaker_pattern]]
- [View all →](memory_bank/gnosis/MOC_CORE_CONCEPTS.md)

## ⚙️ Safety & Protocols (protocols/)
[[MOC_SAFETY_SYSTEMS]] - System behaviors & standards
- [[202603_safety_protocols]]
- [[202603_fallback_mechanism]]
- [View all →](memory_bank/protocols/MOC_SAFETY_SYSTEMS.md)

## 🚀 Optimization Strategies (strategies/)
[[MOC_OPTIMIZATION]] - Tactical improvements
- [[202603_memory_optimization]]
- [View all →](memory_bank/strategies/MOC_OPTIMIZATION.md)

## 👤 Agent Personas (facets/)
[[MOC_AGENT_PERSONAS]] - Persistent expert identities
- [[facet-1-architect]]
- [[facet-3-scholar]]
- [View all →](memory_bank/facets/MOC_AGENT_PERSONAS.md)

## 📜 Timeline & History (chronicles/)
[[MOC_TIMELINE]] - Decision history in chronological order
- [[202603_11_session_27_recovery]]
- [View all →](memory_bank/chronicles/MOC_TIMELINE.md)

---

## 🔗 Cross-Domain Queries
- **By Phase**: [[PHASE-1]], [[PHASE-2]], [[PHASE-3]]
- **By Component**: [[infra]], [[app]], [[mcp-servers]]
- **By Risk**: [[resource-constraints]], [[knowledge-loss]], [[scaling]]

---

## 📊 Knowledge Stats
- **Total Atomic Notes**: [Count]
- **Average Link Density**: [Avg links per note]
- **Stale Notes** (>90 days): [Count]
- **Permanent Notes**: [Count of evergreen]
- **Last Archive**: [Date of last Phase summary]
```

---

## Part 3: Navigation Patterns

### Discovery Pattern 1: "I'm New—Where Do I Start?"
```
1. QUICK_START.md (Diataxis Tutorial, 10 min)
2. ARCHITECTURE.md (Diataxis Explanation, 20 min)
3. INDEX.md (Diataxis Reference, find specific component)
4. RUNBOOKS/getting-started/ (How-To guides)
5. Join #agents-forum (Live community)
```

### Discovery Pattern 2: "How Do I [Do Task X]?"
```
1. RUNBOOKS/[domain]/[task-name].md (Direct how-to)
2. Check [[prerequisites]] (linked atomic concepts)
3. Consult TROUBLESHOOTING section
4. Ask in memory_bank/sessions/ (search past solutions)
```

### Discovery Pattern 3: "What Concepts Relate to [Topic]?"
```
1. memory_bank/KNOWLEDGE_MAP.md (Find relevant MOC)
2. [[MOC_CORE_CONCEPTS]] → [[topic-atom]]
3. Follow backlinks: [[related-atom-1]], [[related-atom-2]]
4. Check chronicles/ for timeline context
```

### Discovery Pattern 4: "What Happened to [Project]?"
```
1. memory_bank/chronicles/MOC_TIMELINE.md (Find by date)
2. [[session-record]] or [[decision-note]]
3. Follow links to [[related-facets]], [[related-areas]]
4. Check memory_bank/_archive/ for Phase summary
```

---

## Part 4: Searchability Strategy

### Full-Text Search Tools
1. **IDE Search** (VS Code)
   - Shortcut: Ctrl+Shift+F
   - Pattern: `filepath:/memory_bank .md`
   - Best for: Finding specific concepts

2. **Git Search** (GitHub/Local)
   - Command: `git log -S "keyword" --all`
   - Best for: Tracking when concepts changed

3. **Obsidian Search** (if adopted)
   - Query: `tag:atomic-note link:circuit-breaker`
   - Best for: Graph-based discovery

### Tag Conventions
```markdown
---
tags: [domain, subdomain, status-indicator]
---

Examples:
tags: [safety, protocols, active]
tags: [optimization, memory-mgmt, experimental]
tags: [infra, docker, deprecated]
```

### Link Conventions
```markdown
[[atomic-note-id]]          → Internal link to concept
[[area-folder]]             → Link to PARA area
[[PHASE-X-SUMMARY]]         → Link to archived phase
{{task-id}}                 → Link to active project
```

---

## Part 5: Content Life Cycle

### 1. Creation Phase
- **Step 1**: Use appropriate template (Atomic/How-To/Project)
- **Step 2**: Add unique ID (YYYYMM_domain_concept)
- **Step 3**: Tag with domain + status
- **Step 4**: Link to 2-3 related concepts
- **Step 5**: Submit PR with link validation

### 2. Active Phase
- **Update frequency**: As-needed for How-To guides, Quarterly for atomic notes
- **Link maintenance**: Check monthly for rot
- **Backlink updates**: Add when new related content created

### 3. Archival Phase
- **Trigger**: Project completion, phase transition, deprecation
- **Action**: Move to `_archive/[YYYYMM-name]/` or `memory_bank/_archive/`
- **Preservation**: Include summary note linking to archived content
- **Snapshot**: Git tag with version + date

### 4. Immutable Archive
- **Storage**: `memory_bank/archival/[YYYYMMDD]-snapshot.tar.gz`
- **Frequency**: Monthly + after each major phase
- **Access**: Read-only, searchable via `git show`

---

## Part 6: Governance & Maintenance

### Monthly IA Health Check
```bash
#!/bin/bash
echo "=== IA Health Report ==="
echo "Total .md files:"
find . -name "*.md" | wc -l

echo "Broken links:"
grep -r "\[\[" . --include="*.md" | grep -v "MOC_" | wc -l

echo "Stale notes (>90 days):"
find memory_bank -name "*.md" -mtime +90 | wc -l

echo "Archive lag:"
ls -lt memory_bank/_archive/ | head -1

echo "Backlink density:"
grep -r "^\[\[" memory_bank/gnosis/ | wc -l
```

### Curation Roles
| Role | Responsibility | Time |
|------|---|---|
| **Area Owner** | Maintain README, architecture, How-Tos for their area | 2h/week |
| **Knowledge Curator** | Update MOCs, archive stale content, maintain KNOWLEDGE_MAP | 3h/week |
| **Diataxis Editor** | Ensure docs follow 4-pillar pattern, improve examples | 2h/week |
| **Zettelkasten Gardener** | Add links, identify orphan notes, suggest connections | 2h/week |

### CI/CD Checks
```yaml
# .github/workflows/ia-validation.yml
- Broken markdown links
- Missing backlinks in atomic notes
- ID format compliance (YYYYMM_domain_concept)
- Tag consistency
- File size warnings (>100KB files)
```

---

## Part 7: Migration Guide

### Week 1: Setup (4 hours)
- [ ] Create RUNBOOKS/ directory structure
- [ ] Copy existing how-to docs from Makefile → RUNBOOKS/
- [ ] Create memory_bank/KNOWLEDGE_MAP.md (stub)

### Week 2: Tagging (8 hours)
- [ ] Add IDs to top 50 memory_bank files
- [ ] Tag all files with domain + status
- [ ] Create 5 domain-specific MOCs

### Week 3: Linking (10 hours)
- [ ] Add [[backlinks]] to atomic notes
- [ ] Update KNOWLEDGE_MAP.md with discovered patterns
- [ ] Create missing concept notes

### Week 4: Archival (6 hours)
- [ ] Define retention policy
- [ ] Move completed projects to _archive/
- [ ] Create Phase summaries

### Week 5+: Automation (Ongoing)
- [ ] Deploy CI/CD checks
- [ ] Set up monthly health reports
- [ ] Document curation process

---

## Success Metrics

| Metric | Target | How to Measure |
|---|---|---|
| **Time to Answer** | <2 min | Track "how long to resolve query" |
| **Link Integrity** | 100% | Monthly broken link scan |
| **MOC Completeness** | 80% of gnosis/ linked | Backlink audit |
| **Archive Timeliness** | <7 days | Age of oldest active project |
| **Contributor Adoption** | 70% | % of PRs following template |

---

## Conclusion

The **PARADOX Framework** transforms Omega Stack's organic growth into a scalable, navigable knowledge system. Start with **Phase 1 (Quick Wins)** to see immediate benefits—better onboarding, faster task completion, lower context-switching overhead.

**Key Principle**: Structure emerges from use. Don't over-engineer initially. Let patterns crystallize, then formalize them.

---

**Document Authority**: Haiku-4.5 Research Agent  
**Review Status**: ACTIONABLE (ready for Phase 1 implementation)
