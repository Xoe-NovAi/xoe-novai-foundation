Memory Bank: Model Cards Summary — 2026-02-16

Summary:
- Created per-model cards for local models found in /models: ruvltra-claude-code, Gemma ONNX, Qwen3, embeddingGemma, functionGemma, Gemma gguf variant, distil-large-v3, Piper, Silero.
- Created MODEL-CARDS-INDEX.md for agent-friendly discovery.

Actionable next steps (stored here):
- Run discovery tests for each model (tokenizer, context window, sample inference, memory telemetry).
- Run embedding smoke test with embeddinggemma and safe batch size tuning.
- Run a ruvltra smoke test to generate Phase-1 JSON and validate pipeline.
- Update plan.md with model-to-phase mapping and assign ownership for per-model research tasks.

Notes:
- All artifacts are local; obey zero-telemetry policy.
- Use torch-free runtimes where possible (onnxruntime, llama.cpp).

Update 2026-02-16: Added per-model cards for Ancient-Greek-BERT, SciBERT and science-BERT overview, philosophy-BERT (candidate), Krikri-8B-Instruct, Phi family placeholder (Phi-3-Omnimatrix), and roc-raccoon placeholder. Next steps: run conversion & discovery smoke-tests (GGUF/ONNX), and create Vikunja tasks for unresolved research items.
