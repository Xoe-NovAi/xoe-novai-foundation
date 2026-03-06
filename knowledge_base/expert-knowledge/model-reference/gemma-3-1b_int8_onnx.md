Model card: Gemma-3-1B_int8.onnx
Path: models/Gemma-3-1B_int8.onnx
Format: ONNX (int8)
Primary role: Mid-sized instruction-following / synthesis model with torch-free runtime via onnxruntime.
Recommended runtimes: onnxruntime (CPU); optionally ONNX-TRT if GPU available and supported.
Primary use-cases: mid-length summarization, multi-document condensation, authoritative synthesis where torch-free determinism is required.
Performance notes: int8 improves memory footprint; still batch documents and stream long inputs.
Suggested inference tactics: chunk large documents, use few-shot system prompts, prefer deterministic settings (low temp).
Knowledge gaps / research tasks:
- Confirm exact tokenizer and token-to-byte mapping for ONNX runtime inference wrappers.
- Measure real peak memory on Ryzen 7 5700U with typical batch sizes (4–8 docs) and produce guidance.
- Validate license and allowed usages for Gemma variant.
- Verify if GEMMA model supports streaming generation via onnxruntime or requires full-token runs.
Next steps:
- Add a small runnable example using onnxruntime and capture memory telemetry during a 4-doc batch.