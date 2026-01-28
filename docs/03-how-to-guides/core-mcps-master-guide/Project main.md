```yaml
---
title: Xoe-NovAi MCP Integration Manual - Enterprise Implementation Guide
version: 1.1 (January 27, 2026)
authors: Claude Sonnet (Generated), Grok (Research Input)
audience: Xoe-NovAi Team (The User/Architect, Cline, Grok, Gemini CLI)
purpose: Complete, sovereign deployment of Filesystem, Git, and Podman MCP servers with fine-tuning for Xoe-NovAi Foundation stack
constraints:
  - sovereignty: local-first, zero-telemetry, offline-capable
  - performance: <300MB RAM/server, <100ms latency
  - security: Ma'at-ethical filters, rootless Podman (UID=1001), HITL for destructive ops
  - compatibility: Torch-free, Ryzen 5700U baseline, BuildKit caches (xnai-uv ID)
dependencies:
  - podman: 5.x rootless
  - python: 3.12 with uv 0.5.21
  - mcp-sdk: pinned to 2026.01.15-stable
  - docker-compose: Podman-compatible
edge_cases:
  - rootless_escalation: UID mismatches/capability drops
  - offline_failure: Path traversal in air-gapped (chroot binds)
  - tool_poisoning: LLM-induced malicious commands (fuzz testing)
  - vuln_injection: Prompt injection in Git forks
  - confused_deputy: Token passthrough (JWT mandatory)
best_practices:
  - owasp_hardening: JWT auth, input fuzzing, version pinning
  - ethical_filters: Ma'at pre-checks + HITL (The User/Architect approval) on tool calls
  - monitoring: Butler integration for ZRAM/VRAM
  - podman_socket: system service + DOCKER_HOST
structure: diataxis  # Tutorials, How-Tos, Explanations, References
output_format: markdown-pdf-ready  # With TOC, code blocks, diagrams
---
```

#### Tutorials (Step-by-Step Onboarding)

1. **Core MCP Setup Tutorial**  
   - Overview: End-to-end deployment from clone to production for Filesystem, Git, and Podman MCP servers (pin mcp-sdk==2026.01.15-stable).  
   - Steps:  
     a. Environment Prep: Verify Podman rootless (make setup-permissions; podman system service for socket); load memory_bank (per contextProtocols.md).  
     b. Clone Servers: Filesystem (modelcontextprotocol/servers/src/filesystem), Git (patched Anthropic fork), Podman (yok-tottii-mcp-podman-devcon).  
     c. Containerize: Extend Dockerfile.base with --mount=type=cache,id=xnai-uv; add services to docker-compose.yml (localhost ports 8003-8005; DOCKER_HOST=unix:///run/user/1001/podman/podman.sock).  
     d. Fine-Tune: Add Ma'at filters + HITL gates (The User/Architect manual approval for write/commit/delete); enforce offline (ENV OFFLINE_MODE=true); JWT auth for confused deputy.  
     e. Integrate: Cline auto-discover; test in Gemini CLI.  
   - Edge Mitigation: Rootless test (podman unshare id); fuzz inputs for poisoning; chroot for offline traversal.  
   - Diagram: Mermaid workflow for deployment phases.

2. **Sovereignty Hardening Tutorial**  
   - Focus: Apply zero-telemetry patches, Ma'at ethics, and HITL.  
   - Steps: Fork repos, remove logging; add JWT/API_KEY auth; fuzz test inputs; implement The User/Architect HITL for destructive ops.

#### How-Tos (Task-Specific Guides)

1. **Deploy Filesystem MCP with Memory_Bank Fine-Tuning**  
   - Task: Enable sovereign file access with RRF hybrid search.  
   - Steps: Bind-mount /memory_bank read-only; add "search_expert_knowledge" tool (wikilinks + RRF support); test edge (symlink attacks via chroot).  
   - Best Practice: Rate limit calls; Ma'at filter + HITL for writes.

2. **Secure Git MCP for Repo Management**  
   - Task: Safe commits/diffs with Butler proxy.  
   - Steps: Patch for 2026 injection vulns; add "podman_ps" tool; edge: Offline mock for remote ops.  
   - Best Practice: HITL (The User/Architect approval) for commits; JWT for deputy attacks; input fuzzing.

3. **Implement Podman MCP for Stack Orchestration**  
   - Task: Container health queries via socket.  
   - Steps: Activate podman system service; set DOCKER_HOST; add "stack_health" tool (infra_status.json); edge: Socket escapes via capability drops.  
   - Best Practice: ZRAM monitoring; JWT + HITL for control ops.

4. **Handle Edge Cases**  
   - How-To: Test offline failures (air-gap sim); audit poisoning (fuzz LLM); mitigate escalation (UID checks); version pin rollback.

#### Explanations (Deep Dives)

1. **Security & Vulnerabilities**  
   - Explain: 2026 vulns (prompt injection, RCE, confused deputy); mitigations (JWT, fuzz, HITL).  
   - Table: Vuln | Impact | Mitigation | Xoe-NovAi Impl.

2. **Sovereignty & Ethics Integration**  
   - Explain: Offline enforcement; Ma'at + HITL alignment.  
   - Diagram: Workflow with ethical/HITL gates.

3. **Performance Optimization**  
   - Explain: xnai-uv BuildKit caches; <6GB constraints.  
   - Metrics Table: Server | RAM | Latency | Edge Handling.

4. **Team Collaboration**  
   - Explain: Role boundaries (teamProtocols.md); manual escalations for HITL.

#### References (Resources & Snippets)

1. **Code Snippets**  
   - Dockerfile Mod: Fenced block with xnai-uv cache for each server.  
   - Ma'at/HITL Filter Script: Python with JWT validation.  
   - Podman Socket Config: DOCKER_HOST example.

2. **Sources**  
   - List all from research (web/X results, OWASP guides).

3. **Appendices**  
   - Glossary: MCP terms, Xoe-NovAi specifics.  
   - Audit Checklist: Vuln scans, sovereignty tests, version pinning.
