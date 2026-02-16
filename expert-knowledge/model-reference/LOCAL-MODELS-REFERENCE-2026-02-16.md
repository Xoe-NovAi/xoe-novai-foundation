Local Models Reference — Xoe-NovAi Stack
Date: 2026-02-16
Path: /home/arcana-novai/Documents/xnai-foundation/models

Purpose
- Inventory local models, describe runtime options (torch-free where possible), recommend use-cases for the 16‑phase hardening plan, and provide an actionable workflow for using ruvltra-claude-code-0.5b-q4_k_m.gguf to generate structured phase-execution JSON for assigned agents.

Summary of discovered models

1) Gemma-3-1B_int8.onnx
- Format: ONNX (int8)
- Type: General LLM / synthesis
- Best runtimes: onnxruntime (CPU), ONNX-TRT if available on GPU (not recommended for this host)
- Use-cases: longer-form synthesis when deterministic inference and torch-free runtime are required; good for Phase-level summarization and multi-doc condensation (use in Gemini for heavier synthesis and Copilot for mid‑size summaries).
- Memory & performance notes: int8 ONNX lowers peak memory; still budget batches and use small chunking (4–8 docs/batch) on Ryzen 5700U.
- Conversion notes: already ONNX — preferred primary runtime for torch-free policy.

2) Qwen3-0.6B-Q6_K.gguf
- Format: GGUF (quantized)
- Type: Small chat/coding LLM
- Best runtimes: llama.cpp / ggml-based runtimes supporting GGUF
- Use-cases: low-latency assistant tasks, quick code transforms, validators for structured outputs; useful for Cline lightweight review tasks and Copilot orchestration tasks.
- Memory & performance: very small footprint; ideal for many concurrent tasks.
- Conversion notes: no ONNX needed — use GGUF runtime.

3) distil-large-v3 (directory)
- Format: local model directory (inspect for format/metadata before heavy use)
- Type: likely distilled transformer (classification / embedding)
- Use-cases: spot-check classification or QA tasks; validate by reading model card in repository.
- Action: inspect README or metadata before production use.

4) embeddinggemma-300M-Q8_0.gguf
- Format: GGUF (embedding model)
- Type: Embeddings
- Best runtimes: llama.cpp (embedding mode) or embeddingGemma tooling (see expert-knowledge/embeddings/embeddinggemma-setup-v1.0.0.md)
- Use-cases: primary embedding model for Qdrant ingestion and FAISS fallback; fits memory constraints well when batching.
- Notes: use embeddingGemma workflow to avoid torch; run small batches (4–8 docs) for Ryzen 5700U.

5) functiongemma-270m-it-Q6_K.gguf
- Format: GGUF
- Type: lightweight function/execution assistant
- Use-cases: helper tasks (prompt transformations, validation, small conversions), good for Copilot-run checks.

6) gemma-3-1b-it-heretic-abliterated-uncensored.i1-Q5_K_M.gguf
- Format: GGUF
- Type: instruction-tuned Gemma 3 (1B)
- Use-cases: stronger instruction-following when ONNX Gemma isn't required; use carefully with license/policy checks.
- Notes: prefer onnx Gemma where possible to honor torch-free guardrails; use GGUF for fallback with llama.cpp.

7) piper (directory)
- Format: TTS engine (Piper resources)
- Type: Text-to-speech
- Use-cases: voice interface (Phase 2/Chainlit voice runtime). Use with silero assets.
- Notes: check piper README for engine & model files.

8) ruvltra-claude-code-0.5b-q4_k_m.gguf
- Format: GGUF (quantized code-specialized model)
- Type: Small code / structured-output LLM
- Best runtimes: llama.cpp / ggml runtimes supporting GGUF
- Use-cases (high priority): generating deterministic, structured JSON (phase task lists, Vikunja task payloads, execution manifests), parsing and converting short docs into structured entries. Ideal as a fast, local generator for per-batch task extraction prior to Gemini-led deep synthesis and Cline approval.
- Memory & performance: very low footprint; excellent for running many small structured generations in parallel within memory budget.
- Validation: always validate model output against a JSON schema (jq, jsonschema, or a second-pass verifier model) before persisting to Redis or creating Vikunja tasks.

9) silero (directory)
- Format: TTS / speech models
- Use-cases: audio front-end (voice UX). See silero docs in repo.


How these models map to the 16-phase hardening plan
- Embeddings (Phase‑0 indexing & Phase B pre-execution): use embeddinggemma-300M.gguf via embeddingGemma or llama.cpp embedding mode to produce vectors for Qdrant/FAISS with small batch sizes.
- Fast structured task generation (Phase batching): use ruvltra-claude-code-0.5b to convert doc excerpts into structured JSON tasks for Vikunja and for Cline/Gemini review.
- Mid-size summarization & authoritative decisions: use Gemma-3-1B_int8.onnx (onnxruntime) when torch-free deterministic synthesis is required and context fits; for longer contexts, delegate to Gemini (external) or use on-disk FAISS + streaming strategies to keep tokens small.
- TTS and voice testing (Phase 2): use piper + silero assets for voice runtime verification and integration tests.
- Low-latency orchestration and validators: use Qwen3-0.6B and functiongemma-270m for quick checks, schema validation, and pre-commit formatting.

ONNX conversion guidance (torch-free policy)
- Prefer models already available as ONNX (Gemma-3-1B_int8.onnx) and use onnxruntime for inference to comply with torch-free policy.
- Many GGUF models (Qwen3, ruvltra, embeddingGemma) are directly usable via llama.cpp / ggml runtimes without PyTorch — this is the recommended torch-free path for GGUF assets.
- Converting GGUF → ONNX typically requires access to the original PyTorch weights and a conversion toolchain (transformers/exporters), which demands PyTorch; avoid converting locally under torch-free constraints unless performed in an isolated, ephemeral environment that complies with project policies.

Practical workflow to generate structured phase execution JSON using ruvltra-claude-code-0.5b (recommended)
1) Extraction: For each doc chunk (size tuned to 512–2k tokens), prompt ruvltra with a strict JSON-only scaffold and low temperature (0.0–0.2) to produce deterministic results.

Prompt template (system + user):
- System: "You are a structured task generator. Output ONLY a JSON object that follows the schema provided. Do not include explanatory text."
- User: "Schema: {\"phase\":string, \"tasks\":[{\"id\":string,\"title\":string,\"description\":string,\"assigned_agent\":string,\"est_minutes\":number,\"acceptance_criteria\":string}], \"dependencies\":[], \"notes\":string}\n\nSource: <insert doc excerpt>\n\nGenerate the JSON manifest for this source."

2) Validation: Run produced JSON through jq/jsonschema or a second-pass verifier model (Qwen3-0.6B or functiongemma) to ensure schema compliance.
3) Persistence: On pass, write to Redis keyspace doc-tasks:{phase}:{id} and create Vikunja tasks via the prepared vikunja_tasks.json templates.
4) Review: Assign to agent:cline-kat for authoritative human review; if approved, Copilot executes non-destructive moves and updates Qdrant/FAISS indices.

Example CLI invocation (llama.cpp-like runtime)
- Use deterministic settings (low temp, top_k/top_p tuned)
- Example (conceptual):
  ./main -m models/ruvltra-claude-code-0.5b-q4_k_m.gguf -p "<PROMPT_FROM_TEMPLATE>" -n 512 --temp 0.2 --top_k 40
- If using a Python wrapper (llama-cpp-python), set model params accordingly and capture raw output for validation.

Recommendations & next steps
- Action 1: Use embeddinggemma-setup guidance in expert-knowledge/embeddings/ before running batch embeddings to ensure torch-free embedding pipeline.
- Action 2: Use ruvltra-claude-code-0.5b for an initial smoke-test: generate Phase-1 structured JSON from MASTER-PLAN-v3.1.md excerpt and validate via functiongemma or Qwen3; confirm schema & persistence flow.
- Action 3: For large synthesis needs, favor Gemma-3-1B_int8.onnx via onnxruntime to remain torch-free, and reserve GGUF models for low-memory, fast tasks.
- Action 4: Add per-model model-cards into expert-knowledge/model-reference/ (one-per-file) if deeper provenance/license details are required — can be auto-generated from this summary.

Notes on safety, telemetry, and memory
- Zero-telemetry: all runtimes above are local only; do not enable remote logging/telemetry.
- Memory safety: always batch small and free model handles between runs; follow Xoe-NovAi cleanup pattern: del model; gc.collect(); await asyncio.sleep(0.1) when using python wrappers.

If you want, next step can be: (A) run a smoke test generation with ruvltra for Phase 1 (I'll run a local generation and validate), (B) run embeddingGemma test with embeddinggemma-300M for a small subset, or (C) create per-model model-cards in expert-knowledge/model-reference/ as separate files.

-- END --
