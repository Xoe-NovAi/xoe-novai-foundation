# 🏙️ Community Guide: Building Your Own AI Metropolis
**Subtitle**: From Non-Programmer to Sovereign System Architect

---

## 🌌 Introduction
The **Omega Metropolis** is a local-first, sovereign AI network that runs 8 isolated "Domain Experts" on a single mid-grade machine (Ryzen 5700U). This guide explains how to build it using only free AI tools and the power of the Omega Stack.

## 🚀 The Architecture
The "Metropolis" works by utilizing **Environmental Isolation**. Instead of one AI seeing everything, we create 8 distinct "districts":
1.  **Architect**: System design and blueprinting.
2.  **API**: Backend development and Redis streams.
3.  **UI**: Frontend, dashboard, and UX.
4.  **Voice**: Audio processing and STT/TTS.
5.  **Data**: RAG, Qdrant, and Postgres.
6.  **Ops**: Infrastructure, Podman, and Caddy.
7.  **Research**: Knowledge mining and ingestion.
8.  **Test**: QA, coverage, and validation.

## 🛠️ Step-by-Step Setup

### 1. The Dispatcher (The "Subway System")
We use a custom bash script (`xnai-gemini-dispatcher.sh`) to route your commands. When you type `gemini --arch`, the stack automatically switches the "district" (folder) and API key.

### 2. High-Fidelity Monitoring
Run `make dashboard` to see your Metropolis alive. It tracks:
*   **Total Tokens**: Real-time throughput.
*   **Message Counts**: Managing your 50-message limits.
*   **Quota Status**: Automated rotation warnings.

### 3. Knowledge Harvesting (The "Library")
Your experts aren't just isolated; they share a soul. The **Knowledge Harvester** script takes conversations from one expert and indexes them into the **Gnosis Engine** (local RAG). This means the API expert can recall a decision made by the Architect yesterday.

### 4. Regional Bypass (The "Embassy")
Facing regional blocks for API keys? We integrated `ProxyChains` so you can retrieve your keys through a secure tunnel without compromising the rest of the local-first stack.

## 📜 The Non-Programmer Origin Story
"I began this entire project specifically to fill a gap I saw in the local AI community—an advanced local RAG system that offers total offline sovereignty on a mid-grade computer." 

By documenting the journey from non-coder to architect of an 8-domain expert network, we are proving that **intelligence has been democratized.**

---
**Keywords**: Local AI, RAG, Sovereign Tech, Gemini CLI, Multi-Account Rotation, AMD Ryzen Optimization.
