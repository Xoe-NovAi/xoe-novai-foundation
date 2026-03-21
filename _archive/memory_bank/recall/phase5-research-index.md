# Phase 5 Research Index: Sovereign Multi-Agent Cloud

This index tracks all research, findings, and documentation created during the Phase 5 Discovery phase.

## 1. Resource & Environment
- **[Expert Knowledge: Multi-Agent Resource Limits](expert-knowledge/environment/multi-agent-resource-limits.md)**
    - *Topic*: 5.3.1 Memory Partitioning
    - *Findings*: Established RAM quotas for 6.6GB Ryzen host; defined OOM/Degradation triggers.
- **[Strategic Design: Agent Context Continuity](internal_docs/01-strategic-planning/agent-context-continuity.md)**
    - *Topic*: 5.3.2 Shared State
    - *Findings*: Proposed Hybrid Redis-File sync with Ed25519 signing for state handover.

## 2. Agent Bus & Communication
- **[Expert Knowledge: Redis Stream Bus Patterns](expert-knowledge/agent-tooling/redis-stream-bus-patterns.md)**
    - *Topic*: 5.1.1 Task Distribution
    - *Findings*: Optimized XGROUP patterns for local host; persistent delivery over Pub/Sub.
- **[Design: AnyIO Agent Bus Client](internal_docs/04-code-quality/07-agent-bus-client-design.md)**
    - *Topic*: 5.1.2 Implementation
    - *Status*: IN PROGRESS (Assigned to Cline)

## 3. Identity & Security
- **[Expert Knowledge: IAM v2.0 Schema Design](expert-knowledge/security/iam-v2-schema-design.md)**
    - *Topic*: 5.2.1 Human-DID Mapping
    - *Findings*: W3C DID extensions for Agent-Human relationship mapping.
- **[Security Protocol: Handshake Admin Verification](internal_docs/04-code-quality/08-handshake-admin-verification.md)**
    - *Topic*: 5.2.2 Hardening
    - *Status*: TODO (Assigned to Copilot)

## 4. Master Task Tree
- **[Phase 5 Task Tree (JSON)](internal_docs/communication_hub/phase-5-task-tree.json)**
