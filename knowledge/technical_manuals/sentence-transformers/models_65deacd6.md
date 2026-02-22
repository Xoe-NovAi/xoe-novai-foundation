---
title: Models
service: sentence-transformers
source_urls: ["/tmp/tmp_3j2bcvd/repo/docs/package_reference/sparse_encoder/models.md"]
scraped_at: 2026-02-17T00:26:37.022232
content_hash: 65deacd64c2dd86248bb688c9dff4f016f48d492e6df945423b9f1130795dd6c
size_kb: 0.90
---

# Modules

`sentence_transformers.sparse_encoder.models` defines different building blocks, that can be used to create SparseEncoder networks from scratch. For more details, see [Training Overview](../../sparse_encoder/training_overview.md).
Note that modules from `sentence_transformers.models` can also be used for Sparse models, such as `sentence_transformers.models.Transformer` from [SentenceTransformer > Modules](../sentence_transformer/models.md)
## SPLADE Pooling
```{eval-rst}
.. autoclass:: sentence_transformers.sparse_encoder.models.SpladePooling
```

## MLM Transformer
```{eval-rst}
.. autoclass:: sentence_transformers.sparse_encoder.models.MLMTransformer
```

## SparseAutoEncoder
```{eval-rst}
.. autoclass:: sentence_transformers.sparse_encoder.models.SparseAutoEncoder
```

## SparseStaticEmbedding
```{eval-rst}
.. autoclass:: sentence_transformers.sparse_encoder.models.SparseStaticEmbedding
``` 