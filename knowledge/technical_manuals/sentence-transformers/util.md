---
title: Util
service: sentence-transformers
source_urls: ["/tmp/tmp_3j2bcvd/repo/docs/package_reference/util.md"]
scraped_at: 2026-02-17T00:26:37.023024
content_hash: 79a55969231f891dba9c21da599c56a683b55ee07e3256fce32d2eb477966863
size_kb: 0.77
---

# util

`sentence_transformers.util` defines different helpful functions to work with text embeddings.

## Helper Functions

```{eval-rst}
.. automodule:: sentence_transformers.util
   :members: paraphrase_mining, semantic_search, community_detection, http_get, truncate_embeddings, normalize_embeddings, is_training_available, mine_hard_negatives
```

## Model Optimization

```{eval-rst}
.. automodule:: sentence_transformers.backend
   :members: export_optimized_onnx_model, export_dynamic_quantized_onnx_model, export_static_quantized_openvino_model
```

## Similarity Metrics

```{eval-rst}
.. automodule:: sentence_transformers.util
   :members: cos_sim, pairwise_cos_sim, dot_score, pairwise_dot_score, manhattan_sim, pairwise_manhattan_sim, euclidean_sim, pairwise_euclidean_sim
```
