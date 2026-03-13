Model card: Qwen3-0.6B-Q6_K.gguf
Path: models/Qwen3-0.6B-Q6_K.gguf
Format: GGUF (quantized)
Primary role: Small chat/coder model for validation, quick checks, and low-latency assistant tasks.
Recommended runtimes: llama.cpp / ggml runtimes supporting GGUF.
Primary use-cases: schema validation, short QA checks, quick code transforms, local verification of structured outputs.
Suggested inference settings: temperature 0.0-0.5 for testing; use 0.0 for deterministic validation.
Knowledge gaps / research tasks:
- Confirm exact tokenizer and vocabulary size.
- Confirm model context window and effective performance profiles.
- License/provenance check and acceptable production uses.
Next steps:
- Create a small validator wrapper that re-parses ruvltra-generated JSON and applies business rules.