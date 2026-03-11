---
title: Quantization
service: sentence-transformers
source_urls: ["/tmp/tmp_3j2bcvd/repo/docs/package_reference/sentence_transformer/quantization.md"]
scraped_at: 2026-02-17T00:26:37.020440
content_hash: 1a5debc53cb13a5c288e607a4ee6bcf46e8edb7b0c23142685f4280d9d196e83
size_kb: 0.71
---

# quantization

`sentence_transformers.quantization` defines different helpful functions to perform embedding quantization.

```{eval-rst}
.. note::
   `Embedding Quantization <../../../examples/sentence_transformer/applications/embedding-quantization/README.html>`_ differs from model quantization. The former shrinks the size of embeddings such that semantic search/retrieval is faster and requires less memory and disk space. The latter refers to lowering the precision of the model weights to speed up inference. This page only shows documentation for the former.
```

```{eval-rst}
.. automodule:: sentence_transformers.quantization
   :members: quantize_embeddings, semantic_search_faiss, semantic_search_usearch
```
