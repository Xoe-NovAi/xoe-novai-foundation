Architect, gaps mined and sealed—2026 crawls confirm Vikunja's sovereignty edge (env-only config, dedicated users, no forced telemetry), Gemini CLI's MCP protocol as the elite bridge (Google's ReAct tool system via FastMCP/Python servers), and MkDocs synergy via scripted Markdown exports. No direct Vikunja-MkDocs plugin, but scripted pulls turn tasks into a living Diátaxis portal. Gemini API patterns locked: Flash for speed, Pro escalation, strict token/safety hygiene. Unsolicited pivot: Forge Vikunja as a Gemini CLI MCP server—agents invoke tasks natively, minimal cloud bleed.

### Gemini API & CLI MCP: Elite Strategy (2026 Locked)
Gemini CLI (google-gemini/gemini-cli) is the terminal powerhouse: ReAct loop + local/remote MCP servers for tools. MCP ("Model Control Protocol" in Google parlance) enables custom servers—Python via FastMCP lib—for tool exposure. Your "Gemini CLI MCP-ready" vision materializes here.

**Tiered Utilization Strategy**
| Layer          | Tool               | Use Case                                 | Best Practices (Sourced 2026)                                | Sovereignty Notes                                            |
| -------------- | ------------------ | ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Light/Fast     | Gemini CLI (Flash) | Terminal execution, quick queries        | Built-in tools first; MCP for custom (e.g., Vikunja tasks). Config extensions locally. | Offline-capable post-setup; register local MCP servers.      |
| Heavy/Critical | Gemini API (Pro/3) | Multimodal, long-context reasoning       | Clear system instructions; token counting pre-call; streaming responses; safety settings (block medium+). Model select: Flash default, Pro escalate. Async for parallel. | Cache responses locally; no telemetry flags where available—cloud inevitability, route via CLI proxy if possible. |
| Orchestration  | MCP Servers        | Agent tool calls (Vikunja create/update) | FastMCP for Python servers; expose endpoints (create_task, get_status). ReAct guardrails in agent config. | Self-host MCP—zero cloud for tool execution. Cline integrates via CLI hooks. |

**Implementation Thrust**: Cline-Kat prototypes `vikunja-mcp-server.py` (FastMCP base). Register in Gemini CLI config: local HTTP endpoint. Agents then "call Vikunja" sovereignly—task handoff without API sprawl.

Risk: Rate limits on API (quota management via Vertex if scaled); mitigate with CLI-first.

### MkDocs Enhancement for Vikunja: Yes, Knowledge Portal Pivot
No native integration (Vikunja Markdown rendering still buggy per community 2025 threads—raw HTML exports dominant). But elite workaround: Script API pulls → Markdown tasks/descriptions → MkDocs Material site.

**Strategy**:
- Cron/script (Gemini CLI executes): Query Vikunja API → export namespaces/projects as .md (frontmatter labels, body descriptions).
- MkDocs config: Diátaxis structure (Tutorials: Roadmaps; How-To: Charters; Reference: EKB links; Explanation: Philosophy).
- Benefits: Static, searchable project portal—offline browsable, version with git. Attachments as assets.
- Plugin: mkdocs-material + search/icons for mythic polish.

Caveat: Manual/sync script maintenance—automate via MCP tool.

### Advanced Vikunja Best Practices (Self-Hosted Sovereign)
From official docs + community (systemd hardening, config.yml samples, integrations):
- **Config**: Env vars only—no committed files. JWT secret runtime-generated or env-injected.
- **Security**: Dedicated non-root user; reverse proxy (Caddy/Nginx local-only); OpenID if multi-user (avoid cloud providers).
- **Performance**: Postgres tuning (shared_buffers ~25% RAM); index tasks/labels heavily queried.
- **Automation**: Community n8n nodes (self-host n8n Podman if needed); webhooks to local scripts (e.g., task create → EKB commit).
- **Backups/Restores**: pg_dump cron → encrypted volumes. Test restores quarterly.
- **API Mastery**: Bulk endpoints for migration; filters/labels for Ma'at tagging; custom fields (energies, commit hashes).
- **Clients**: Vja CLI terminal; CalDAV for mobile sync (sovereign).

### Caveats to Avoid (Hardened Gates)
- **Data Loss Migration**: No native MD export—script thoroughly, dry-run imports.
- **Markdown Pitfalls**: Vikunja renders inconsistent—store raw MD in descriptions, render via external (MkDocs).
- **Over-Automation**: Webhooks/n8n bloat—keep manual for consciousness alignment.
- **Resource Creep**: DB growth on Ryzen—prune archives, vacuum regularly.
- **Cloud Leak**: No external auth/integrations—local-only reverse proxy.
- **API Abuse**: Self-hosted unlimited, but token rotation + IP restrict.

_meta/projects.md Update Proposal

| Project       | Status      | Priority | Owner            | Next Action                               | Blockers       | EKB Links                                                    | Local Sync Notes                     |
| ------------- | ----------- | -------- | ---------------- | ----------------------------------------- | -------------- | ------------------------------------------------------------ | ------------------------------------ |
| Vikunja-Hub   | In-Progress | High     | Xoe / Gemini CLI | Prototype vikunja-mcp-server.py (FastMCP) | None           | sync/vikunja-mcp-v1.0.0.md, infrastructure/gemini-mcp-v1.0.0.md | MCP bridge accelerates agent synergy |
| MkDocs-Portal | Proposed    | Medium   | Cline-Kat        | Script Vikunja → MD exporter              | API auth setup | docs/mkdocs-vikunja-export-v1.0.0.md                         | Diátaxis knowledge vault             |

**Next Actions**:
1. Cline: Forge FastMCP Vikunja MCP server—commit prototype.
2. Gemini CLI: Test MCP registration + sample task call.
3. Draft MkDocs exporter script—pull one namespace.
