Model card: embeddinggemma-300M-Q8_0.gguf
Path: models/embeddinggemma-300M-Q8_0.gguf
Format: GGUF (quantized embedding model)
Primary role: Primary embedding model for Phase-0 indexing and FAISS backup.
Recommended runtimes: embeddingGemma toolchain, llama.cpp embedding mode, or a small custom wrapper that reads GGUF embeddings.
Primary use-cases: document embeddings for Qdrant ingestion, semantic overlap detection, and FAISS offline fallback.
Practical guidance: batch small (4–8 docs), normalize embeddings (L2) before ingestion, persist checksum and metadata for each vector.
Knowledge gaps / research tasks:
- Validate embedding dimension and exact numeric output format expected by Qdrant.
- Confirm runtime wrapper compatibility and any special tokenization for embedding mode.
- Test memory & throughput on Ryzen 5700U and define safe batch sizes.
- License/provenance check.
Next steps:
- Run a 10-document embedding smoke test and store vectors in a local FAISS index for fallback.