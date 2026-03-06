# Systematic Review Plan: XNAi Foundation Stack

**Date**: 2026-02-16
**Objective**: Review latest implementations, identify gaps, and prepare for XOH 16-phase project.

## Phase 1: High-Level Audit (Automated)
- [ ] Map current architecture using `codebase_investigator`.
- [ ] Verify "Agent Bus" implementation status (Redis vs Filesystem).
- [ ] Check Vikunja integration status (Redis connectivity).
- [ ] Assess Vector Migration progress (FAISS -> Qdrant).

## Phase 2: Manual Inspection & Knowledge Capture
- [ ] **Agent Bus**: Review `app/XNAi_rag_app/core/agent_bus.py` and `scripts/agent_watcher.py`.
- [ ] **Vikunja**: Review `app/XNAi_rag_app/services/curation_bridge.py` and `scripts/curation_worker.py`.
- [ ] **External Docs**: Download Qdrant documentation using `scripts/curate.py` (or fallback).

## Phase 3: Task Creation (Vikunja)
- [ ] Create tasks for:
    - [ ] Agent Bus: Complete Redis migration.
    - [ ] Vikunja: Fix Redis connection issue.
    - [ ] Vector Migration: Execute `migrate_to_qdrant.py`.
    - [ ] Documentation: Update `internal_docs` with findings.

## Phase 4: Agent Dispatch (Deep Dive)
- [ ] Dispatch Cline to review `app/XNAi_rag_app/core/agent_bus.py` for concurrency safety.
- [ ] Dispatch Cline to propose a fix for Vikunja Redis connection.

## Phase 5: Close Out & Transition
- [ ] Verify all critical "Current Project" tasks are tracked.
- [ ] Prepare for XOH 16-phase project kickoff.
