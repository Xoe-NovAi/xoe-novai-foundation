# 🤵 The Butler: Sovereign Infrastructure System

## 🎯 System Overview
**The Butler** is the specialized infrastructure orchestration layer of the Xoe-NovAi Foundation stack. Named after the "Butler Pattern," it serves as a silent, efficient, and self-healing administrator that ensures the underlying hardware (AMD Ryzen 5700U) and OS resources are perfectly harmonized with the AI's cognitive demands.

In the Xoe-NovAi ecosystem, The Butler is responsible for **Zero-Configuration Acceleration**, **Resource Shielding**, and **Sovereignty Auditing**.

---

## 🏗️ Architecture: The Modular Butler

The Butler is designed as a **Plugin-First Infrastructure Module**. It resides in `scripts/infra/` and `configs/quadlets/`, decoupled from the core AI logic to ensure portability and ease of open-source adaptation.

### 1. The Butler CLI (`butler_tui.sh`)
The command-line interface for the human director and AI team to interact with the host system.
- **Tasks**: Lifecycle management, MTU alignment, Ryzen core steering, and health diagnostics.

### 2. The Core Steer Engine (taskset)
The "Ryzen Guard". It manages CPU affinity to ensure LLM inference has dedicated resources while background tasks are masked to efficiency cores.

### 3. The Resource Shield (Cgroup V2 / ZRAM)
Protects the AI from host-level instability.
- **ZRAM Guard**: Monitors compressed swap to prevent OOM on 8GB systems.
- **Core Masking**: Pins background tasks to efficiency threads (12-15), reserving the high-performance threads (0-11) for AI workloads.

---

## 🛡️ Harmony Guards

The Butler maintains the "Ma'at Balance" of the system through three automated guards:

| Guard | Responsibility | Implementation |
|-------|----------------|----------------|
| **Core Guard** | LLM Performance | Pins AI tasks to threads 0-11 via `taskset`. |
| **Memory Guard** | OOM Prevention | Enforces the 400MB soft-stop rule and monitors ZRAM. |
| **Network Guard** | Sovereignty | Aligns MTU to 1500 and optimizes `pasta` drivers. |

---

## 🗺️ The Butler Roadmap

### Phase 1: Sovereign Foundation (CURRENT)
- [x] **Unified Butler CLI**: Centralized `scripts/infra/butler.sh`.
- [x] **Hardened Foundation**: MTU 1500 + Ryzen Core Alignment.
- [x] **TUI Prototype**: Interactive `butler_tui.sh` using `gum`.
- [x] **Path Normalization**: Full portability using `${PROJECT_ROOT}`.

### Phase 2: Cognitive Infrastructure
- [ ] **Sovereign Health Bridge**: Auto-generating `data/infra_status.json` for Chainlit UI.
- [ ] **Self-Healing Diagnostics**: Butler automatically detects and resets `pasta` networking.
- [ ] **Dynamic Load Steering**: Automatically re-pining threads based on real-time CPU thermal data.

### Phase 3: Sovereign Evolution (DEFERRED)
- [ ] **Aptly Integration**: Transition from caching to full repository mirroring.
- [ ] **Local Proxy Re-evaluation**: Re-assessing `apt-cacher-ng` for multi-node deployments.
- [ ] **Air-Gap Protocol**: "USB Sneakernet" automated import/export scripts.

### Phase 4: Open Source Release
- [ ] **Standalone Installer**: One-command setup for external adaptation.
- [ ] **Butler-as-a-Service**: REST API for multi-agent infrastructure control.

---

## 🌐 Open Source Adaptability
The Butler is designed to be **clonable**. By maintaining its configuration in `lib/sovereign-proxy/`, other developers can adapt our hardening rules for their own Ryzen-based AI projects, creating a standard for "Elite Local AI Infrastructure."

---
*Documented by Gemini CLI (Lead Architect)*
