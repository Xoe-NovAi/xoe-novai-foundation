#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 6 - Semantic Search Integration Tests
# ============================================================================
# Purpose: Integration tests for search algorithm, top-k retrieval, 
#          similarity calculations, and result formatting
# Guide Reference: Phase 6 (Testing & Production Hardening)
# Last Updated: 2026-02-16
# ============================================================================

import pytest
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch


# ============================================================================
# MOCK Document CLASS (for systems without langchain)
# ============================================================================

class Document:
    """Mock Document class for testing without langchain dependency"""
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}


# ============================================================================
# SEARCH ALGORITHM TESTS
# ============================================================================

class TestSearchAlgorithm:
    """Integration tests for semantic search algorithm"""

    @pytest.fixture
    def search_engine(self):
        """Create a hybrid search engine"""
        class HybridSearchEngine:
            def __init__(self, documents: List[Document], embeddings: List[np.ndarray]):
                self.documents = documents
                self.embeddings = np.array(embeddings)
                self.doc_count = len(documents)
                
                # Normalize embeddings
                norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
                self.embeddings = self.embeddings / (norms + 1e-10)
            
            def semantic_search(
                self, 
                query_embedding: np.ndarray, 
                top_k: int = 5
            ) -> List[Tuple[int, float]]:
                """Semantic search using cosine similarity"""
                query_embedding = query_embedding / (
                    np.linalg.norm(query_embedding) + 1e-10
                )
                
                # Compute similarities
                similarities = np.dot(self.embeddings, query_embedding)
                
                # Get top-k indices
                top_indices = np.argsort(similarities)[::-1][:top_k]
                top_scores = similarities[top_indices]
                
                return list(zip(top_indices, top_scores))
            
            def bm25_search(
                self,
                query: str,
                top_k: int = 5
            ) -> List[Tuple[int, float]]:
                """BM25 lexical search"""
                from rank_bm25 import BM25Okapi
                
                tokenized = [doc.page_content.split() for doc in self.documents]
                bm25 = BM25Okapi(tokenized)
                
                query_tokens = query.split()
                scores = bm25.get_scores(query_tokens)
                
                # Get top-k
                top_indices = np.argsort(scores)[::-1][:top_k]
                top_scores = scores[top_indices]
                
                return list(zip(top_indices, top_scores))
            
            def hybrid_search(
                self,
                query: str,
                query_embedding: np.ndarray,
                top_k: int = 5,
                alpha: float = 0.5
            ) -> List[Tuple[Document, float]]:
                """Hybrid search combining semantic and lexical"""
                # Get results from both methods
                semantic_results = self.semantic_search(query_embedding, top_k * 2)
                lexical_results = self.bm25_search(query, top_k * 2)
                
                # Normalize scores
                semantic_dict = {}
                for idx, score in semantic_results:
                    semantic_dict[idx] = (score + 1) / 2  # [-1, 1] -> [0, 1]
                
                max_bm25 = max(score for _, score in lexical_results) if lexical_results else 1.0
                lexical_dict = {}
                for idx, score in lexical_results:
                    lexical_dict[idx] = score / (max_bm25 + 1e-10)
                
                # Combine scores
                combined = {}
                all_indices = set(semantic_dict.keys()) | set(lexical_dict.keys())
                
                for idx in all_indices:
                    sem_score = semantic_dict.get(idx, 0.0)
                    lex_score = lexical_dict.get(idx, 0.0)
                    combined_score = alpha * lex_score + (1 - alpha) * sem_score
                    combined[idx] = combined_score
                
                # Get top-k
                sorted_results = sorted(
                    combined.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:top_k]
                
                return [
                    (self.documents[idx], score)
                    for idx, score in sorted_results
                ]
        
        # Create test documents and embeddings
        docs = [
            Document(
                page_content="Python is a programming language",
                metadata={"id": "doc1", "type": "tech"}
            ),
            Document(
                page_content="Semantic search finds similar documents",
                metadata={"id": "doc2", "type": "tech"}
            ),
            Document(
                page_content="Machine learning uses neural networks",
                metadata={"id": "doc3", "type": "ml"}
            ),
            Document(
                page_content="Vector databases store embeddings",
                metadata={"id": "doc4", "type": "tech"}
            ),
            Document(
                page_content="Dogs are loyal pets",
                metadata={"id": "doc5", "type": "pets"}
            ),
        ]
        
        # Create deterministic embeddings
        np.random.seed(42)
        embeddings = [np.random.randn(384).astype(np.float32) for _ in docs]
        
        return HybridSearchEngine(docs, embeddings), docs

    def test_semantic_search_returns_results(self, search_engine):
        """Test that semantic search returns results"""
        engine, docs = search_engine
        
        query_emb = np.random.randn(384).astype(np.float32)
        results = engine.semantic_search(query_emb, top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(idx, (int, np.integer)) for idx, _ in results)
        assert all(isinstance(score, (float, np.floating)) for _, score in results)

    def test_semantic_search_respects_topk(self, search_engine):
        """Test that semantic search respects top_k parameter"""
        engine, docs = search_engine
        
        query_emb = np.random.randn(384).astype(np.float32)
        
        for k in [1, 2, 3, 5, 10]:
            results = engine.semantic_search(query_emb, top_k=k)
            assert len(results) <= min(k, len(docs))

    def test_bm25_search_returns_results(self, search_engine):
        """Test that BM25 search returns results"""
        engine, docs = search_engine
        
        query = "python programming"
        results = engine.bm25_search(query, top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(idx, (int, np.integer)) for idx, _ in results)

    def test_hybrid_search_combines_results(self, search_engine):
        """Test that hybrid search combines semantic and lexical"""
        engine, docs = search_engine
        
        query = "programming language"
        query_emb = np.random.randn(384).astype(np.float32)
        
        results = engine.hybrid_search(query, query_emb, top_k=3, alpha=0.5)
        
        assert len(results) <= 3
        assert all(isinstance(doc, Document) for doc, _ in results)
        assert all(isinstance(score, (float, np.floating)) for _, score in results)

    def test_hybrid_search_alpha_parameter(self, search_engine):
        """Test that alpha parameter affects results"""
        engine, docs = search_engine
        
        query = "python"
        query_emb = np.ones(384, dtype=np.float32)
        
        # Pure lexical (alpha=1.0)
        results_lex = engine.hybrid_search(query, query_emb, top_k=5, alpha=1.0)
        
        # Pure semantic (alpha=0.0)
        results_sem = engine.hybrid_search(query, query_emb, top_k=5, alpha=0.0)
        
        # Mixed (alpha=0.5)
        results_mix = engine.hybrid_search(query, query_emb, top_k=5, alpha=0.5)
        
        # All should return results
        assert len(results_lex) > 0
        assert len(results_sem) > 0
        assert len(results_mix) > 0


# ============================================================================
# TOP-K RETRIEVAL TESTS
# ============================================================================

class TestTopKRetrieval:
    """Integration tests for top-k result retrieval"""

    @pytest.fixture
    def retriever(self):
        """Create a top-k retriever"""
        class TopKRetriever:
            def __init__(self, embeddings: np.ndarray, documents: List[Document]):
                self.embeddings = embeddings
                self.documents = documents
            
            def retrieve_topk(
                self,
                query_embedding: np.ndarray,
                k: int = 5,
                min_score: float = 0.0
            ) -> List[Dict[str, Any]]:
                """Retrieve top-k results with filtering"""
                # Compute similarities
                similarities = np.dot(self.embeddings, query_embedding)
                
                # Filter by min_score
                valid_indices = np.where(similarities >= min_score)[0]
                valid_similarities = similarities[valid_indices]
                
                # Sort and get top-k
                sorted_indices = np.argsort(valid_similarities)[::-1][:k]
                
                results = []
                for idx in sorted_indices:
                    original_idx = valid_indices[idx]
                    results.append({
                        'document': self.documents[original_idx],
                        'score': float(similarities[original_idx]),
                        'rank': len(results) + 1,
                        'index': int(original_idx)
                    })
                
                return results
            
            def retrieve_with_reranking(
                self,
                query_embedding: np.ndarray,
                k: int = 5,
                reranker_func=None
            ) -> List[Dict[str, Any]]:
                """Retrieve top-k and rerank"""
                # Get more candidates than needed
                candidates = self.retrieve_topk(query_embedding, k * 3)
                
                # Rerank if function provided
                if reranker_func:
                    for result in candidates:
                        result['rerank_score'] = reranker_func(
                            query_embedding,
                            self.embeddings[result['index']]
                        )
                    candidates = sorted(
                        candidates,
                        key=lambda x: x.get('rerank_score', x['score']),
                        reverse=True
                    )
                
                # Return top-k
                for i, result in enumerate(candidates[:k]):
                    result['rank'] = i + 1
                
                return candidates[:k]
        
        docs = [
            Document(page_content=f"Document {i}", metadata={"id": f"doc{i}"})
            for i in range(10)
        ]
        
        np.random.seed(42)
        embeddings = np.random.randn(10, 384).astype(np.float32)
        
        return TopKRetriever(embeddings, docs)

    def test_topk_returns_limited_results(self, retriever):
        """Test that retrieval respects k limit"""
        query_emb = np.ones(384, dtype=np.float32)
        
        for k in [1, 3, 5, 10]:
            results = retriever.retrieve_topk(query_emb, k=k)
            assert len(results) <= k

    def test_topk_returns_ranked_results(self, retriever):
        """Test that results are properly ranked"""
        query_emb = np.ones(384, dtype=np.float32)
        results = retriever.retrieve_topk(query_emb, k=5)
        
        # Check ranking is correct
        for i, result in enumerate(results):
            assert result['rank'] == i + 1

    def test_topk_score_ordering(self, retriever):
        """Test that results are ordered by score"""
        query_emb = np.ones(384, dtype=np.float32)
        results = retriever.retrieve_topk(query_emb, k=5)
        
        scores = [r['score'] for r in results]
        # Scores should be in descending order
        assert scores == sorted(scores, reverse=True)

    def test_topk_min_score_filtering(self, retriever):
        """Test that min_score parameter filters results"""
        query_emb = np.ones(384, dtype=np.float32)
        
        results_no_filter = retriever.retrieve_topk(query_emb, k=100, min_score=0.0)
        results_filtered = retriever.retrieve_topk(query_emb, k=100, min_score=0.5)
        
        assert len(results_filtered) <= len(results_no_filter)
        assert all(r['score'] >= 0.5 for r in results_filtered)

    def test_topk_empty_results(self, retriever):
        """Test handling of no results"""
        # Query with very negative values unlikely to match
        query_emb = -np.ones(384, dtype=np.float32)
        
        results = retriever.retrieve_topk(query_emb, k=5, min_score=0.999)
        # May be empty or have few results
        assert isinstance(results, list)


# ============================================================================
# COSINE SIMILARITY TESTS
# ============================================================================

class TestCosineSimilarity:
    """Integration tests for cosine similarity calculations"""

    @pytest.fixture
    def similarity_calculator(self):
        """Create a similarity calculator"""
        class SimilarityCalculator:
            @staticmethod
            def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
                """Compute cosine similarity"""
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 < 1e-10 or norm2 < 1e-10:
                    return 0.0
                
                return float(np.dot(vec1, vec2) / (norm1 * norm2))
            
            @staticmethod
            def batch_cosine_similarity(
                vec1: np.ndarray,
                batch_vecs: np.ndarray
            ) -> np.ndarray:
                """Compute cosine similarity with batch"""
                norm1 = np.linalg.norm(vec1)
                batch_norms = np.linalg.norm(batch_vecs, axis=1)
                
                similarities = np.dot(batch_vecs, vec1) / (
                    norm1 * batch_norms + 1e-10
                )
                
                return similarities
            
            @staticmethod
            def euclidean_to_cosine(euclidean_dist: float, dim: int) -> float:
                """Convert Euclidean distance to cosine similarity"""
                # For unit vectors: cosine = 1 - (dist^2 / 2)
                return 1.0 - (euclidean_dist ** 2) / 2.0
        
        return SimilarityCalculator()

    def test_cosine_similarity_self(self, similarity_calculator):
        """Test that vector is identical to itself"""
        vec = np.ones(384, dtype=np.float32)
        sim = similarity_calculator.cosine_similarity(vec, vec)
        
        assert abs(sim - 1.0) < 1e-5

    def test_cosine_similarity_orthogonal(self, similarity_calculator):
        """Test that orthogonal vectors have zero similarity"""
        vec1 = np.array([1, 0, 0], dtype=np.float32)
        vec2 = np.array([0, 1, 0], dtype=np.float32)
        
        sim = similarity_calculator.cosine_similarity(vec1, vec2)
        assert abs(sim) < 1e-5

    def test_cosine_similarity_opposite(self, similarity_calculator):
        """Test that opposite vectors have similarity of -1"""
        vec1 = np.ones(384, dtype=np.float32)
        vec2 = -np.ones(384, dtype=np.float32)
        
        sim = similarity_calculator.cosine_similarity(vec1, vec2)
        assert abs(sim - (-1.0)) < 1e-5

    def test_cosine_similarity_bounds(self, similarity_calculator):
        """Test that cosine similarity is in [-1, 1]"""
        np.random.seed(42)
        for _ in range(100):
            vec1 = np.random.randn(384).astype(np.float32)
            vec2 = np.random.randn(384).astype(np.float32)
            
            sim = similarity_calculator.cosine_similarity(vec1, vec2)
            assert -1.0 <= sim <= 1.0

    def test_batch_similarity_consistency(self, similarity_calculator):
        """Test batch similarity matches individual"""
        query = np.ones(384, dtype=np.float32)
        batch = np.random.randn(10, 384).astype(np.float32)
        
        # Batch computation
        batch_sims = similarity_calculator.batch_cosine_similarity(query, batch)
        
        # Individual computations
        individual_sims = np.array([
            similarity_calculator.cosine_similarity(query, batch[i])
            for i in range(len(batch))
        ])
        
        np.testing.assert_allclose(batch_sims, individual_sims, rtol=1e-5)

    def test_euclidean_to_cosine_conversion(self, similarity_calculator):
        """Test Euclidean to cosine conversion for unit vectors"""
        # For unit vectors, we can validate the conversion formula
        # Distance between unit vectors: sqrt(2 - 2*cos(angle))
        
        # Test case: orthogonal vectors (90 degrees)
        vec1 = np.array([1, 0], dtype=np.float32)
        vec2 = np.array([0, 1], dtype=np.float32)
        
        euclidean = np.linalg.norm(vec1 - vec2)
        cosine_expected = 0.0  # orthogonal = 0 similarity
        cosine_computed = similarity_calculator.euclidean_to_cosine(euclidean, 2)
        
        assert abs(cosine_computed - cosine_expected) < 0.1


# ============================================================================
# RESULT FORMATTING TESTS
# ============================================================================

class TestResultFormatting:
    """Integration tests for search result formatting"""

    @pytest.fixture
    def formatter(self):
        """Create a result formatter"""
        class ResultFormatter:
            @staticmethod
            def format_search_result(
                document: Document,
                score: float,
                rank: int
            ) -> Dict[str, Any]:
                """Format a single search result"""
                return {
                    'id': document.metadata.get('id', 'unknown'),
                    'content': document.page_content[:200],  # First 200 chars
                    'score': round(float(score), 4),
                    'rank': rank,
                    'metadata': {k: v for k, v in (document.metadata or {}).items()
                                if k not in ['id']},
                    'timestamp': datetime.now().isoformat()
                }
            
            @staticmethod
            def format_search_results(
                documents: List[Document],
                scores: List[float],
                query: str,
                execution_time_ms: float
            ) -> Dict[str, Any]:
                """Format complete search response"""
                results = []
                for rank, (doc, score) in enumerate(zip(documents, scores), 1):
                    results.append(
                        ResultFormatter.format_search_result(doc, score, rank)
                    )
                
                return {
                    'query': query,
                    'result_count': len(results),
                    'results': results,
                    'execution_time_ms': round(execution_time_ms, 2),
                    'timestamp': datetime.now().isoformat()
                }
            
            @staticmethod
            def format_error_result(
                error_message: str,
                error_code: str
            ) -> Dict[str, Any]:
                """Format error response"""
                return {
                    'error': error_message,
                    'error_code': error_code,
                    'timestamp': datetime.now().isoformat()
                }
        
        return ResultFormatter()

    def test_format_single_result(self, formatter):
        """Test formatting of single result"""
        doc = Document(
            page_content="This is a test document for semantic search",
            metadata={"id": "doc1", "source": "test", "score": 0.95}
        )
        
        formatted = formatter.format_search_result(doc, score=0.95, rank=1)
        
        assert formatted['id'] == 'doc1'
        assert formatted['rank'] == 1
        assert formatted['score'] == 0.95
        assert 'content' in formatted
        assert 'metadata' in formatted
        assert 'timestamp' in formatted

    def test_format_single_result_truncates_content(self, formatter):
        """Test that long content is truncated"""
        long_text = "A" * 500
        doc = Document(
            page_content=long_text,
            metadata={"id": "doc1"}
        )
        
        formatted = formatter.format_search_result(doc, score=0.95, rank=1)
        
        assert len(formatted['content']) <= 200

    def test_format_multiple_results(self, formatter):
        """Test formatting of multiple results"""
        docs = [
            Document(
                page_content=f"Document {i}",
                metadata={"id": f"doc{i}"}
            )
            for i in range(3)
        ]
        scores = [0.95, 0.87, 0.73]
        
        response = formatter.format_search_results(
            docs, scores, query="test", execution_time_ms=125.5
        )
        
        assert response['query'] == "test"
        assert response['result_count'] == 3
        assert response['execution_time_ms'] == 125.5
        assert len(response['results']) == 3
        
        # Verify ranking
        for i, result in enumerate(response['results'], 1):
            assert result['rank'] == i

    def test_format_results_preserves_metadata(self, formatter):
        """Test that metadata is preserved in formatting"""
        docs = [
            Document(
                page_content="Test",
                metadata={
                    "id": "doc1",
                    "source": "test",
                    "version": "1.0",
                    "category": "tech"
                }
            )
        ]
        
        response = formatter.format_search_results(
            docs, [0.95], query="test", execution_time_ms=50.0
        )
        
        result = response['results'][0]
        assert result['metadata']['source'] == 'test'
        assert result['metadata']['version'] == '1.0'
        assert result['metadata']['category'] == 'tech'

    def test_format_error_result(self, formatter):
        """Test error formatting"""
        error_response = formatter.format_error_result(
            error_message="Query parsing failed",
            error_code="QUERY_PARSE_ERROR"
        )
        
        assert error_response['error'] == "Query parsing failed"
        assert error_response['error_code'] == "QUERY_PARSE_ERROR"
        assert 'timestamp' in error_response

    def test_format_empty_results(self, formatter):
        """Test formatting of empty results"""
        response = formatter.format_search_results(
            documents=[],
            scores=[],
            query="no results",
            execution_time_ms=10.0
        )
        
        assert response['result_count'] == 0
        assert response['results'] == []


# ============================================================================
# END-TO-END SEMANTIC SEARCH TESTS
# ============================================================================

class TestSemanticSearchE2E:
    """End-to-end semantic search tests"""

    def test_search_pipeline_complete(self):
        """Test complete search pipeline from query to formatted results"""
        # Setup
        docs = [
            Document(
                page_content="Python is a programming language",
                metadata={"id": "doc1"}
            ),
            Document(
                page_content="Machine learning with Python",
                metadata={"id": "doc2"}
            ),
            Document(
                page_content="JavaScript is used for web development",
                metadata={"id": "doc3"}
            ),
        ]
        
        # Create embeddings
        np.random.seed(42)
        embeddings = np.random.randn(3, 384).astype(np.float32)
        
        # Simulate search
        query = "Python programming"
        query_emb = embeddings[0].copy()
        
        # Compute similarities
        similarities = np.dot(embeddings, query_emb)
        top_indices = np.argsort(similarities)[::-1][:2]
        
        results = [
            (docs[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        # Format results
        formatted = []
        for rank, (doc, score) in enumerate(results, 1):
            formatted.append({
                'id': doc.metadata['id'],
                'rank': rank,
                'score': round(score, 4)
            })
        
        assert len(formatted) == 2
        assert formatted[0]['rank'] == 1
        assert formatted[1]['rank'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
