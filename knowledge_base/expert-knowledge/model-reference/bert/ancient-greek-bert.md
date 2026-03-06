Model card: pranaydeeps/Ancient-Greek-BERT
Path: models/pranaydeeps/Ancient-Greek-BERT (Hugging Face)
Format: HF Transformers (recommended convert to GGUF/Q8_0)

Summary
- Lightweight Ancient Greek BERT (110M params). Recommended quantization Q8_0 (~110MB) for Xoe-NovAi.
- Primary role: fast linguistic analysis (tokenization, PoS tagging, morphological analysis) and embedding generation for RAG.

Key specs
- Architecture: BERT-base variant (12-layer, 768 hidden, 12 heads)
- Params: 110M
- Context: 512 tokens
- Training corpus: First1KGreek, Perseus, PROIEL, Gorman (~20M tokens)
- License: Apache-2.0 (compatible)

Use-cases in XNAi
- Always-resident linguistic analyzer for Ancient Greek pipelines
- Produce embeddings for Qdrant/FAISS and drive Krikri generation pipeline

Integration notes
- Convert to GGUF (Q8_0) and load via llama.cpp or embeddingGemma for embedding generation.
- Keep resident (mlock/use_mmap) — ~110MB RSS expected.

Knowledge gaps / Research tasks
- Verify conversion toolchain and exact tokenization behavior after GGUF conversion
- Validate embeddingGemma compatibility and embedding dimension
- Run accuracy & perf tests on PROIEL/Perseus subsets

Next steps
- Convert HF artifact to GGUF Q8_0 and place under /models
- Add model-card to model manager and tests (see Phase 10 plan)

Sources
- internal_docs/01-strategic-planning/.../ANCIENT-GREEK-MODELS-RESEARCH.md
- https://huggingface.co/pranaydeeps/Ancient-Greek-BERT (if available)
