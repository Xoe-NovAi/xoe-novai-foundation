### Research Unit 3 Execution Summary

Based on extensive research from web sources, hybrid search combining BM25 (sparse) and FAISS (dense) with Reciprocal Rank Fusion (RRF) improves retrieval accuracy by 10-30% for technical/keyword-heavy queries, as seen in implementations from LlamaIndex, LangChain, and Meilisearch. RRF is preferred for its score-agnostic ranking (using 1/(k + rank), k=60). For auto-tuning, FAISS ParameterSpace and heuristics tie nprobe to sqrt(nlist) scaled by dataset size and CPU time budgets, aiming for sub-second searches. IndexIVFFlat scales to large datasets (>10k vectors) by clustering (nlist ~ sqrt(N)), reducing search time 10-100x vs. IndexFlatL2, with serialization via write_index/read_index for disk persistence, enabling fast restarts without rebuilding.

Deliverables integrate into existing Python setup without new databases, assuming documents and embeddings are available (embedder placeholder; maintain Torch-free by using ONNX alternatives if needed).

#### Deliverable 3.1: `HybridRetriever` class in `main.py` that combines keyword and semantic search.
This class fuses BM25 and FAISS results via RRF for improved technical query recall.

```python
from rank_bm25 import BM25Okapi
import faiss
import numpy as np

class HybridRetriever:
    def __init__(self, documents, embeddings, faiss_index=None):
        # Sparse: BM25 on tokenized docs
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.documents = documents
        
        # Dense: FAISS index (default to FlatL2 if none provided)
        if faiss_index is None:
            d = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(d)
            self.faiss_index.add(embeddings.astype(np.float32))
        else:
            self.faiss_index = faiss_index

    def retrieve(self, query, top_k=5, k_rrf=60):
        # Sparse retrieval with BM25
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_results = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Dense retrieval (embed query; placeholder for Torch-free embedder)
        query_embedding = self._embed_query(query)  # Implement with ONNX or similar
        _, dense_indices = self.faiss_index.search(query_embedding.astype(np.float32), top_k)
        dense_results = [(int(idx), 1.0) for idx in dense_indices[0]]  # Dummy scores; ranks matter for RRF
        
        # Reciprocal Rank Fusion
        all_docs = set(idx for idx, _ in bm25_results).union(idx for idx, _ in dense_results)
        bm25_ranks = {idx: rank + 1 for rank, (idx, _) in enumerate(bm25_results)}
        dense_ranks = {idx: rank + 1 for rank, (idx, _) in enumerate(dense_results)}
        
        rrf_scores = {}
        for doc_id in all_docs:
            score = 0.0
            if doc_id in bm25_ranks:
                score += 1.0 / (k_rrf + bm25_ranks[doc_id])
            if doc_id in dense_ranks:
                score += 1.0 / (k_rrf + dense_ranks[doc_id])
            rrf_scores[doc_id] = score
        
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.documents[idx], score) for idx, score in sorted_results]

    def _embed_query(self, query):
        # Placeholder: Replace with actual embedder (e.g., ONNX sentence-transformers)
        return np.random.rand(1, self.faiss_index.d).astype(np.float32)

# Integration in main.py:
# retriever = HybridRetriever(your_docs, your_embeds)
# results = retriever.retrieve("example technical query")
```

Add to Docker: `pip install rank_bm25`.

#### Deliverable 3.2: `optimize_index()` function that auto-configures the index at startup.
This dynamically sets nprobe based on dataset size and CPU time, using heuristics from FAISS docs (nprobe scales with sqrt(nlist), clamped for balance).

```python
import faiss
import numpy as np
import time

def optimize_index(faiss_index, dataset_size, target_search_time=0.5):
    if not hasattr(faiss_index, 'nprobe'):
        print("Index does not support nprobe (not IVF). Skipping optimization.")
        return faiss_index
    
    nlist = faiss_index.nlist
    d = faiss_index.d
    
    # Initial heuristic: nprobe ≈ sqrt(nlist)
    base_nprobe = max(1, int(np.sqrt(nlist)))
    faiss_index.nprobe = base_nprobe
    
    # Benchmark with sample query
    sample_query = np.random.rand(1, d).astype(np.float32)
    start = time.time()
    faiss_index.search(sample_query, 10)
    elapsed = time.time() - start
    
    # Adjust based on time (scale down if too slow, up for accuracy)
    adjustment_factor = target_search_time / max(elapsed, 1e-6)
    optimized_nprobe = int(base_nprobe * adjustment_factor)
    
    # Clamp by dataset size
    if dataset_size > 100000:
        optimized_nprobe = min(max(optimized_nprobe, 16), 128)  # Large datasets: higher for accuracy
    elif dataset_size > 10000:
        optimized_nprobe = min(max(optimized_nprobe, 8), 64)
    else:
        optimized_nprobe = min(max(optimized_nprobe, 1), 32)
    
    faiss_index.nprobe = optimized_nprobe
    print(f"Auto-tuned nprobe to {optimized_nprobe} for dataset size {dataset_size}")
    return faiss_index

# Usage at startup (e.g., in main.py init):
# optimized_index = optimize_index(your_faiss_index, len(your_dataset))
```

Run once at load; re-run if dataset changes.

#### Deliverable 3.3: Updated `vectorstore` dependency with IVF support and safe disk persistence.
This enhances `vectorstore.py` to use IndexIVFFlat for >10k vectors, with automatic disk serialization for persistence.

```python
import faiss
import numpy as np
import os

class VectorStore:
    def __init__(self, dimension, index_path='faiss_index.bin', threshold=10000):
        self.dimension = dimension
        self.index_path = index_path
        self.threshold = threshold
        self.index = None

    def load_or_build(self, embeddings, nlist=None):
        num_vectors = embeddings.shape[0]
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            print(f"Loaded persisted index from {self.index_path}")
        else:
            if num_vectors > self.threshold:
                # IVF for large datasets; nlist default ~ sqrt(N)
                if nlist is None:
                    nlist = max(4, int(np.sqrt(num_vectors)))
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                self.index.train(embeddings.astype(np.float32))
            else:
                # Flat for small
                self.index = faiss.IndexFlatL2(self.dimension)
            
            self.index.add(embeddings.astype(np.float32))
            faiss.write_index(self.index, self.index_path)
            print(f"Built and persisted index to {self.index_path}")

    def add_vectors(self, new_embeddings):
        if self.index is None:
            raise ValueError("Index not initialized. Call load_or_build first.")
        self.index.add(new_embeddings.astype(np.float32))
        faiss.write_index(self.index, self.index_path)  # Update persistence
        print("Added vectors and updated disk persistence.")

    def search(self, query_embedding, k=5):
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        return indices, distances

# Usage:
# store = VectorStore(dimension=384)
# store.load_or_build(np.random.rand(15000, 384))  # Uses IVF, persists to disk
# indices, _ = store.search(np.random.rand(1, 384))
```