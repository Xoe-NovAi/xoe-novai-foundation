---
title: Documentation & Diagram Impact Protocol
version: 1.0
status: active
tags: [documentation, refactor, protocol, metropolis]
last_sync: 2026-03-10
---

# 📄 Documentation & Diagram Impact Protocol (v1.0)

**Mandate**: Every code refactor, architectural change, or secret rotation MUST trigger a documentation impact assessment.

## 1. Impact Assessment Matrix

| Change Type | Primary Docs to Update | Diagram Files |
|:---|:---|:---|
| **Secret Rotation** | `memory_bank/MPI.md`, `.env.example` | N/A |
| **New Service/MCP** | `SESSIONS_MAP.md`, `mcp_config.json` | `docs/architecture/METROPOLIS_WIRING_MAP.md` |
| **API Refactor** | `docs/api/`, `KNOWLEDGE-HUB.md` | `docs/architecture/service-wiring.md` |
| **Protocol Change** | `docs/protocols/`, `GEMINI.md` | `docs/architecture/METROPOLIS-AGENT-BUS.md` |
| **Storage Change** | `redis-schemas-design.md`, `MPI.md` | `docs/architecture/diagrams/storage-flow.mermaid` |

## 2. The "Refactor Hook"
Before completing any task marked as "Refactor" or "Implementation":
1. Run `grep -r "[Symbol/Service Name]" docs/` to find stale references.
2. Update the corresponding `GEMINI.md` in the affected domain.
3. If the service mesh changes, update the Mermaid source in `docs/architecture/`.

## 3. Verification
A task is not **COMPLETE** until the "Documentation Sync" step is checked in the session log.

---
*Locked by Gemini General. Protocol active across the Metropolis Mesh. 🔱*
