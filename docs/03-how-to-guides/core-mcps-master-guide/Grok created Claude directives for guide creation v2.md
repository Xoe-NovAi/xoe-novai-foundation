# XNAi Foundation Stack: MCP Integration Directives (v2.0)

```yaml
---
title: XNAi Foundation MCP Integration Manual - Enterprise Implementation Guide
version: 2.0 (January 27, 2026)
authors: Claude Sonnet (Generated), Grok (Research Input), Gemini CLI (Technical Audit)
audience: XNAi Team (The User/Architect, Cline, Grok, Gemini CLI)
purpose: Complete, sovereign deployment of Community Filesystem, Git, and Podman MCP servers.
constraints:
  - sovereignty: local-first, zero-telemetry, offline-capable
  - performance: <300MB RAM/server, <100ms latency
  - security: Ma'at-ethical filters, rootless Podman (UID=0 cache standard), HITL mandatory
  - compatibility: Torch-free capable, Ryzen 5700U baseline
dependencies:
  - podman: 5.x rootless (requires `podman system service` for socket access)
  - python: 3.12 with uv 0.5.21
  - docker-compose: Podman-compatible
structure: diataxis  # Tutorials, How-Tos, Explanations, References
output_format: markdown-pdf-ready
---
```

## Executive Directive
Claude, you are tasked with generating the definitive **XNAi Foundation Stack MCP Integration Manual**. Use the provided supplemental files in your Project Knowledge Base to ensure 100% alignment with our Ryzen-tuned, Ma'at-governed architecture.

### 1. Tutorials (Step-by-Step)
- **Core MCP Setup**: End-to-end deployment of community servers (Filesystem, Git, Podman).
- **Socket Activation**: Enabling `podman system service` and `DOCKER_HOST` for rootless socket communication.
- **Cache Hardening**: Implementing the `uid=0,gid=0` BuildKit standard for `uv` hardlink compatibility.

### 2. How-Tos (Task-Specific)
- **Filesystem MCP**: Bind-mounting `/memory_bank` as Read-Only; implementing `search_expert_knowledge` with RRF support.
- **Git MCP**: Hardening against 2026 prompt-injection; enforcing HITL (Human-in-the-loop) for all commits.
- **Podman MCP**: Monitoring stack health via the rootless socket.

### 3. Explanations (Deep Dives)
- **The Ma'at Guardrail**: How the 7 Cardinal Virtues (Sovereignty, Sincerity, Harmony, Balance, Purity, Trust, Compassion) govern tool usage.
- **Confused Deputy Mitigations**: Implementing JWT-based auth and HITL gates to prevent AI-driven unauthorized access.

### 4. References
- **Standardized Dockerfile Snippets**: Using `Dockerfile.base` inheritance and `xnai-uv` cache IDs.
- **Ma'at Filter Scripts**: Logic for validating tool calls against the 42 Ideals.

## Recommended Knowledge Base Files
1. `memory_bank/teamProtocols.md` (Relay Protocol & HITL)
2. `memory_bank/activeContext.md` (Current build status)
3. `memory_bank/maatDistilled.md` (7 Cardinal Virtues)
4. `memory_bank/systemPatterns.md` (Ryzen tuning & AnyIO)
5. `expert-knowledge/environment/buildkit_cache_hardlining.md` (The uid=0 standard)
6. `memory_bank/cline.md` (Formerly forge.md)
7. `memory_bank/mcpConfiguration.md` (Community MCP Strategy)