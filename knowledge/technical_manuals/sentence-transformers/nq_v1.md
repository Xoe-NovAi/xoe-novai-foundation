---
title: Nq V1
service: sentence-transformers
source_urls: ["/tmp/tmp_3j2bcvd/repo/docs/pretrained-models/nq-v1.md"]
scraped_at: 2026-02-17T00:26:37.024834
content_hash: aa44b5ebbc708b77b3b8c0930f85dd4749212f6803ebab01bd84aa6deef61c49
size_kb: 1.16
---

# Natural Questions Models
[Google's Natural Questions dataset](https://ai.google.com/research/NaturalQuestions) consists of about 100k real search queries from Google with the respective, relevant passage from Wikipedia. Models trained on this dataset work well for question-answer retrieval.

## Usage

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("nq-distilbert-base-v1")

query_embedding = model.encode("How many people live in London?")

# The passages are encoded as [ [title1, text1], [title2, text2], ...]
passage_embedding = model.encode(
    [["London", "London has 9,787,426 inhabitants at the 2011 census."]]
)

print("Similarity:", util.cos_sim(query_embedding, passage_embedding))
```

Note: For the passage, we have to encode the Wikipedia article title together with a text paragraph from that article.


## Performance
The models are evaluated on the Natural Questions development dataset using MRR@10.

| Approach       |  MRR@10 (NQ dev set small) |  
| ------------- |:-------------: |
| nq-distilbert-base-v1 | 72.36 |
| *Other models* | |
| [DPR](https://huggingface.co/transformers/model_doc/dpr.html) | 58.96 |