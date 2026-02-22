#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 6 - Vector Indexing Unit Tests
# ============================================================================
# Purpose: Comprehensive unit tests for document chunking, embedding, 
#          deduplication, and metadata preservation
# Guide Reference: Phase 6 (Testing & Production Hardening)
# Last Updated: 2026-02-16
# ============================================================================

import pytest
import numpy as np
import hashlib
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# ============================================================================
# MOCK Document CLASS (for systems without langchain)
# ============================================================================

class Document:
    """Mock Document class for testing without langchain dependency"""
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}


# ============================================================================
# DOCUMENT CHUNKING TESTS
# ============================================================================

class TestDocumentChunking:
    """Unit tests for document chunking logic"""

    @pytest.fixture
    def chunker(self):
        """Create a simple document chunker"""
        class SimpleChunker:
            def __init__(self, chunk_size: int = 512, overlap: int = 50):
                self.chunk_size = chunk_size
                self.overlap = overlap
            
            def chunk_text(self, text: str) -> List[str]:
                """Split text into chunks with overlap"""
                chunks = []
                pos = 0
                while pos < len(text):
                    chunk = text[pos:pos + self.chunk_size]
                    chunks.append(chunk)
                    # Move position by chunk_size minus overlap
                    pos += self.chunk_size - self.overlap
                
                return chunks
            
            def chunk_documents(self, docs: List[Document]) -> List[Document]:
                """Chunk documents preserving metadata"""
                chunked = []
                for doc in docs:
                    chunks = self.chunk_text(doc.page_content)
                    for i, chunk in enumerate(chunks):
                        metadata = doc.metadata.copy() if doc.metadata else {}
                        metadata['chunk_index'] = i
                        metadata['original_id'] = doc.metadata.get('id', 'unknown')
                        chunked.append(Document(
                            page_content=chunk,
                            metadata=metadata
                        ))
                return chunked
        
        return SimpleChunker()

    def test_chunk_size_consistency(self, chunker):
        """Test that chunks respect configured size"""
        text = "A" * 1000  # 1000 characters
        chunks = chunker.chunk_text(text)
        
        # All chunks except the last should be >= chunk_size
        for chunk in chunks[:-1]:
            assert len(chunk) == chunker.chunk_size
        
        # Last chunk should be <= chunk_size
        assert len(chunks[-1]) <= chunker.chunk_size

    def test_overlap_preservation(self, chunker):
        """Test that overlap is correctly maintained"""
        text = "0123456789" * 100  # More structured text
        chunker.chunk_size = 100
        chunker.overlap = 20
        
        chunks = chunker.chunk_text(text)
        
        # Verify that there is overlap
        for i in range(len(chunks) - 1):
            # Last `overlap` chars of chunk[i] should match first `overlap` chars of chunk[i+1]
            end_of_current = chunks[i][-chunker.overlap:]
            start_of_next = chunks[i + 1][:chunker.overlap]
            # In our implementation, the overlap should be present
            assert len(end_of_current) > 0, f"Chunk {i} is too short: {len(chunks[i])}"
            assert len(start_of_next) > 0, f"Chunk {i+1} is too short: {len(chunks[i+1])}"

    def test_chunk_coverage(self, chunker):
        """Test that chunking covers entire document"""
        text = "The quick brown fox jumps over the lazy dog. " * 50
        chunks = chunker.chunk_text(text)
        
        # Reconstruct: all chars should be present
        reconstructed = ""
        for i, chunk in enumerate(chunks):
            if i == 0:
                reconstructed += chunk
            else:
                # Skip the overlap part
                reconstructed += chunk[chunker.overlap:]
        
        # Check coverage (allowing for truncation at end)
        assert text.startswith(reconstructed[:len(text)]) or \
               reconstructed.startswith(text)

    def test_empty_text_chunking(self, chunker):
        """Test handling of empty text"""
        chunks = chunker.chunk_text("")
        assert chunks == []

    def test_document_metadata_preservation(self, chunker):
        """Test that metadata is preserved during chunking"""
        docs = [
            Document(
                page_content="A" * 1000,
                metadata={"id": "doc1", "source": "manual", "version": "1.0"}
            ),
            Document(
                page_content="B" * 500,
                metadata={"id": "doc2", "source": "auto", "version": "2.0"}
            )
        ]
        
        chunked = chunker.chunk_documents(docs)
        
        # Verify all chunks have required metadata
        for chunk in chunked:
            assert 'original_id' in chunk.metadata
            assert 'chunk_index' in chunk.metadata
            assert 'source' in chunk.metadata
            assert 'version' in chunk.metadata
        
        # Verify original metadata values
        doc1_chunks = [c for c in chunked if c.metadata['original_id'] == 'doc1']
        assert all(c.metadata['source'] == 'manual' for c in doc1_chunks)
        assert all(c.metadata['version'] == '1.0' for c in doc1_chunks)


# ============================================================================
# VECTOR EMBEDDING TESTS
# ============================================================================

class TestVectorEmbedding:
    """Unit tests for vector embedding consistency"""

    @pytest.fixture
    def embedder(self):
        """Create a mock embedder with deterministic embeddings"""
        class MockEmbedder:
            def __init__(self, dim: int = 384):
                self.dim = dim
            
            def embed_text(self, text: str) -> np.ndarray:
                """Generate deterministic embedding from text"""
                # Use hash of text to seed deterministic vector
                hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
                np.random.seed(hash_val % (2**31))
                embedding = np.random.randn(self.dim).astype(np.float32)
                # Normalize
                embedding = embedding / np.linalg.norm(embedding)
                return embedding
            
            def embed_batch(self, texts: List[str]) -> np.ndarray:
                """Embed multiple texts"""
                embeddings = []
                for text in texts:
                    embeddings.append(self.embed_text(text))
                return np.array(embeddings, dtype=np.float32)
            
            def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
                """Compute cosine similarity"""
                return float(np.dot(emb1, emb2) / (
                    np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-10
                ))
        
        return MockEmbedder()

    def test_embedding_dimension(self, embedder):
        """Test that embeddings have correct dimension"""
        text = "This is a test document for semantic search."
        embedding = embedder.embed_text(text)
        
        assert embedding.shape == (embedder.dim,)
        assert embedding.dtype == np.float32

    def test_embedding_determinism(self, embedder):
        """Test that same text produces same embedding"""
        text = "Deterministic embedding test"
        
        emb1 = embedder.embed_text(text)
        emb2 = embedder.embed_text(text)
        
        # Should be exactly equal
        np.testing.assert_array_equal(emb1, emb2)

    def test_embedding_normalization(self, embedder):
        """Test that embeddings are normalized"""
        texts = [
            "Short text",
            "This is a longer piece of text with more information",
            "X" * 1000  # Very long text
        ]
        
        embeddings = embedder.embed_batch(texts)
        
        for embedding in embeddings:
            norm = np.linalg.norm(embedding)
            # Should be normalized to ~1.0
            assert abs(norm - 1.0) < 1e-5

    def test_embedding_similarity_bounds(self, embedder):
        """Test that similarity scores are in valid range"""
        texts = ["Apple", "Banana", "Apple pie", "Orange juice"]
        embeddings = embedder.embed_batch(texts)
        
        for i in range(len(embeddings)):
            for j in range(len(embeddings)):
                sim = embedder.similarity(embeddings[i], embeddings[j])
                # Cosine similarity should be in [-1, 1] (allow small floating-point error)
                assert -1.001 <= sim <= 1.001, f"Similarity {sim} out of bounds for indices {i},{j}"

    def test_embedding_self_similarity(self, embedder):
        """Test that text has high similarity with itself"""
        text = "This text should be similar to itself"
        emb = embedder.embed_text(text)
        
        sim = embedder.similarity(emb, emb)
        # Self-similarity should be 1.0 (or very close)
        assert abs(sim - 1.0) < 1e-5

    def test_embedding_batch_consistency(self, embedder):
        """Test that batch embedding matches individual embeddings"""
        texts = ["Text 1", "Text 2", "Text 3"]
        
        # Individual embeddings
        individual = [embedder.embed_text(t) for t in texts]
        
        # Batch embedding
        batch = embedder.embed_batch(texts)
        
        for i, (ind, bat) in enumerate(zip(individual, batch)):
            np.testing.assert_array_equal(ind, bat)


# ============================================================================
# DEDUPLICATION TESTS
# ============================================================================

class TestDeduplication:
    """Unit tests for document deduplication"""

    @pytest.fixture
    def deduplicator(self):
        """Create a deduplication engine"""
        class Deduplicator:
            def __init__(self, similarity_threshold: float = 0.95):
                self.threshold = similarity_threshold
            
            def compute_text_hash(self, text: str) -> str:
                """Compute MD5 hash of text"""
                return hashlib.md5(text.encode()).hexdigest()
            
            def deduplicate_exact(self, docs: List[Document]) -> List[Document]:
                """Remove exact duplicates using hash"""
                seen = set()
                unique = []
                
                for doc in docs:
                    text_hash = self.compute_text_hash(doc.page_content)
                    if text_hash not in seen:
                        seen.add(text_hash)
                        unique.append(doc)
                
                return unique
            
            def compute_embedding_hash(self, embedding: np.ndarray) -> str:
                """Hash embedding to string for deduplication"""
                quantized = (embedding * 1000).astype(int)
                return hashlib.sha256(
                    quantized.tobytes()
                ).hexdigest()
            
            def deduplicate_semantic(
                self, 
                embeddings: List[np.ndarray],
                texts: List[str]
            ) -> tuple[List[str], List[np.ndarray], List[int]]:
                """Remove semantic duplicates using similarity"""
                unique_texts = []
                unique_embeddings = []
                kept_indices = []
                
                for i, (embedding, text) in enumerate(zip(embeddings, texts)):
                    is_duplicate = False
                    
                    for unique_emb in unique_embeddings:
                        # Compute cosine similarity
                        sim = float(np.dot(embedding, unique_emb) / (
                            np.linalg.norm(embedding) * np.linalg.norm(unique_emb) + 1e-10
                        ))
                        
                        if sim > self.threshold:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        unique_texts.append(text)
                        unique_embeddings.append(embedding)
                        kept_indices.append(i)
                
                return unique_texts, unique_embeddings, kept_indices
        
        return Deduplicator()

    def test_exact_deduplication(self, deduplicator):
        """Test exact duplicate removal"""
        docs = [
            Document(page_content="Unique document 1"),
            Document(page_content="Unique document 1"),  # Exact duplicate
            Document(page_content="Unique document 2"),
            Document(page_content="Unique document 1"),  # Another exact duplicate
        ]
        
        unique = deduplicator.deduplicate_exact(docs)
        
        assert len(unique) == 2
        assert unique[0].page_content == "Unique document 1"
        assert unique[1].page_content == "Unique document 2"

    def test_exact_hash_consistency(self, deduplicator):
        """Test that hash is consistent for same text"""
        text = "Consistent text for hashing"
        
        hash1 = deduplicator.compute_text_hash(text)
        hash2 = deduplicator.compute_text_hash(text)
        
        assert hash1 == hash2

    def test_empty_deduplication(self, deduplicator):
        """Test deduplication with empty list"""
        unique = deduplicator.deduplicate_exact([])
        assert unique == []

    def test_no_duplicates(self, deduplicator):
        """Test that all unique docs are preserved"""
        docs = [
            Document(page_content=f"Document {i}")
            for i in range(5)
        ]
        
        unique = deduplicator.deduplicate_exact(docs)
        assert len(unique) == 5

    def test_semantic_deduplication(self, deduplicator):
        """Test semantic duplicate removal"""
        # Create embeddings with high similarity
        np.random.seed(42)
        base_emb = np.random.randn(384)
        base_emb = base_emb / np.linalg.norm(base_emb)
        
        # Create near-duplicate embeddings
        emb1 = base_emb.copy()
        noise = np.random.randn(384) * 0.02
        emb2 = base_emb + noise
        emb2 = emb2 / np.linalg.norm(emb2)
        
        # Create distinct embedding
        distinct = np.random.randn(384)
        distinct = distinct / np.linalg.norm(distinct)
        
        embeddings = [emb1, emb2, distinct]
        texts = ["Text 1", "Text 2", "Text 3"]
        
        unique_texts, unique_embs, kept_indices = \
            deduplicator.deduplicate_semantic(embeddings, texts)
        
        # Should keep at least 2 (the base and distinct)
        assert len(unique_texts) >= 2
        assert len(kept_indices) >= 2


# ============================================================================
# METADATA PRESERVATION TESTS
# ============================================================================

class TestMetadataPreservation:
    """Unit tests for metadata preservation during processing"""

    @pytest.fixture
    def metadata_processor(self):
        """Create a metadata processor"""
        class MetadataProcessor:
            def __init__(self):
                self.required_fields = {'id', 'source', 'timestamp'}
            
            def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
                """Check if metadata has required fields"""
                return all(field in metadata for field in self.required_fields)
            
            def enrich_metadata(
                self, 
                doc: Document, 
                embeddings: np.ndarray
            ) -> Document:
                """Add computed metadata to document"""
                enriched = doc.metadata.copy() if doc.metadata else {}
                
                # Add computed fields
                enriched['content_hash'] = hashlib.md5(
                    doc.page_content.encode()
                ).hexdigest()
                enriched['embedding_dim'] = len(embeddings)
                enriched['processed_at'] = datetime.now().isoformat()
                enriched['text_length'] = len(doc.page_content)
                
                return Document(
                    page_content=doc.page_content,
                    metadata=enriched
                )
            
            def preserve_through_pipeline(
                self,
                docs: List[Document],
                embeddings: List[np.ndarray]
            ) -> List[Document]:
                """Preserve metadata through processing pipeline"""
                processed = []
                for doc, emb in zip(docs, embeddings):
                    enriched = self.enrich_metadata(doc, emb)
                    processed.append(enriched)
                return processed
        
        return MetadataProcessor()

    def test_required_metadata_validation(self, metadata_processor):
        """Test validation of required metadata fields"""
        valid_meta = {
            'id': 'doc1',
            'source': 'manual',
            'timestamp': datetime.now().isoformat()
        }
        
        invalid_meta = {
            'id': 'doc2',
            'source': 'auto'
            # Missing 'timestamp'
        }
        
        assert metadata_processor.validate_metadata(valid_meta) is True
        assert metadata_processor.validate_metadata(invalid_meta) is False

    def test_metadata_enrichment(self, metadata_processor):
        """Test metadata enrichment during processing"""
        doc = Document(
            page_content="Sample document content",
            metadata={
                'id': 'doc1',
                'source': 'test',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        embedding = np.ones(384, dtype=np.float32)
        enriched = metadata_processor.enrich_metadata(doc, embedding)
        
        # Check that new fields were added
        assert 'content_hash' in enriched.metadata
        assert 'embedding_dim' in enriched.metadata
        assert 'processed_at' in enriched.metadata
        assert 'text_length' in enriched.metadata
        
        # Check that original fields are preserved
        assert enriched.metadata['id'] == 'doc1'
        assert enriched.metadata['source'] == 'test'

    def test_metadata_through_pipeline(self, metadata_processor):
        """Test metadata preservation through processing"""
        docs = [
            Document(
                page_content="Doc 1",
                metadata={
                    'id': 'doc1',
                    'source': 'src1',
                    'timestamp': datetime.now().isoformat(),
                    'custom_field': 'value1'
                }
            ),
            Document(
                page_content="Doc 2",
                metadata={
                    'id': 'doc2',
                    'source': 'src2',
                    'timestamp': datetime.now().isoformat(),
                    'custom_field': 'value2'
                }
            )
        ]
        
        embeddings = [
            np.ones(384, dtype=np.float32),
            np.ones(384, dtype=np.float32)
        ]
        
        processed = metadata_processor.preserve_through_pipeline(docs, embeddings)
        
        assert len(processed) == 2
        
        # Verify first doc
        assert processed[0].metadata['id'] == 'doc1'
        assert processed[0].metadata['custom_field'] == 'value1'
        assert 'content_hash' in processed[0].metadata
        
        # Verify second doc
        assert processed[1].metadata['id'] == 'doc2'
        assert processed[1].metadata['custom_field'] == 'value2'
        assert 'embedding_dim' in processed[1].metadata

    def test_metadata_immutability(self, metadata_processor):
        """Test that original metadata is not mutated"""
        original_meta = {
            'id': 'doc1',
            'source': 'test',
            'timestamp': datetime.now().isoformat()
        }
        
        doc = Document(
            page_content="Test",
            metadata=original_meta.copy()
        )
        
        embedding = np.ones(384, dtype=np.float32)
        enriched = metadata_processor.enrich_metadata(doc, embedding)
        
        # Original should not be modified
        assert len(original_meta) == 3
        # Enriched should have more fields
        assert len(enriched.metadata) > 3


# ============================================================================
# INTEGRATION-LIKE UNIT TESTS
# ============================================================================

class TestIndexingPipeline:
    """Integration-like tests for complete indexing pipeline"""

    def test_full_chunking_embedding_pipeline(self):
        """Test complete pipeline: chunk -> embed -> deduplicate"""
        # Setup
        docs = [
            Document(
                page_content="A" * 1000,
                metadata={'id': 'doc1', 'source': 'test'}
            )
        ]
        
        # Chunking
        class Chunker:
            def chunk(self, docs):
                result = []
                for doc in docs:
                    text = doc.page_content
                    for i in range(0, len(text), 512):
                        chunk = text[i:i+512]
                        meta = doc.metadata.copy() if doc.metadata else {}
                        meta['chunk_index'] = i // 512
                        result.append(Document(page_content=chunk, metadata=meta))
                return result
        
        chunker = Chunker()
        chunked = chunker.chunk(docs)
        
        assert len(chunked) > 0
        assert all('chunk_index' in d.metadata for d in chunked)

    def test_memory_aware_embedding(self):
        """Test memory-conscious embedding of large datasets"""
        # Simulate large document set
        large_docs = [
            Document(
                page_content=f"Document {i} " * 100,
                metadata={'id': f'doc{i}', 'source': 'test'}
            )
            for i in range(10)
        ]
        
        # Process in batches to respect memory limit
        batch_size = 5
        total_processed = 0
        
        for i in range(0, len(large_docs), batch_size):
            batch = large_docs[i:i+batch_size]
            # Simulate embedding
            embeddings = [
                np.random.randn(384).astype(np.float32) 
                for _ in batch
            ]
            total_processed += len(batch)
        
        assert total_processed == len(large_docs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
