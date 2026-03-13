---
title: ruvltra-claude-code-0.5b-q4_k_m
description: "Local GGUF Claude-like code model for structured agent tasking (0.5B, q4_k_m GGUF)."
model_family: claude
size: 0.5b
format: gguf
path: models/ruvltra-claude-code-0.5b-q4_k_m.gguf
embedding_support: false
license: unknown
priority: high
frq_score: 9
---

ruvltra-claude-code-0.5b-q4_k_m.gguf is a local GGUF-format model intended for on-device structured tasking and code generation.

Usage notes:
- Intended for local use with llama.cpp / ggml / GGUF-compatible runners.
- Do NOT enable external telemetry; follow zero-telemetry policy.
- Preferred for structured JSON/agent prompts to reduce token costs and improve determinism.
- Add model to models/registry.json via scripts/model_registry.py and expose path to agent_coordinator/agent_watcher for selection.

Operational tasks:
- Validate model format and load test locally (llama.cpp or preferred runner).
- Add to ModelRegistry and mark as high priority in XNAi Agent Bus config.
- Create wrapper to expose simple `generate(prompt, max_tokens=...)` for agent use.

