# 🔱 Xoe-NovAi Component Registry: Core vs. Supplemental

This document serves as the authoritative map of the Xoe-NovAi ecosystem. It distinguishes between the core stack features and the supplemental tools provided for developer efficiency.

---

## 🏗️ 1. Core Stack Features
These components are integral to the Xoe-NovAi mission and are fully integrated into the containerized stack.

### 🤵 The Butler (`scripts/infra/butler.sh`)
- **Status**: **CORE / INTEGRATED** (with Independent Ambitions).
- **Role**: Infrastructure orchestrator, Ryzen core-steering, and build manager.
- **Dual-Purpose**: Architected to be eventually packaged as a standalone tool for other stacks.

### 🧠 Expert Knowledge System (`expert-knowledge/`)
- **Status**: **CORE / INTEGRATED** (Cross-Agent Memory).
- **Role**: The "Long-Term Memory" of the stack. Stores technical mastery, standards, and best practices.
- **Dual-Purpose**: Structured specifically to be consumable by ANY AI assistant (Gemini CLI, Cline, Grok, internal models) even outside the Xoe-NovAi Foundation stack.

### 🔍 RAG Engine (FastAPI + FAISS)
- **Status**: **CORE**.
- **Role**: Hybrid retrieval (Semantic + Lexical) using the RRF standard.

### 🗣️ Voice & UI (Piper, Whisper, Chainlit)
- **Status**: **CORE**.
- **Role**: The accessible, voice-first interaction layer.

---

## 🤖 2. Supplemental & Complementary Tooling
These tools are "Added Bonuses" included in the repository to enhance the development environment. They are NOT required for the stack to function but are highly recommended.

### 🎭 Gemini CLI Specialist Agents (`.gemini/agents/`)
- **Status**: **SUPPLEMENTAL / COMPLEMENTARY**.
- **Agents**: `stack-researcher`, `qa-specialist`, `turn-auditor`.
- **Role**: Project-specific AI personas for autonomous research and stabilization.

### 📂 Model Context Protocol (MCP) Servers
- **Status**: **SUPPLEMENTAL / COMPLEMENTARY**.
- **Role**: Standards-based tool integration for agents (e.g., local filesystem access).

---

## 📈 3. Architecture Philosophy
Xoe-NovAi is built on the **Sovereign Entity Pattern**. 
1. **Offline-First**: Every core and supplemental tool must function without external API dependencies.
2. **Standardization**: Use `uv` for packages, `Markdown/YAML` for knowledge, and `BuildKit` for speed.
3. **Intelligence Density**: Maximize the output of every turn through specialized knowledge retrieval.
