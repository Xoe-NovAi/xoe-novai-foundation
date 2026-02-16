Model card: SciBERT (allenai/scibert_scivocab_uncased)
Path: https://huggingface.co/allenai/scibert_scivocab_uncased
Format: HF Transformers (recommend GGUF conversion for local use)

Summary
- SciBERT: BERT-family model trained on scientific publications (Semantic Scholar corpus).
- Primary role: domain-specific semantic embeddings and classification for scientific texts.

Use-cases
- Domain-aware retrieval for research docs, extracting methods/results, semantic search in Phase indexing.
- Feature extraction for downstream QA and citation matching.

Integration guidance
- Test embeddingGemma or convert to GGUF and run embeddings in small batches (4-8 docs) for memory safety.
- Validate tokenizer and embedding dimension with Qdrant schema.

Knowledge gaps
- License compatibility for production use (HF listing indicates permissive but confirm model card)
- Best quantization path (GGUF Q8_0 or onnx) for embedding fidelity vs speed

Next steps
- Download, convert to GGUF, run embedding smoke test on 10 papers, persist to FAISS backup.
