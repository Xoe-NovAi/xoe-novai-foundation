Repository Copilot Instructions — XNAi Orchestration & Hardening (XOH)

Purpose
- Provide Copilot repository-level guidance so Copilot CLI and agents use project conventions, honor zero-telemetry, and follow model/runtime constraints.

Key rules
- Zero-telemetry: do not call external APIs for model inference without explicit user approval.
- Torch-free policy: prefer ONNX/GGUF/llama.cpp runtimes; avoid installing PyTorch unless explicitly authorized.
- Model provenance: consult expert-knowledge/model-reference/*.md before using model artifacts.
- Agents: Default agent labels: agent:copilot (orchestration), agent:cline-kat (human review), agent:gemini-cli (heavy synthesis).
- Allowed directories for Copilot automated edits: internal_docs/**, expert-knowledge/**, vikunja_tasks/**, and app/** when explicitly authorized.

How to use
- Use /init to initialize repository-level instructions for Copilot CLI.
- Use /instructions to view or toggle repository instructions.

