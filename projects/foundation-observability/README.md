# Foundation Observability — Project Hub

Purpose
- Create a central hub for total observability across the Xoe‑NovAi Foundation stack.
- Enable agents and models to become experts about their runtime environment (host, pods/containers, dev env, instrumentation and docs).

Goals
- Provide a runtime probe that produces both human-readable JSON and Prometheus textfile metrics.
- Store research, strategy, and Gemini materials for RAG ingestion and agent workflows.
- Maintain checklists and runbooks for staging-only automated actions.

Initial contents
- scripts/runtime_probe.py — runtime probe (host, podman/docker, vulkan, CPU/memory, env).
- tests/test_runtime_probe.py — unit test for the probe.
- memory_bank/FOUNDATION-OBSERVABILITY.md — high-level strategy + checklist.

Next steps (short)
1. Add probe to node_exporter textfile collector (systemd timer / cron). 📅
2. Wire probe outputs into Grafana dashboard panels & add alert rules. 📊
3. Add Gemini CLI processes to query the JSON state and answer environment questions.

Owner: Xoe‑NovAi foundation observability initiative
Status: draft — ongoing initiative

Contact: add notes in `expert-knowledge/gemini-inbox/INBOX_Phase5A_Agent-Collab.md` for agent handoff.