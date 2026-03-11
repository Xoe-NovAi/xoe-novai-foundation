# 🗺️ Omega Stack Hardening Roadmap 2026
## From Emergency Patching to Continuous Technical Integrity

**Status**: ACTIVE | **Phase**: 4.0 (Integrity Hardening)  
**Baseline**: Hardened Foundation (Post-Audit 2026-03-08)

---

## 🏗️ Pillar 1: Network & Infrastructure (Sovereign Shield)
*Goal: Zero-trust communication between stack components.*

| ID | Objective | Action | Priority |
|:---|:---|:---|:---|
| **NS1** | **Redis TLS/SSL** | Enable TLS for all intra-stack Redis traffic. | 🔴 HIGH |
| **NS2** | **Network Partitioning** | Use Podman network aliases to restrict UI visibility to DBs. | 🟡 MED |
| **NS3** | **Hardware Sentinel** | Auto-adjust model quantization (AWQ/GGUF) based on host RAM. | 🟢 LOW |

---

## 🔑 Pillar 2: Identity & Access (Scoped Sovereignty)
*Goal: Beyond simple tokens to cryptographic identity.*

| ID | Objective | Action | Priority |
|:---|:---|:---|:---|
| **IA1** | **Scoped API Keys** | Replace `auth_token` with RBAC-style scoped keys in IAM DB. | 🔴 HIGH |
| **IA2** | **A2A Signature Check** | Sign all Agent Bus tasks using Ed25519 identity keys. | 🟠 HIGH |
| **IA3** | **OIDC Bridge** | Optional bridge for external developer access via local OIDC. | 🟢 LOW |

---

## 🧪 Pillar 3: Validation & Resilience (The Red-Phone Protocol)
*Goal: Automated verification of failover and kill-switches.*

| ID | Objective | Action | Priority |
|:---|:---|:---|:---|
| **VR1** | **Red-Phone Drills** | Automated CI test for the `emergency_stop` protocol. | 🔴 HIGH |
| **VR2** | **Chaos Monkey** | Randomly terminate core services to verify MCP Fallback. | 🟠 MED |
| **VR3** | **Coverage Target** | Reach 80% coverage on `core/` and `mcp-servers/`. | 🟡 MED |

---

## 🏛️ Pillar 4: Scholarly Intelligence (The Great Library)
*Goal: Transform the stack into a world-class classical research tool.*

| ID | Objective | Action | Priority |
|:---|:---|:---|:---|
| **SI1** | **LCS Deployment** | Implementation of the Library Curation System (Autonomous Crawler). | 🔴 HIGH |
| **SI2** | **Philology Engine** | Integrate Ancient Greek BERT and Ithaca Restoration tools. | 🟠 MED |
| **SI3** | **Vikunja Sync** | Automated research ticket generation for Knowledge Gaps. | 🟡 LOW |

---

## 🧭 Scouted Milestones


### 🏁 Milestone 4.1: Cryptographic Handshake (Q2 2026)
- [ ] Implement IA2: All Agent-to-Agent communication is signed.
- [ ] Implement VR1: Monthly Red-Phone drills integrated into health checks.

### 🏁 Milestone 4.2: Encrypted Backbone (Q3 2026)
- [ ] Implement NS1: Full Redis TLS coverage.
- [ ] Implement IA1: Scoped tokens for all MCP tools.

---

## 🗂️ Archived Epochs
- [x] **Epoch 3.1**: Pydantic Validation & RDB Fixes (March 2026)
- [x] **Epoch 3.2**: Memory Bank Persistence Hardening (March 2026)
- [ ] **Epoch 4.0**: Continuous Integrity Transition (Current)

---
*Document sealed by Gemini General. The path is marked. 🔱*
