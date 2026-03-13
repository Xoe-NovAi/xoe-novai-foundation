---
id: FOUNDATION-OBSERVABILITY-20260213
title: Foundation Observability — project hub
summary: |
  Centralize runtime visibility so agents and models can query and reason about their environment.
  Provide JSON + Prometheus outputs, runbooks, and Gemini integration for long-term agent expertise.
tags: [observability, agents, gemini, runtime-probe]
---

## Project purpose
- Make environment introspection a core pillar of the Foundation stack.
- Provide agents with authenticated, versioned, and queryable runtime state.

## Components
- `scripts/runtime_probe.py` — probe that emits `runtime_probe.json` and `runtime_probe.prom`.
- Prometheus textfile collector ingestion (monitoring/prometheus/textfile).
- Grafana panels + alert rules (follow-up PR).
- Gemini CLI integration to query the JSON and answer environment questions.

## Checklist (initial)
- [x] Create runtime_probe script (read-only). ✅
- [x] Add unit test for runtime_probe. ✅
- [ ] Add systemd timer / cron to run probe regularly.
- [ ] Add Grafana panels and Alert rules.
- [ ] Add Gemini CLI tools to query `runtime_probe.json`.
- [ ] Add agent training docs + RAG ingestion pointers.

## Owner
- Xoe-NovAi observability initiative (Phase-5A)
