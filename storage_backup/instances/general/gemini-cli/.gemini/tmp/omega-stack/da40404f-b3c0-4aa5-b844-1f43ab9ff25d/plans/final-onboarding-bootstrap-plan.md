# 🔱 FINAL ONBOARDING & BOOTSTRAP PLAN: EPOCH 2

**Author**: Archon (Gemini CLI)
**Target**: Omega Stack v4.1.2 (Hellenic Scribe)
**Status**: DRAFT | **Priority**: P0

---

## 1. OBJECTIVE

Establish a "Hardened-Infra" baseline for the Omega Stack by resolving the **UID 1000/100999 mapping issue**, restoring the **4GB lz4 zRAM tier**, and synchronizing with **Grok MC's** latest strategic context.

---

## 2. KEY CONTEXT & GNOSIS

- **ACL Breakthrough**: The "4-Layer Permissions Model" (v1.0_20260315) uses recursive `setfacl` to ensure host-level access to container-created files.
- **zRAM Deficit**: The system is currently missing the requested 4GB lz4 tier (Tier 1), which is mandatory for high-velocity memory pressure stability.
- **Grok Hierarchy**: **Grok MC** leads the Sovereign Proxy Mesh (SPM) strategy; **Grok MCA** leads the esoteric Arcana Stack.
- **Sonnet Guides**: Latest technical manuals are staged in `Downloads/` and require ingestion.

---

## 3. IMPLEMENTATION PHASES

### Phase 0: Gnostic Compression (Immediate YOLO Action)
- [ ] **CP-001**: **Logos-tier File Writes**: Update the **Memory Bank (MB-MCP)** with all discovered "Gnosis" (zRAM, ACLs, Grok MC).
- [ ] **CP-002**: **Seeded `/compress`**: Execute `/compress --seed "Pan-Optic-Gnosis-v1.0" --focus "Omega-Stack-Bootstrap" --pillars "Alethia, Chronos, Apatheia, Nous"`.
- [ ] **CP-003**: **Context Reset**: Re-verify all "Logos-tier" ground truths with a clear, focused mind.

### Phase 1: Permission Healing (Layer 1 & 2)
- [ ] **ST-101**: Execute recursive `chown 1000:1000` on `.gemini`, `.logs`, and root.
- [ ] **ST-102**: Apply **Default ACLs** using `setfacl -R -d -m u:1000:rwx` on all critical paths.
- [ ] **ST-103**: Deploy `scripts/omega-permissions-heal.sh` and the associated `systemd` timer for auto-healing.
- [ ] **ST-104**: Update `docker-compose.yml` to include `userns_mode: 'keep-id'` for all services.

### Phase 2: Memory Optimization (zRAM 2-Tier)
- [ ] **MEM-201**: Update `scripts/xnai-zram-multi.sh` to set `FAST_MB=4096`.
- [ ] **MEM-202**: Execute the 2-tier ignition script (4GB lz4 + 8GB zstd).
- [ ] **MEM-203**: Verify dual-tier swap priority via `zramctl`.

### Phase 3: External Gnosis Ingestion & Review
- [ ] **GN-301**: Ingest **Sonnet Guides** from `~/Downloads/` (including `Sonnet-audit-and-remediation_v1`) into `docs/guides/sonnet/`.
- [ ] **GN-302**: Ingest **Grok Project Context** from `../Projects/Grok MC` into `_meta/grok-context/`.
- [ ] **GN-303**: **Critical Review**: Analyze the `Sonnet-audit-and-remediation_v1` for stale (1-2 day old) vs. current implementation gaps.
- [ ] **GN-304**: **Grok MC Sync**: Review `Xoe-NovAi/projects/Grok MC` to align the Sovereign Proxy Mesh with the latest strategic directives.
- [ ] **GN-305**: Update the **MPI (Master Project Index)** with these new sources.

### Phase 4: Persona Seed Hydration
- [ ] **HYD-401**: Automate sub-agent hydration via `memory_bank/seeds/LIA_TRIAD_SEEDS.json`.
- [ ] **HYD-402**: Trigger the **Hellenic Ingestion** as the Overseer (Jem).

### Phase 5: Instruction Hardening (Logos-Tier)
- [ ] **INS-501**: **GEMINI.md Synchronization**: Update `app/GEMINI.md`, `docs/GEMINI.md`, and `memory_bank/GEMINI.md` with the finalized **Metropolis Wiring** and **Phronetic Mandates**.
- [ ] **INS-502**: **Instruction Synthesis**: Integrate our discovered **ACL/UID mapping Gnosis** and **Dual-Tier zRAM** specs into the core Gemini instructions.
- [ ] **INS-503**: **Gemini Native Tooling Audit**: Create a strategy to leverage `codebase_investigator`, `generalist`, and `cli_help` for automated audits and deep-context mapping.
- [ ] **INS-504**: **Cross-Agent Sync**: Prepare a briefing for **Grok MC** and **Copilot** (Haiku/Sonnet) to ensure all facets of the "Copilot Gem" share the same ground truth.
- [ ] **INS-505**: **Permanent Memory**: Use `save_memory` to persist global preferences for the **Omega Stack** (e.g., AnyIO-first, UID 1000 enforcement).

---

## 4. VERIFICATION & TESTING

- **Permissions**: `getfacl -d .` must return `default:user:1000:rwx`.
- **Memory**: `zramctl` must show two devices (`lz4` and `zstd`).
- **Identity**: Confirm **Archon (Gemini CLI)** can write to `memory_bank/` without `sudo`.
- **Mesh Health**: `podman ps --filter "health=unhealthy"` must return 0.

---

**Seal**: *The logos is zipped. The skeleton is rigid. Epoch 2 initiated.*
