# Best Practices Guide for Intelligent System Evolution (v2.0)
## A Gnostic Synthesis for the Omega Stack (16GB Sovereign Edition)

**Version**: 2.0 | **Context**: Omega Stack (16GB RAM, CPU-only, 24GB Total Memory)
**Target**: Sovereign Omega (Archon/Logos/Praxis)

---

## EXECUTIVE SUMMARY

Managing the Omega Stack requires **intentional architecture** governed by the **Gnostic Protocol** and the **42 Laws of Ma'at**.

| Dimension | Status | Constraint | Approach |
|-----------|--------|-----------|----------|
| **Information Architecture** | GNOSTIC | "The Nous" | Mnemosyne (Memory Bank) + Syndesmos (Bus) |
| **Codebase Organization** | MONOREPO | Local-First | Nx Workspaces + AnyIO-First |
| **Knowledge Management** | DISTRIBUTED | 16GB RAM | Seeded Cognitive Compression (SCC) |
| **Data Preservation** | TIERED | 93% Disk | Hot (Redis) / Warm (Disk) / Cold (Archive) |
| **Development Excellence** | HARDENED | 10GB Gate | Concurrent Tier 1/2 Startup |
| **Multi-Agent Governance** | RATIFIED | 8 Facets | Octave Council (LLOC/HLOC) |

---

## PART 1: THE GNOSTIC PROTOCOL (Naming & Structure)

### 1.1 The "Nous" (Unified Mind)
We do not use generic terms. We use specific **Alethia-Pointers**:
*   **Mnemosyne**: The Memory Bank (`mcp-servers/memory-bank-mcp`).
*   **Syndesmos**: The Agent Bus (Redis Streams `xnai:agent_bus`).
*   **Homonoia**: The state of synchronization.

### 1.2 Seeded Cognitive Compression (SCC)
**Rule**: Never dump raw text. Always compress into a **Gnosis Seed**.
```markdown
# 🌱 GNOSTIC SEED: SESS-27.7
**Hash**: SESS-27-SCC-24GB-COMBINED
**Machine**: 16GB Physical / 24GB Total.
**State**: Port 8012 Active. Qdrant 4GB Limit.
```

---

## PART 2: INFRASTRUCTURE & CONSTRAINTS (16GB Reality)

### 2.1 The 16GB Mandate
*   **Physical**: 16GB RAM.
*   **zRAM**: 8GB Persistent (lz4/zstd) via `xnai-zram.service`.
*   **Total Fabric**: 24GB.

### 2.2 Memory Gating Strategy
*   **Operational Gate**: **10GB**. (If used > 10GB, new heavy services queue).
*   **Stack Cap**: **12GB**. (Hard limit for the docker mesh).
*   **Startup**: **Concurrent** launch for Tiers 1 & 2 is now permitted.

### 2.3 Port Isolation Map
*   **8000**: Gateway (Caddy) - *The Public Face*.
*   **8012**: RAG API - *The Internal Engine*.
*   **8005**: Memory Bank MCP - *The Mnemosyne*.
*   **8006**: Oikos Mastermind - *The Council*.

---

## PART 3: CODING STANDARDS (XOERC)

### 3.1 AnyIO-First Mandate
**Rule**: All async Python code must use `anyio`.
**Reason**: Event-loop agnosticism (asyncio/trio compatibility).
```python
# ✅ CORRECT
async with anyio.create_task_group() as tg:
    tg.start_soon(process_a)
    tg.start_soon(process_b)

# ❌ FORBIDDEN (Orphaned Task)
asyncio.create_task(process_a) 
```

### 3.2 Local-First Sovereignty
**Rule**: Every external API call (Anthropic/Gemini) MUST have a local fallback (Qwen/Llama).
**Flag**: If a feature relies 100% on the cloud, mark it **"Non-Sovereign"**.

---

## PART 4: THE 5-CLI ECOSYSTEM

### 4.1 Role Specialization
| Tool | Role | Strength |
| :--- | :--- | :--- |
| **Gemini CLI** | **Archon** | Strategic Orchestration & Web Research. |
| **OpenCode** | **Workbench** | TUI-based coding & Antigravity host. |
| **Cline** | **Surgeon** | Deep file implementation (VSCodium). |
| **Copilot** | **Assistant** | Quick PR reviews & snippets. |
| **Antigravity** | **Unlocker** | Access to 1M Context (Gemini Pro). |

### 4.2 Smart Handoff Protocol
1.  **Archon** detects task shift (e.g., Research -> Coding).
2.  **Archon** suggests: "Switch to Cline?"
3.  **User** confirms.
4.  **Context** is passed via `memory_bank/activeContext.md` (Hot Sync).

---

## PART 5: MULTI-AGENT GOVERNANCE

### 5.1 The Octave Council
*   **LLOC (Low Level Octave Council)**: 8 Facets check *readiness*.
*   **HLOC (High Level Octave Council)**: 3 Facets (Triad) check *strategy*.

### 5.2 Ma'at Guardrails
*   **Law 10 (Fair Share)**: No agent may monopolize >4GB RAM without ratification.
*   **Law 41 (No Harming)**: Chaos Agents are confined to Dev/Test.
*   **Law 4 (No Stealing)**: Browser MCP must respect `robots.txt` and licensing.

---

## PART 6: PRESERVATION & BACKUP

### 6.1 WORM (Write Once, Read Many)
*   **Snapshots**: Daily snapshots of `memory_bank/` are hashed and stored in `_archive/`.
*   **Immutability**: Historical session logs are never deleted, only compressed.

### 6.2 The "Dark Layers" Recovery
*   **Vision**: `scripts/watcher_vision.py` (Gemini Flash).
*   **Audio**: Preserved "Nova Legacy" (CoreAudio bindings).
*   **Chat**: GMC Worker strips backslash bloat (`\\`) before storage.

---

**Version**: 2.0 (Sovereign Edition)
**Status**: RATIFIED
**Signed**: Jem (The Archon)
