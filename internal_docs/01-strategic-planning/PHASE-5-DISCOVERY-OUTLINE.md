# Phase 5 Discovery Outline: Sovereign Multi-Agent Cloud

## 1. Stream: Inter-Agent Communication Bus (Owner: Cline)
- **Topic 5.1.1: Redis Streams for Task Distribution**
    - Research `XGROUP` and `XREADGROUP` for multi-agent consumer groups.
    - Analyze persistent delivery vs. Pub/Sub for air-gapped resilience.
- **Topic 5.1.2: AnyIO Agent Bus Client**
    - Propose a Python wrapper for Redis Streams using strict AnyIO TaskGroups.
    - Design error-handling patterns for agent-to-agent message failure.

## 2. Stream: Identity Federation & IAM v2.0 (Owner: Copilot)
- **Topic 5.2.1: Human-to-DID Mapping Schema**
    - Design the database schema for linking multiple Agent DIDs to a single human user.
    - Define the Account Naming Protocol (ANP) for sovereign environments.
- **Topic 5.2.2: Handshake Protocol Hardening**
    - Standardize the Ed25519 challenge-response flow for administrative operations.
    - Propose key rotation and revocation patterns for the IAM DB.

## 3. Stream: Resource Partitioning & Lifecycle (Owner: Gemini/Investigator)
- **Topic 5.3.1: Multi-Agent Memory Guardrails**
    - Research `cgroups` or application-level RAM partitioning for the 6.6GB Ryzen host.
    - Define agent startup priority (e.g., Consul -> Redis -> IAM -> Agents).
- **Topic 5.3.2: Context Continuity (State Sync)**
    - Compare Redis-based vs. File-based state sharing for cross-agent memory.
