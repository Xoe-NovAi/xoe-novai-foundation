# Research: Multi-Agent Coordination Patterns

> **Date**: 2026-02-22
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: Research Task G-007

---

## 1. Overview

As the XNAi foundation moves toward a multi-agent architecture (Cline, Gemini, MC-Overseer), established coordination patterns are required to manage complexity, prevent race conditions, and ensure high-quality outputs.

## 2. Identified Coordination Patterns

### 2.1 The Supervisor (Centralized)
- **Role**: A "master" agent (like MC-Overseer) that decomposes high-level goals into sub-tasks.
- **Mechanism**: Assigns tasks to specialized agents (CLINE-1, CLINE-2, etc.), monitors progress, and synthesizes final results.
- **Best For**: Complex workflows requiring high consistency and quality control.

### 2.2 The Pipeline (Sequential)
- **Role**: Information flows linearly from one agent to the next.
- **Mechanism**: Agent A (Extractor) -> Agent B (Distiller) -> Agent C (Store).
- **Best For**: Knowledge absorption and data processing tasks.

### 2.3 The Swarm (Decentralized)
- **Role**: Agents act semi-autonomously based on their local state and a shared "Agent Bus."
- **Mechanism**: Agents "claim" tasks from a Redis stream (XNAi Agent Bus) based on their capabilities.
- **Best For**: High-throughput, parallel operations where tasks are loosely coupled.

### 2.4 The Blackboard (Shared Memory)
- **Role**: A shared state (Memory Bank) where all agents can read/write.
- **Mechanism**: Agents use lock files (`.lock`) and a "Coordination Key" (e.g., `ACTIVE-TASK-DISPATCH-2026-02-22`) to synchronize.
- **Best For**: Collaborative research and system-wide refactoring.

---

## 3. Best Practices for XNAi

1. **Clear Identity & Specialization**: Every agent must have a defined `Agent ID` and specialization (e.g., `CLINE-2: Security`).
2. **Explicit Handoffs**: Use the Agent Bus (`xnai:agent_bus`) to signal when a task is ready for the next agent.
3. **Atomic Memory Updates**: Rigorously follow the "Read before write" and "Lock file" protocol to prevent state corruption.
4. **Failure Recovery**: If an agent fails, the Supervisor (MC-Overseer) should detect the timeout and re-assign the task.
5. **Observability**: Log all agent actions to a centralized `transaction_logger.py` to enable audit trails.

---

## 4. Proposed Architecture: Hybrid Supervisor-Swarm
- **MC-Overseer** acts as the Supervisor, generating the `ACTIVE-TASK-DISPATCH`.
- **Specialized Agents** (Cline/Gemini) act as a Swarm, picking up tasks from the dispatch and communicating status via the Redis-based Agent Bus.

---

## 5. Next Steps
1. Formalize the `agent_orchestrator.py` logic.
2. Implement the Redis stream consumer groups for task distribution.
