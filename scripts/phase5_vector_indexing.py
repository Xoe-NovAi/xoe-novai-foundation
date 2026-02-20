#!/usr/bin/env python3
"""
Phase 5: Vector Indexing & Semantic Search Implementation

Chunks documents, embeds with sentence-transformers, indexes in Qdrant.
"""

import anyio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try imports with graceful fallbacks
try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks documents for embedding."""

    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        """Initialize chunker."""
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_document(self, content: str, metadata: Dict) -> List[Dict]:
        """
        Chunk a document into smaller pieces for embedding.

        Args:
            content: Document content
            metadata: Document metadata (service, source_url, etc.)

        Returns:
            List of chunk dicts with content and metadata
        """
        chunks = []

        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        current_chunk = ""
        chunk_num = 0

        for para in paragraphs:
            # Skip empty paragraphs
            if not para.strip():
                continue

            # If adding this para exceeds limit, save current chunk
            test_chunk = current_chunk + "\n\n" + para if current_chunk else para

            if len(test_chunk) > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunk_num += 1
                chunks.append(
                    {
                        "content": current_chunk.strip(),
                        "chunk_id": f"{metadata.get('source_url', 'unknown')}#{chunk_num}",
                        "metadata": {
                            **metadata,
                            "chunk_num": chunk_num,
                            "chunk_size": len(current_chunk),
                        },
                    }
                )

                # Start new chunk with overlap
                current_chunk = para
            else:
                current_chunk = test_chunk

        # Save final chunk
        if current_chunk.strip():
            chunk_num += 1
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "chunk_id": f"{metadata.get('source_url', 'unknown')}#{chunk_num}",
                    "metadata": {
                        **metadata,
                        "chunk_num": chunk_num,
                        "chunk_size": len(current_chunk),
                    },
                }
            )

        return chunks

    def chunk_all_documents(
        self, docs_dir: str = "knowledge/technical_manuals"
    ) -> List[Dict]:
        """Chunk all documents in a directory."""
        all_chunks = []
        docs_path = Path(docs_dir)

        if not docs_path.exists():
            logger.error(f"Documents directory not found: {docs_dir}")
            return []

        # Iterate through services
        for service_dir in sorted(docs_path.iterdir()):
            if not service_dir.is_dir():
                continue

            service_name = service_dir.name
            logger.info(f"Chunking {service_name}...")

            # Iterate through files in service
            for file_path in sorted(service_dir.glob("*.md")):
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    metadata = {
                        "service": service_name,
                        "source_url": str(file_path),
                        "file_name": file_path.name,
                        "scraped_at": "2026-02-16",  # From execution
                    }

                    chunks = self.chunk_document(content, metadata)
                    all_chunks.extend(chunks)

                    logger.debug(f"  - {file_path.name}: {len(chunks)} chunks")

                except Exception as e:
                    logger.error(f"Error chunking {file_path}: {e}")

        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


class VectorIndexer:
    """Embeds documents and indexes in Qdrant."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 32,
        qdrant_path: str = "./qdrant_storage",
    ):
        """Initialize indexer."""
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers not installed")
        if not HAS_QDRANT:
            raise ImportError("qdrant-client not installed")

        self.model_name = model_name
        self.batch_size = batch_size
        self.qdrant_path = qdrant_path

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device="cpu")

        logger.info(f"Initializing Qdrant client at {qdrant_path}")
        self.client = QdrantClient(path=qdrant_path)

        # Get model dimensions
        self.vector_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model embedding dimension: {self.vector_dim}")

    def embed_chunks(self, chunks: List[Dict]) -> List[Tuple[str, List[float]]]:
        """
        Embed all chunks.

        Args:
            chunks: List of chunk dicts with 'content' key

        Returns:
            List of (chunk_id, embedding) tuples
        """
        logger.info(f"Embedding {len(chunks)} chunks...")

        embeddings = []
        contents = [c["content"] for c in chunks]

        # Embed in batches
        for i in range(0, len(contents), self.batch_size):
            batch = contents[i : i + self.batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_numpy=True)

            for j, embedding in enumerate(batch_embeddings):
                chunk_id = chunks[i + j]["chunk_id"]
                embeddings.append((chunk_id, embedding.tolist()))

            if (i // self.batch_size + 1) % 5 == 0:
                logger.info(
                    f"  - Embedded {min(i + self.batch_size, len(contents))}/{len(contents)} chunks"
                )

        logger.info(f"Embedding complete: {len(embeddings)} vectors")
        return embeddings

    def create_collection(self, collection_name: str = "technical_manuals"):
        """Create Qdrant collection."""
        try:
            # Try to delete existing collection first
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")
        except:
            pass

        # Create new collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
        )

        logger.info(f"Created collection: {collection_name}")

    def index_vectors(
        self,
        chunks: List[Dict],
        embeddings: List[Tuple[str, List[float]]],
        collection_name: str = "technical_manuals",
    ):
        """Upload vectors and metadata to Qdrant."""
        logger.info(f"Indexing {len(embeddings)} vectors into Qdrant...")

        # Create points
        points = []
        for (chunk_id, embedding), chunk in zip(embeddings, chunks):
            point = PointStruct(
                id=hash(chunk_id) & 0x7FFFFFFF,  # Convert to positive int
                vector=embedding,
                payload={
                    "chunk_id": chunk_id,
                    "content": chunk["content"],
                    **chunk["metadata"],
                },
            )
            points.append(point)

        # Upload to Qdrant
        self.client.upsert(collection_name=collection_name, points=points)

        logger.info(f"Indexed {len(points)} vectors")

    def search(
        self, query: str, collection_name: str = "technical_manuals", top_k: int = 10
    ) -> List[Dict]:
        """Search for similar documents."""
        # Embed query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0].tolist()

        # Search in Qdrant
        results = self.client.search(
            collection_name=collection_name, query_vector=query_embedding, limit=top_k
        )

        return [
            {
                "score": result.score,
                "chunk_id": result.payload["chunk_id"],
                "service": result.payload["service"],
                "content": result.payload["content"][:200] + "...",
                "metadata": {
                    k: v
                    for k, v in result.payload.items()
                    if k not in ["content", "chunk_id"]
                },
            }
            for result in results
        ]


async def main():
    """Main Phase 5 execution."""
    logger.info("=" * 60)
    logger.info("PHASE 5: VECTOR INDEXING & SEMANTIC SEARCH")
    logger.info("=" * 60)

    # Check dependencies
    if not HAS_SENTENCE_TRANSFORMERS:
        logger.error(
            "sentence-transformers not installed. Run: pip install sentence-transformers"
        )
        return 1

    if not HAS_QDRANT:
        logger.error("qdrant-client not installed. Run: pip install qdrant-client")
        return 1

    try:
        # Phase 5a: Chunk documents
        logger.info("\n[Phase 5a] Chunking documents...")
        chunker = DocumentChunker(max_chunk_size=512)
        chunks = chunker.chunk_all_documents()

        if not chunks:
            logger.error("No chunks created!")
            return 1

        logger.info(f"Created {len(chunks)} chunks")

        # Phase 5b: Embed chunks
        logger.info("\n[Phase 5b] Embedding chunks...")
        indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", batch_size=32)
        embeddings = indexer.embed_chunks(chunks)

        # Phase 5c: Index in Qdrant
        logger.info("\n[Phase 5c] Indexing vectors...")
        indexer.create_collection("technical_manuals")
        indexer.index_vectors(chunks, embeddings, "technical_manuals")

        # Phase 5d & 5e: Test search
        logger.info("\n[Phase 5d & 5e] Testing semantic search...")
        test_queries = [
            "How do I configure Redis?",
            "FastAPI best practices",
            "Docker container networking",
            "Prometheus metrics configuration",
            "SQLAlchemy ORM tutorial",
        ]

        logger.info("Testing queries:")
        for query in test_queries:
            results = indexer.search(query, top_k=3)
            logger.info(f"\nQuery: '{query}'")
            for i, result in enumerate(results, 1):
                logger.info(
                    f"  {i}. [{result['service']}] Score: {result['score']:.3f}"
                )
                logger.info(f"     {result['content']}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ PHASE 5 COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Total chunks indexed: {len(chunks)}")
        logger.info(f"Qdrant storage: {indexer.qdrant_path}")
        logger.info("Ready for Phase 6: Testing & Documentation")

        return 0

    except Exception as e:
        logger.error(f"Phase 5 failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = anyio.run(main)
    exit(exit_code)
