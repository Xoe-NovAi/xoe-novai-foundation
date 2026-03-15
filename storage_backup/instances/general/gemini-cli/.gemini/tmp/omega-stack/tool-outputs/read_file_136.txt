Model card: Llama-Krikri-8B-Instruct (ilsp)
Path: https://huggingface.co/ilsp/Llama-Krikri-8B-Instruct
Format: HF Transformers / official GGUF quantized artifacts recommended

Summary
- Instruction-tuned 8B model specialized for Greek (built on Llama-3.1-8B). Strong performance on Greek & bilingual tasks.
- Reported context length: 128k (very large context support) per HF model page; SFT+DPO trained on Greek & English.

Use-cases
- High-quality generation for Greek translation, explanation, and creative tasks in the RAG pipeline.
- Partner with Ancient-Greek-BERT for analysis (BERT for PoS/embeddings, Krikri for generation).

Integration guidance
- Use official GGUF artifacts (HF strongly recommends official quantized versions).
- For local use prefer llama.cpp / ggml or vLLM for large-context scenarios; mmap strategy recommended for low memory.

Knowledge gaps
- Confirm which GGUF quantization variants are available (Q4_K_M, Q5_K_M) and pick tested artifact.
- Test real-world memory & latency on Ryzen 5700U for mmap + working set.

Next steps
- Download official GGUF or request specific quantized artifact per HF warning; validate via smoke tests.
- Add to model manager as on-demand mmap candidate; write tests for first-load latency & memory footprint.

Source
- https://huggingface.co/ilsp/Llama-Krikri-8B-Instruct
