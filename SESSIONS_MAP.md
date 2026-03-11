# 🗺️ Omega Stack: Strategic Session Roadmap (v1.3)

This roadmap assigns all tasks into 9 targeted, context-efficient chat sessions.

---

## 🛡️ SESS-01: Identity & Credentials
**Focus**: Stabilize ownership and secure credentials.
- [x] **Filesystem Cleanup**: Merge `_new` folders and lock UID 1000 ownership.
- [x] **Task C3**: Purge `changeme123` & `vikunja123` from all files.
- [x] **Task P3**: Restore `rate_limit_handler.py`.
- [x] **MB-MCP Fix**: Resolve `fastapi` and upgrade Watchdog.
- [x] **MPI Update**: Integrate 'dark layers' and drift reports.
- [x] **Protocols**: Lock in `SECRETS_ENFORCEMENT` and `DOCUMENTATION_IMPACT`.

## 🧠 SESS-02: Memory Bank Hardening
**Focus**: Ensure the agent's memory survives restarts and Redis failures.
- [ ] **Task MB1**: Persistence (Restore agents from Redis on startup).
- [ ] **Task C1**: Redis Null-Guards in `server.py` to prevent crashes.
- [ ] **Task MB4**: Redis Reconnection Logic.
- [ ] **Task MB5**: Filesystem Persistence for context data (Write-through).
- [ ] **Task MB3**: LRU Cache for context (Prevent OOM).
- [ ] **Task MB6**: `run_server.sh` Venv Validation.

## 🏗️ SESS-03: Infra & Capacity
**Focus**: Fix service crashes and consolidate orchestration.
- [ ] **Task C2**: Fix Docker Compose memory over-commit.
- [ ] **Compose Consolidation**: Remediate `DG-001` (DG-001/002 drift).
- [ ] **Task P1/P2**: Fix Healthchecks for MCP and Qdrant.
- [ ] **Task ST4**: `decode_responses` standardization.

## 🔒 SESS-04: The Sentinel (Security)
**Focus**: Implement Zero-Trust across the internal mesh.
- [ ] **Task S1**: JWT Signature Verification.
- [ ] **Task S2**: MCP Agent Auth Tokens.
- [ ] **Task S4**: FAISS SHA256 Gate.
- [ ] **Task S5**: SanitizationResult Refactor.

## 📡 SESS-05: Agent Bus & Streams
**Focus**: Standardize communication protocols between facets.
- [ ] **Task ST1**: Sentinel Pub/Sub → Streams Protocol Alignment.
- [ ] **Task ST2**: `update_context` Tier Parameter.
- [ ] **Task ST5**: `asyncio.get_event_loop()` migration to AnyIO.

## 🔍 SESS-06: Deep Research & Ops
**Focus**: Finalize unaudited components and establish testing.
- [ ] **Audit Queue**: Review `xnai-rag`, `xnai-memory`, `xnai-sambanova`.
- [ ] **Testing**: Run `pytest --cov` and address low-coverage modules.

## 🐙 SESS-07: GitHub & Skills Ecosystem
**Focus**: GitHub management, workflows, Gemini features (Skills, Extensions, Agents).
- [ ] **GitHub Strategy**: Repository health and PR workflows.
- [ ] **Skills Ecosystem**: Audit and expand Gemini CLI skills.

## 🗺️ SESS-08: GEMINI.md Audit & Protocol Hardening
**Focus**: Review and enhance domain directives.
- [ ] **Directives Audit**: Review all `GEMINI.md` files for 2026 alignment.
- [ ] **Advanced Protocols**: Implement best practices for agent coordination.

## 📚 SESS-09: Documentation Management & Cleanup
**Focus**: Final synchronization of all diagrams and manuals.
- [ ] **Mermaid Sync**: Update all architectural diagrams to match Metropolis Mesh.
- [ ] **Diátaxis Alignment**: Refactor `docs/` into Tutorial/How-to/Reference/Explanation.

## 🗺️ SESS-10: zRAM Hardening & Crisis Management
**Focus**: Address missing swap capacity and implement fine-grained monitoring.
- [x] **Capacity Restoration**: Fixed missing 4GB swap (12GB total zstd).
- [x] **Fine-Grained Monitoring**: Deployed `monitor_swap.py` exporter.
- [x] **Resource Guard**: Applied Task C2 memory limits.

## 🧠 SESS-11: Context Management & Summarization Agent
**Focus**: Keep Gemini sessions performant via automated summarization.
- [ ] **Agent Design**: Implement local agent using `Qwen3-0.6B`.
- [ ] **History Crawling**: Periodic scan of oldest messages in session context.
- [ ] **Summarization Protocol**: Replace old turns with high-fidelity summaries.
- [ ] **Performance Benchmarking**: Measure context reduction impact.

## 🗺️ SESS-12: Rate Limit Optimization & OAuth Expansion
**Focus**: Maximize Gemini throughput via dual-auth per account.
- [ ] **Dual-Auth Implementation**: Configure agents to use both OAuth and API Keys simultaneously.
- [ ] **Service Account Setup**: Implement non-interactive OAuth via Google Cloud Service Accounts.
- [ ] **RPD Monitor**: Track RPD usage across 8 accounts (Target: 10,000 RPD).
- [ ] **Load Balancing**: Distribute agent work based on quota availability.

## 🏛️ SESS-13: Discovery & Palace Strategy
**Focus**: Strategize using archived documents from the "RECLAIMED_PALACE" vault.
- [ ] **Palace Indexing**: Index documents in `/media/arcana-novai/omega_vault/RECLAIMED_PALACE` using Facet 3 (The Researcher).
- [ ] **Strategy Extraction**: Distill old research into actionable tasks for the 2026 Metropolis roadmap.
- [ ] **Cross-Linkage**: Connect legacy research with current `memory_bank` state.
- [ ] **Autonomous Synthesis**: Generate a "Palace Audit Report" with forward-looking directives.

## 🤖 SESS-14: Cline Optimization & Instruction Adherence
**Focus**: Resolve Cline CLI's repeated failure to follow "No-Modify" directives.
- [ ] **Failure Audit**: Review logs of SESS-02 where Cline violated MB-MCP directives.
- [ ] **Instruction Hardening**: Implement `.clinerules` and system prompts to enforce strict domain boundaries.
- [ ] **Tool Constraint**: Research and implement restricted tool access for Cline during concurrent agent work.
- [ ] **Team Handshaking**: Establish a protocol for agents to signal "Domain Locked" status to each other.

## ✂️ SESS-15: Context Management & Chat Trimming
**Focus**: Implement the "Chat Trimming Protocol" to resolve stability and CPU issues.
- [x] **The Librarian**: Deployed background service for recursive summarization.
- [x] **KV Cache Optimization**: Implemented `q4_0` quantization for 32k context.
- [x] **State Hydration**: Established mandatory atomic synchronization protocol.
- [x] **GitHub Sync**: Defined 7-stage CI/CD parity loop.

## 📦 SESS-16: Image Bloat & Build Optimization
**Focus**: Inspect images and build process to reduce size and eliminate "dark layers".
- [ ] **Layer Analysis**: Use `dive` or similar to identify bloated layers in `xnai-rag` and `xnai-base`.
- [ ] **MPI Integration**: Add findings to the Master Plan Index for long-term tracking.
- [ ] **Optimization Pass**: Refactor Dockerfiles to leverage multi-stage builds and minimize runtime dependencies.
- [ ] **Dark Layer Detection**: Systematic scan for redundant `apt` or `pip` operations across the mesh.

## 🚰 SESS-17: OpenPipe Deep Integration
**Focus**: Explore and implement advanced OpenPipe features for LLM optimization and data collection.
- [ ] **Usage Audit**: Review current OpenPipe usage and identify optimization opportunities.
- [ ] **Advanced Logging**: Implement fine-grained prompt/response logging via OpenPipe.
- [ ] **Fine-Tuning Pipeline**: Research and design a pipeline for using OpenPipe data for local model fine-tuning.
- [ ] **Metric Correlation**: Integrate OpenPipe metrics with VictoriaMetrics and Grafana.

## 📊 SESS-19: Gemini Observability & Token Metrics
**Focus**: Implement comprehensive tracking for Gemini CLI performance, token usage, and cache efficiency.
- [ ] **Token Tracker**: Implement a tool or dashboard to track tokens per turn and cumulative session usage.
- [ ] **Cache Efficiency**: Monitor and report on cache hit/miss rates for session context.
- [ ] **Cost Analysis**: Estimate real-world or theoretical cost of turns based on token usage.
- [ ] **Prometheus Integration**: Export Gemini metrics to VictoriaMetrics for long-term historical analysis.

## 📱 SESS-21: Mobile Agent-Bus Gateway
**Focus**: Enable secure communication with the Agent Bus via mobile devices.
- [ ] **Gateway Research**: Design a secure endpoint (likely via Caddy + Auth) for mobile access.
- [ ] **Interface Design**: Prototype a simple mobile-friendly UI or bot interface (Telegram/WhatsApp/Web).
- [ ] **Security Hardening**: Implement DPoP or similar for mobile client authentication.
- [ ] **Network Strategy**: Optimize for varying latency and connectivity.

## 🧠 SESS-22: Global Model Curation & Partition Scan
**Focus**: Scan and index all available GGUF/ONNX models across all system partitions.
- [ ] **Partition Scan**: Systematically search `/`, `/media`, and other mounts for model files.
- [ ] **Integrity Audit**: Verify checksums and metadata for all discovered models.
- [ ] **Omega Indexing**: Register found models in the Omega stack model registry.
- [ ] **Hardening pass**: Implement strict validation for model loading and usage.

---

### 📌 Session Hygiene:

- Keep chat context <5MB.
- **START EVERY SESSION** with an MB-MCP health check: `curl http://localhost:8005/health`.
