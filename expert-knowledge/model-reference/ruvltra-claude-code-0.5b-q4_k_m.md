Model card: ruvltra-claude-code-0.5b-q4_k_m.gguf
Path: models/ruvltra-claude-code-0.5b-q4_k_m.gguf
Format: GGUF (quantized)
Primary role: Small, code-specialized model optimized for structured, deterministic outputs and code-oriented transformations.
Recommended runtimes: llama.cpp / ggml-based runtimes (llama-cpp-python wrapper for programmatic use).
Primary use-cases: Converting doc excerpts into strict JSON manifests, extracting tasks, transforming short code snippets, schema-constrained generation for Vikunja task payloads.
Suggested inference settings (start): temperature 0.0-0.2, top_k 40, max_tokens 512, repeat_penalty 1.1.
Prompt scaffold (JSON-only):
System: "You are a structured task generator. Output ONLY valid JSON that matches the schema provided. Do not include explanatory text."
User: "Schema: {\"phase\":string, \"tasks\":[{\"id\":string,\"title\":string,\"description\":string,\"assigned_agent\":string,\"est_minutes\":number,\"acceptance_criteria\":string}], \"dependencies\":[], \"notes\":string}\n\nSource: <DOC_EXCERPT>\n\nGenerate the JSON manifest for this source."
Validation: run jq/jsonschema or a second-pass verifier (functiongemma or qwen3) before persisting.
Agent mapping: primary generator: Copilot (local ruvltra), reviewer: agent:cline-kat, final approval: human operator.
Knowledge gaps / research tasks:
- Confirm exact context window (tokens) and effective max_tokens for stable JSON outputs.
- Identify tokenizer name and tokenization edge-cases with non-UTF8 inputs.
- Confirm precise quantization algorithm behind "q4_k_m" (GPTQ variant? custom layout?) and implications for determinism.
- License & provenance verification for production use and any redistribution constraints.
- Automatic schema-enforcement toolchain (jsonschema rules, verifier prompts) and a sample wrapper script.
Next steps:
- Run a smoke-test: feed a 512-token excerpt from MASTER-PLAN-v3.1.md and generate a Phase-1 JSON; validate via jq and functiongemma.