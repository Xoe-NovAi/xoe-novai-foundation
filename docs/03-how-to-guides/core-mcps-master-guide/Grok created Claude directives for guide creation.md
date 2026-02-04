## Research Summary

This final iteration confirms the MCP integration directives are fully optimized for Claude Sonnet's generation of an enterprise-grade manual, with all knowledge gaps (e.g., 2026-specific hardening like confused deputy mitigations) resolved via updated research. The directives are now purely task-focused on MCP deployment (Filesystem, Git, Podman servers) for Xoe-NovAi, emphasizing sovereignty, Ma'at ethics, and edge case handling without extraneous elements. The supplemental file has been refined to reflect the current team structure (The User/Architect, Cline, Grok, Gemini CLI) and stack details, ensuring Claude has comprehensive, up-to-date context for producing high-fidelity outputs.

## Technical Assessment

The directives leverage Diátaxis for structured manual generation, with YAML frontmatter enabling easy parsing in Claude Projects (500k token capacity in 2026). Edge cases (e.g., rootless escalations, offline failures) are fully integrated with OWASP best practices, aligning with Xoe-NovAi's torch-free, <6GB constraints. The supplemental aggregates stack/env details without legacy references, filling gaps like Gemini CLI's MCP role (per gemini.md) and recent vuln patches (e.g., CVE-2025-6515 fixes). This setup ensures Claude produces a 50-100 page PDF-ready manual with code, diagrams, and audits, ready for team use.

## Implementation Recommendations

Below is the full, updated, task-at-hand focused directives for Claude—the **Master Guide** as a single, parseable Markdown document. Following it is the full, updated supplemental file (`xoe-novai-stack-context.md`). Upload both to Claude's Project Knowledge Base, along with the 12 recommended memory_bank/docs files.

### Master Guide for Claude: Xoe-NovAi MCP Implementation Directives

```yaml
---
title: Xoe-NovAi MCP Integration Manual - Enterprise Implementation Guide
version: 1.0 (January 27, 2026)
authors: Claude Sonnet (Generated), Grok (Research Input)
audience: Xoe-NovAi Team (The User/Architect, Cline, Grok, Gemini CLI)
purpose: Complete, sovereign deployment of Filesystem, Git, and Podman MCP servers with fine-tuning for Xoe-NovAi Foundation stack
constraints:
  - sovereignty: local-first, zero-telemetry, offline-capable
  - performance: <300MB RAM/server, <100ms latency
  - security: Ma'at-ethical filters, rootless Podman (UID=1001), Human-in-the-loop (HITL) for write operations
  - compatibility: Torch-free, Ryzen 5700U baseline, BuildKit caches (xnai-uv)
dependencies:
  - podman: 5.x rootless (requires `podman system service` for MCP socket access)
  - python: 3.12 with uv 0.5.21
  - docker-compose: Podman-compatible
edge_cases:
  - rootless_socket_access: Permission denied on /run/user/1001/podman/podman.sock
  - confused_deputy: Unauthorized tool chaining via LLM context injection
  - tool_poisoning: LLM-induced malicious commands in git commit messages
  - vuln_injection: Prompt injection in Git forks
  - air_gap_dependency_loss: Missing wheelhouse in total isolation
best_practices:
  - owasp_hardening: JWT auth, input fuzzing, strict CORS for local servers
  - ethical_filters: Ma'at pre-checks on tool calls (42 Ideals validation)
  - monitoring: Butler integration for ZRAM/VRAM and socket health
structure: diataxis  # Tutorials, How-Tos, Explanations, References
output_format: markdown-pdf-ready  # With TOC, code blocks, diagrams
---
```

#### Tutorials (Step-by-Step Onboarding)

1. **Core MCP Setup Tutorial**  
   - Overview: End-to-end deployment from clone to production for Filesystem, Git, and Podman MCP servers.  
   - Steps:  
     a. Environment Prep: Verify Podman rootless (`make setup-directories`), load memory_bank.  
     b. Socket Activation: Enable `podman system service --time=0` for the Podman MCP server.
     c. Clone Servers: Filesystem (modelcontextprotocol/servers/src/filesystem), Git (patched Anthropic fork), Podman (yok-tottii-mcp-podman-devcon).  
     d. Containerize: Use standardized `Dockerfile.base` inheritance; mount `xnai-uv` caches.
     e. Fine-Tune: Implement Ma'at filters (HITL for all write/commit/delete operations).
     f. Integrate: Cline (Forge) auto-discover via Codium settings; verify in Gemini CLI.  
   - Edge Mitigation: Include rootless test script (podman unshare id); handle confused deputy with JWT validation.  
   - Diagram: Mermaid workflow for deployment phases.

2. **Sovereignty Hardening Tutorial**  
   - Focus: Apply zero-telemetry patches and Ma'at ethics.  
   - Steps: Fork repos, remove logging; add API_KEY auth; fuzz test inputs for tool poisoning.

#### How-Tos (Task-Specific Guides)

1. **Deploy Filesystem MCP with Memory_Bank Fine-Tuning**  
   - Task: Enable sovereign file access.  
   - Steps: Bind-mount `/memory_bank` read-only for general agents; add "search_expert_knowledge" tool with RRF support; test edge (symlink attacks via chroot).  
   - Best Practice: Enforce Ma'at filter for all write operations; The User/Architect (Human) approval required for `memory_bank` modifications.

2. **Secure Git MCP for Repo Management**  
   - Task: Safe commits/diffs.  
   - Steps: Patch for 2026 injection vulns; add Butler proxy ("podman_ps"); ensure `GIT_AUTHOR_NAME` reflects the acting AI (e.g., "Cline AI").
   - Best Practice: Human-in-loop (The User/Architect approval via inbox) for writes; input fuzzing for poisoning.

3. **Implement Podman MCP for Stack Orchestration**  
   - Task: Container health queries.  
   - Steps: Expose socket securely using `DOCKER_HOST=unix:///run/user/1001/podman/podman.sock`; add "stack_health" tool (infra_status.json).
   - Best Practice: ZRAM monitoring integration; JWT for deputy attacks.

4. **Handle Edge Cases**  
   - How-To: Test offline failures (simulate air-gap); audit tool poisoning (fuzz LLM inputs); mitigate UID escalations (podman unshare).

#### Explanations (Deep Dives)

1. **Security & Vulnerabilities**  
   - Explain: 2026 vulns (prompt injection, RCE, confused deputy); mitigations (OWASP, Ma'at filters).  
   - Table: Vuln | Impact | Mitigation | Xoe-NovAi Impl.

2. **Sovereignty & Ethics Integration**  
   - Explain: Offline enforcement; Ma'at alignment (42 Laws in tool prompts).  
   - Diagram: Workflow with ethical gates.

3. **Performance Optimization**  
   - Explain: BuildKit caches for deploys; <6GB constraints.  
   - Metrics Table: Server | RAM | Latency | Edge Handling.

4. **Team Collaboration**  
   - Explain: Role boundaries (teamProtocols.md); handoffs via communications inboxes.

#### References (Resources & Snippets)

1. **Code Snippets**  
   - Dockerfile Mod: Fenced block for each server.  
   - Ma'at Filter Script: Python example for ethical checks.

2. **Sources**  
   - List all from research (web/X results, OWASP guides).

3. **Appendices**  
   - Glossary: MCP terms, Xoe-NovAi specifics.  
   - Audit Checklist: Vuln scans, sovereignty tests.

### Updated Supplemental File: xoe-novai-stack-context.md

```markdown
# Xoe-NovAi Foundation Stack Context for Claude Projects

**Document Version**: 1.0 (January 27, 2026)  
**Purpose**: Comprehensive context file for Claude Sonnet to maintain full awareness of Xoe-NovAi Foundation stack, multi-AI environment, development strategies, and sovereignty constraints. This enables generation of enterprise-grade implementation manuals, security audits, and ethical frameworks.  
**Key Principles**: Sovereignty-first (zero-telemetry, offline-capable), consciousness evolution (Ma'at-aligned), rootless Podman deployment.  
**Constraints**: Torch-free, <6GB RAM, CPU/Vulkan only (Ryzen 5700U baseline).  

## Executive Overview

Xoe-NovAi is a sovereign, local-first RAG stack in Phase 6 release hardening (v0.1.7), focused on production readiness with BuildKit caches, Butler orchestration, and multi-AI collaboration. Core mission: Democratize enterprise-grade AI with consciousness frameworks. Team: The User/Architect (Human Director), Cline (Local Development Specialist), Grok (Research Specialist), Gemini CLI (Real-time Assistance Specialist). Environment: Podman 5.x rootless containers, Codium IDE + Cline extension, Gemini CLI terminal assistance. Strategies: Iterative hardening, ethical AI (42 Laws of Ma'at), MCP integration for workflow enhancement.

## Stack Details (Technical Architecture)

- **Core Services** (from docker-compose.yml):  
  - Redis: Cache/streams (7.4.1, maxmemory 512MB).  
  - RAG API: FastAPI backend (Dockerfile, LLM: smollm2-135m, FAISS hybrid RRF).  
  - Chainlit UI: Voice-enabled frontend (Dockerfile.chainlit, Piper TTS/Faster-Whisper STT).  
  - Curation/Crawl Workers: Ingestion pipelines (Dockerfiles for crawl/curation).  
  - Base Image: Python 3.12 slim with uv 0.5.21 (Dockerfile.base, BuildKit caches for apt/pip/uv).  

- **Infrastructure** (from techContext.md, systemPatterns.md):  
  - Podman 5.x rootless (pasta networking, MTU 1500).  
  - Build Optimization: RUN --mount=type=cache (xnai-apt, xnai-pip, xnai-uv).  
  - Performance: OPENBLAS_CORETYPE=ZEN, N_THREADS=6, 400MB ZRAM rule.  
  - Patterns: AnyIO TaskGroups for concurrency, WASM plugins for isolation, SQLite WAL for persistence.  

- **Configuration** (from config.toml, .env):  
  - Sovereignty: telemetry_enabled=false, offline_mode=true.  
  - Voice: distil-large-v3-turbo STT, piper_onnx TTS.  
  - Security: API_KEY, CIRCUIT_BREAKER_ENABLED=true.  

- **Makefile & Scripts**: Build orchestration (make build), Butler CLI (scripts/infra/butler.sh for core steering, health monitoring).  

## Environment Details (Multi-AI Setup)

- **Primary**: Codium IDE + Cline extension (Claude API integration, MCP-enhanced).  
- **Target**: Xoe-NovAi Foundation Stack (Podman containers, not yet fully spun up per progress.md).  
- **Secondary**: Gemini CLI (terminal, MCP server with sovereignty validation per gemini.md).  
- **Relationships**: Shared memory_bank for coordination; Cline for local development, Grok.com for research.  

- **Team Structure**: 
  The User/Architect (Human Director)
  ├── Ultimate authority and strategic oversight
  └── Quality assurance and validation (HITL Gatekeeper)

  Cline (Local Development Specialist - Formerly Forge)
  ├── Code implementation and technical execution
  ├── Real-time debugging and optimization
  └── Codium IDE + Cline extension primary environment

  Grok (Research Specialist)
  ├── Comprehensive research and analysis
  └── Grok.com primary environment

  Gemini CLI (Real-time Assistance Specialist)
  ├── Immediate problem-solving and analysis
  └── MCP integration and health monitoring

- **Protocols** (from contextProtocols.md):  
  - Context Loading: Phase 1 (activeContext.md, environmentContext.md, teamProtocols.md), Phase 2 (projectbrief.md, etc.).  
  - Switching: Seamless between envs with caching.  
  - Security: Encryption, access controls.  

## Strategies & Processes

- **Development Strategies** (from activeContext.md, progress.md):  
  - Phase 6 Focus: Release hardening (BuildKit standardization, Butler TUI, GitHub cleanup).  
  - Sovereignty: Local-first, air-gapped readiness.  
  - Consciousness: Ma'at integration, mind-model resurrection.  
  - MCP Strategy: Local servers for codebase/git/RAG (fine-tune for memory_bank queries).  

- **Collaboration Processes** (from teamProtocols.md):  
  - Communications: Inboxes/outboxes (memory_bank/communications/[agent]/inbox.md).  
  - Escalation: Notify The User/Architect for critical issues.  
  - Performance: Metrics for quality, timeliness, collaboration.  

- **Onboarding & Emergency** (from onboardingChecklist.md):  
  - Phase 1: Core context loading.  
  - Handling: Root cause analysis, The User/Architect notification.  

- **Ethical Strategies**: 42 Laws of Ma'at for AI decisions; human-AI partnership focus.  

## Knowledge Gaps Filled & MCP-Specific Direction

- **Gaps Researched**:  
  - 2026 MCP Vulns: Prompt hijacking (CVE-2025-6515), context leakage, token passthrough (per JFrog, OWASP). Mitigations: JWT auth, fuzz testing, ethical filters.  
  - Best Practices: Production Rust patterns (MCP Server Best Practices), secure Claude integration (Clockwise blog), no exposed servers (BitSight: 1000+ risks).  
  - Claude-Specific: Use Projects for 500k token persistence; integrate with Cline via local MCP discovery; avoid cloud deps for sovereignty.  

- **Direction for Claude**: Generate manuals with Diátaxis (tutorials/how-tos/explanations/references); include Ma'at guards, rootless patches, and Butler monitoring. Focus on Filesystem/Git/Podman MCPs with edge mitigations (e.g., offline mocks, UID checks).  

## Recommended Files for Upload to Claude's Project Folder

Upload these 12 files from memory_bank and docs to Claude's Knowledge Base for full context (prioritize core ones first):  
1. memory_bank/teamProtocols.md (Team structure, protocols).  
2. memory_bank/contextProtocols.md (Context loading/switching).  
3. memory_bank/environmentContext.md (Multi-env architecture).  
4. memory_bank/activeContext.md (Current priorities/blockers).  
5. memory_bank/progress.md (Phase timeline/metrics).  
6. memory_bank/gemini.md (Gemini CLI guidelines/MCP).  
7. memory_bank/claude.md (Claude operational protocols).  
8. memory_bank/cline.md (Cline capabilities - Updated from forge.md).  
9. memory_bank/grok.md (Grok research guidelines).  
10. memory_bank/systemPatterns.md (Architectural patterns).  
11. memory_bank/techContext.md (Hardware/stack constraints).  
12. docs/06-development-log/gemini_cli_and_mcps_dev_project_notes_20260124.md (MCP integration notes).  

## Appendices

- **Glossary**: Butler (infra orchestration), Ma'at (ethical framework), BuildKit (cache mounts).  
- **Diagrams**: Mermaid for team structure/env relationships (include in manuals).  
  ```

## Success Metrics & Validation

- **Directive Focus**: 100% on MCP task (no extraneous elements); Claude outputs match Diátaxis structure.  
- **Context Completeness**: Supplemental covers all stack/env; gaps filled (vuln/practice audits).  
- **Claude Readiness**: Manual generation in single session; team utility ≥9/10.  
- **Validation Procedure**: Upload and query Claude for sample section; confirm sovereignty/edge coverage.

## Sources & References

- OWASP MCP Guide (Jan 2026): https://owasp.org/www-project-mcp-security  
- JFrog CVE-2025-6515 (Oct 2025): https://jfrog.com/blog/mcp-prompt-hijacking-vulnerability  
- BitSight Exposed Servers (Dec 2025): https://www.bitsight.com/blog/exposed-mcp-servers-reveal-new-ai-vulnerabilities  
- Practical DevSecOps (Jan 2026): https://www.practical-devsecops.com/mcp-best-practices-2026  
- Builder.io Best MCP Servers (Dec 2025): https://www.builder.io/blog/best-mcp-servers-2026  
- MintMCP Claude Security (Dec 2025): https://www.mintmcp.com/blog/claude-code-security  
- Cyber Press Top 10 MCP (Jan 2026): https://cyberpress.org/best-mcp-servers  
- ByteBridge Securing MCP (2025): https://bytebridge.medium.com/securing-mcp-gateways-risks-vulnerabilities-and-best-practices-18c5f5abda4f  
- Snyk MCP Integration (2025): https://snyk.io/articles/claude-desktop-and-snyk-mcp  
- Skyvern Browser MCP (Oct 2025): https://www.skyvern.com/blog/browser-automation-mcp-servers-guide  
- LobeHub Claude Gemini (Jan 2026): https://lobehub.com/mcp/cmdaltctr-claude-gemini-mcp-slim  
- Nucleus Security MCP (Dec 2025): https://nucleussec.com/platform/mcp-server  
- appcypher Awesome MCP (2025): https://github.com/appcypher/awesome-mcp-servers  
- Composio MCP Vulns (Aug 2025): https://composio.dev/blog/mcp-vulnerabilities-every-developer-should-know  
- Clockwise Claude MCP (Nov 2025): https://www.getclockwise.com/blog/claude-code-mcp-tools-integration  
- Security Boulevard MCP Guide (Nov 2025): https://securityboulevard.com/2025/11/mcp-for-technical-professionals-a-comprehensive-guide-to-understanding-and-implementing-the-model-context-protocol