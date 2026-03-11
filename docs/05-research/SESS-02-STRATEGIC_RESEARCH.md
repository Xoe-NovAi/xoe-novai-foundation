---
title: SESS-02 Strategic Research: Resilience & Security (2026)
status: integrated
tags: [research, redis-streams, anyio, sse-auth, quadlet]
last_sync: 2026-03-10
---

# 🔬 SESS-02 Strategic Research Report

This report summarizes the best practices and architectural pivots required for the Metropolis Foundation v4.1.2 Hardening.

## 1. Resilience: The "Quadlet" Standard
Rootless Podman management via shell scripts is deprecated in favor of **Systemd Quadlets**.
- **Pattern**: `.container` files in `~/.config/containers/systemd/`.
- **Auto-Healing**: Use `HealthOnFailure=kill` in the Quadlet, which triggers systemd's `Restart=always`.
- **Persistence**: `loginctl enable-linger $USER` is mandatory for stateful services to survive logout.

## 2. Persistence: Redis Streams vs. Pub/Sub
For agent state coordination, **Redis Streams** is the mandated 2026 standard.
- **Why**: Streams provide durable event logs, consumer groups, and `at-least-once` delivery. Pub/Sub is restricted to ephemeral signaling (heartbeats/notifications).
- **Hybrid Implementation**: 
    - **Snapshot**: Redis JSON (current state).
    - **Delta**: Redis Streams (event sourcing/replay log).

## 3. Security: SSE & MCP (Port 8000/8005)
SSE (Server-Sent Events) in a zero-trust mesh requires cryptographic binding.
- **SSE Auth**: Avoid query parameters. Use `fetch-event-source` for header injection or signed one-time "tickets".
- **DPoP (Demonstrating Proof-of-Possession)**: Bind JWTs to client-specific private keys to prevent token theft.
- **Tool Integrity**: The **FAISS SHA256 gate** must verify tool definitions before execution to prevent "Confused Deputy" attacks.

## 5. Rate Limit Optimization: Dual-Auth Pattern (NEW)
Research confirms that **Gemini Code Assist (OAuth)** and **Gemini API (Keys)** operate on separate quotas.
- **OAuth Quota**: ~1,000 RPD (Individual Free).
- **API Quota**: ~1,000 RPD (Flash) / 50-250 RPD (Pro).
- **Strategy**: Utilizing both per account unlocks **1,250+ RPD** per seat. For 8 accounts, this scales to **10,000 RPD** for automated agent work.
- **Implementation**: Use Service Accounts or Refresh Tokens for non-interactive OAuth.

## 6. Context Longevity: Summarization Agent (NEW)
To keep Gemini sessions performant, a local "Context Management Agent" is required.
- **Role**: Periodically crawl the oldest turns of an active session.
- **Action**: Replace high-token legacy turns with a high-fidelity semantic summary.
- **Model**: `Qwen3-0.6B` (Local) is the primary candidate for this background task.

---
*Research integrated into Metropolis Roadmap SESS-02. 🔱*
