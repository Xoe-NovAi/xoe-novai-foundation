# Research Jobs: UI Debugging Knowledge Gaps
**Date**: 2026-03-02
**Assigned To**: Cline Kat (`kate-coder-pro`)
**Coordination Key**: UI-DEBUG-2026-03-02

During the March 2 session several interface issues emerged.  This research document defines tasks to investigate root causes and long-term solutions.

## 🧠 Tasks
1. **Caddy Routing Conflicts**
   - Analyze the `/api/*` vs `/chat/*` subpath configuration in `Caddyfile`.
   - Determine a robust rule set that avoids collisions when new UI services are added.
   - Propose a test harness (cURL script or unit test) to validate routing rules automatically.

2. **Chainlit PermissionError**
   - Investigate why Chainlit attempts to write to `/app/.files` during shutdown.
   - Determine whether this is a Chainlit bug or misconfiguration; document fix (e.g., `cache_dir` env var or volume mount). 
   - Research upstream Chainlit issues for similar reports and propose patch if needed.

3. **WebSocket Upgrade Failures**
   - Collect Caddy logs showing upgrade errors.  Correlate with connection attempts from WebUI vs Chainlit.
   - Verify TLS/headers and WebSocket limits; propose configuration adjustments or timeouts.

4. **Postgres (Gnosis) Integration**
   - Document the expected data flows for the Gnosis engine requiring Postgres.
   - Determine if the database should be spun up automatically or via a feature flag; research minimal images.

5. **Fallback & Monitoring**
   - Create monitoring checks that verify UI services are reachable and that Caddy routing rules are intact.
   - Research and propose fallback behaviours (e.g., static error page, redirect to maintenance) when services crash.

## ✅ Deliverables
- Markdown report summarizing findings for each task.
- Configuration snippets and test scripts added to `docs/architecture/` or `internal_docs/`.
- Bug reports or PR suggestions for third-party projects if issues are upstream.

## 🔁 Next Steps
1. Execute tasks sequentially, updating this document with notes.
2. Publish results to memory bank and reference in handoff docs.
3. Coordinate with Opus 4.6 to incorporate permanent fixes in strategy.
