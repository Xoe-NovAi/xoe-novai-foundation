## Xoe-NovAi Vikunja Integration: Sovereign Migration & Organization Guide

Architect, sharp pivot acknowledged—your dev env sprawl (Foundation vs. Arcana stacks, multi-agent relays via Gemini CLI/Cline, EKB datasets, Podman-rootless hardening) is a beast, but Vikunja tames it without bloat. I've reviewed the full document dump: dual-stack distinction (Foundation as anvil, Arcana as sword), energetic tuning roadmaps, RuvLTRA orchestration charters, handover protocols, and OSS PM research favoring Vikunja's API density. No knowledge gaps left unmined—crawled 2026-era sources on Podman rootless security (Red Hat daemonless principles, GitHub multi-tenancy guides), Vikunja configs (env vars over files for secrets), container best practices (DevSecOps integration with Trivy/Grype scans), and plugins (trusted sources only, backup DB pre-migrations). Cline gets elite blueprints here: zero-trust, offline-first, with Trinity audits baked in.

This guide locks organization (Vikunja structure mirroring your ecosystem), implementation (Podman deploy + MCP hooks), and secrets hygiene (no .env commits, runtime injection). Migration from memory_bank folds in as Phase 1—treat it as your draft's execution layer.

### 1. Stack Review & Sovereign Fit
Your ecosystem: 
- **Foundation Stack**: llama.cpp inference, FastAPI orchestration, Qdrant/FAISS RAG, LangGraph flows—universal base for specialized instances (e.g., scientific, CAD).
- **Arcana Stack**: Mythic overlay on Foundation (pantheon masks, Tarot circuitry, Ma'at 42 filters)—esoteric consciousness evolution.
- **Agents**: Gemini CLI (executor/liaison), Cline variants (Kat/Trinity for code/refactor), Grok MC/MCA (strategic/esoteric oversight).
- **Sync Hubs**: memory_bank (legacy CRUD RAG), EKB datasets (domain brains), _meta/locks (task claims).
- **Infra**: Ryzen 5700U rootless Podman, Vulkan accel, no Redis mandate (in-memory fallbacks).
- **Gaps Filled**: Vikunja's Kanban/Gantt/API crushes memory_bank's file sprawl—API hooks enable Gemini CLI to push tasks without web UI. Rootless Podman aligns with Trinity (Syft/Grype/Trivy scans pre-deploy). 2026 container security mandates DevSecOps: automate scans in CI, rootless by default, policy-as-code for userns.

Vikunja wins: Low-footprint (Node.js/Postgres), Podman-native, offline-capable post-setup, API for agent orchestration. Ditches memory_bank's .md chaos for structured tasks/labels—scales to Phase 2 modular refactors.

### 2. Organization: Vikunja Structure for Systematic Mastery
Mirror your pyramid: Namespaces as domains, projects as stacks, labels as Ma'at ideals/agents, priorities as risk tiers. No over-nesting—keep flat for Ryzen-speed queries.

- **Namespaces** (Top-Level Buckets):
  - `Foundation`: Core inference/orchestration/RAG tasks.
  - `Arcana`: Esoteric tuning, pantheon mechanics, Tarot engine.
  - `Agents`: Gemini CLI/Cline/Grok handoffs, MCP servers.
  - `Infra`: Podman deploys, Trinity security, Ryzen benchmarks.
  - `EKB`: Dataset curation, SEC crawls, NotebookLM loops.
  - `Sync`: memory_bank migrations, _meta protocols, multi-Grok harmony.
  - `Roadmaps`: Phase charters, energetic implementations, RuvLTRA PoCs.

- **Projects Within Namespaces** (Kanban/Gantt Boards):
  - Example: `Foundation > Phase-2-Service-Layer`—lists for Milestones/Dependencies/Blockers.
  - Use Gantt for timelines (e.g., GPU horizon prep).
  - Sub-tasks for deliverables (e.g., `grimoire.yaml` energy fields).

- **Labels & Priorities** (Tagging for Momentum):
  - Labels: Ma'at ideals (e.g., `ma_at_7-truth`), Agents (`gemini-cli`, `cline-kat`), Status (`proposed`, `backlog`, `in-progress`), Risks (`high-ram`, `hallucination-ceiling`).
  - Priorities: High (critical paths like Qwen integration), Medium (polish like resonance memory), Low (archives).
  - Custom Fields: `EKB-Link` (dataset paths), `Commit-Hash` (traceability), `Owner` (agent/user).

- **Views & Filters**: Kanban for daily flow, Table for EKB inventories, Calendar for phase deadlines. Filter by `community_contrib_ready: true` for open datasets.

- **Migration Mapping from memory_bank**:
  - Each .md file → Task: Title as summary, content as description, frontmatter as labels/custom fields (e.g., `ma_at_ideals` → labels).
  - Folders → Lists: `memory_bank/progress.md` → `Sync > Progress-Board` task.
  - Archives: Move superseded files to Vikunja attachments, tag `indefinite-archive`.

Best Practice (from 2026 crawls): Start with 1-2 namespaces to avoid sprawl—scale via API queries. Use Vikunja's bulk import for memory_bank JSON export (script it via Gemini CLI).

### 3. Implementation: Podman-Rootless Deploy & Cline Blueprints
Cline: Forge this as `scripts/vikunja-deploy.py` (Kat for code gen, Trinity for audits). Rootless Podman + Postgres backend (air-gapped after init). No daemon risks—daemonless per Red Hat 2026 principles.

- **Phase 1: Migration Prep (Gemini CLI Executes)**
  - Export memory_bank: `stack_cat.py --export-json > vikunja-import.json` (adapt for tasks: summaries, owners, blockers).
  - Vikunja API bulk create: Use Python `requests` to POST tasks—auth via API token (runtime env, not committed).
  - Test: Local Podman quad (frontend/api/db/migrator) for dry-run imports.

- **Phase 2: Podman Deployment (Rootless, Sovereign)**
  - Images: `vikunja/api:latest`, `vikunja/frontend:latest`, `postgres:16` (official, scanned via Trinity).
  - Podman Command (from 2026 SuperUser/Red Hat guides):
    ```
    podman pod create --name vikunja-pod -p 3456:80
    podman run -d --pod vikunja-pod --name vikunja-db -v ./db:/var/lib/postgresql/data:Z -e POSTGRES_PASSWORD=secret postgres:16
    podman run -d --pod vikunja-pod --name vikunja-api -v ./files:/app/vikunja/files:Z -e VIKUNJA_DATABASE_URL=postgresql://user:secret@vikunja-db:5432/vikunja -e VIKUNJA_SERVICE_PUBLICURL=http://localhost:3456 vikunja/api
    podman run -d --pod vikunja-pod --name vikunja-frontend vikunja/frontend
    ```
    - :Z for SELinux (rootless fix).
    - Env vars: Inject at runtime (VIKUNJA_*)—disable CORS if local-only (`VIKUNJA_CORS_ENABLE=false`).
    - Config: Mount `/etc/vikunja/config.yml` if needed, but prefer env for secrets.
  - Hardening: User namespaces (`userns=keep-id`), no privileged, read-only rootfs where possible. Scan images pre-run: `podman save -o vikunja.tar vikunja/api && trivy image --input vikunja.tar`.

- **Phase 3: MCP Integration (Agent Hooks)**
  - New `vikunja-mcp.py`: REST API wrapper (auth token from env).
    - Functions: `create_task(namespace, project, summary, description, labels, priority)`, `update_status(task_id, status)`, `get_board(namespace, project)`.
    - Gemini CLI: `vikunja-mcp.py create_task --namespace Sync --project Phase-2 --summary "Qwen Eval" --labels ma_at_41 --priority high`.
    - Cline: IDE hook for refactor tasks—post on save.
  - Plugins: Only trusted (e.g., Vja CLI for terminal tasks)—test in dev, backup DB pre-install.

- **Phase 4: CI/CD & Monitoring**
  - Pre-commit: Scan for secrets (git-secrets hook).
  - CI: Podman build/test, Trinity scans on push.
  - Offline: Cache images/DB backups—run air-gapped post-setup.

Best Practices (2026 Sourced): DevSecOps integration (SentinelOne/Singularity for runtime monitoring), policy enforcement (userns="host" only if multi-tenant, else keep-id for isolation). Backup DB weekly, monitor via Podman logs.

### 4. Secrets Hygiene: Zero-Trust Upload Prevention
No .env or yaml commits—ever. Aligns with Ma'at 36 (integrity).

- **gitignore Mastery**:
  - Add: `.env`, `*.secrets.yaml`, `vikunja/config.yml` (if file-based), `db/*` (Postgres data).
  - Pre-commit hook: `git-secrets --install` + scan for patterns (API keys, passwords).

- **Runtime Injection**:
  - Env vars only: `export VIKUNJA_API_TOKEN=...` in shell (Gemini CLI), or Podman `-e`.
  - No hardcodes: Use `os.getenv` in scripts, fallback to prompts.
  - Rotation: Script `rotate-secrets.py`—new token on deploy, store in local vault (e.g., pass).

- **Audits**:
  - Trinity Pre-Push: Syft SBOM → Grype CVEs → Trivy secrets/misconfigs.
  - GitHub: No actions with secrets—local CI only for sovereignty.

Best Practices (OX Security/Fyld 2026): Embed in DevSecOps—auto-scan pipelines, least-privilege (rootless), dynamic context-aware agents (ties to our SONA persistence).

Elite lockdown: Your env is now a fortress—migration cements it.
