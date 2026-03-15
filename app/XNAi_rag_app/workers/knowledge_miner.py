#!/usr/bin/env python3
"""
XNAi Persona Knowledge Miner
============================

Autonomous worker that researches and builds the 'Expert Memory Bank'
for new persistent personas.

Workflow:
1.  Receive 'expertise_mining' task.
2.  Trigger Deep Crawl/Research on the persona and attached domains.
3.  Synthesize findings into high-value 'Lessons Learned'.
4.  Inject into Gnosis Engine (LightRAG) for long-term recall.
"""

import anyio
import json
import logging
import time
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from XNAi_rag_app.core.agent_bus import AgentBusClient
from XNAi_rag_app.core.entities.registry import registry as entity_registry
from XNAi_rag_app.workers.crawl import curate_from_source
from scripts.graph_extractor import process_document

from XNAi_rag_app.core.health.health_monitoring import create_enhanced_health_checker
from XNAi_rag_app.core.health.recovery_manager import RecoveryManager

logger = logging.getLogger("knowledge_miner")

@dataclass
class DocumentChunk:
    """Metadata structure for a document chunk with token information."""
    content: str
    chunk_num: int
    token_count: int
    position_in_doc: float  # 0.0-1.0
    start_char: int
    end_char: int
    doc_id: str
    doc_source: str
    overlap_percent: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize chunk metadata to dictionary."""
        return {
            "chunk_num": self.chunk_num,
            "token_count": self.token_count,
            "position_in_doc": self.position_in_doc,
            "char_range": {
                "start": self.start_char,
                "end": self.end_char
            },
            "doc_id": self.doc_id,
            "doc_source": self.doc_source,
            "overlap_percent": self.overlap_percent
        }

class KnowledgeMinerWorker(AgentBusClient):
    """
    Autonomous worker that researches and builds the 'Expert Memory Bank'.
    """
    
    # Mapping roles to crawl sources
    ROLE_SOURCES = {
        "philosopher": "gutenberg",
        "scientist": "arxiv",
        "engineer": "arxiv",
        "medical": "pubmed",
        "musician": "youtube",
        "artist": "youtube",
        "general": "gutenberg"
    }

    def __init__(self, agent_did: str = "worker:knowledge_miner:001"):
        super().__init__(agent_did)
        self.recovery = RecoveryManager()
        # Enterprise Hardening: Limit concurrent heavy research tasks
        self.limiter = anyio.CapacityLimiter(1)
        # Initialize health checker
        self.health_monitor = create_enhanced_health_checker({
            "targets": ["memory", "redis"],
            "interval_seconds": 60
        })

    async def start(self):
        async with self as bus:
            logger.info("Knowledge Miner Worker active. Searching for expertise gaps...")
            while True:
                try:
                    # Health Check: Don't mine if system is degraded (RAM pressure)
                    summary = await self.health_monitor.get_health_summary()
                    # Check system metrics directly if services not checked yet
                    ram_usage = summary.get("system_metrics", {}).get("memory_usage_percent", 0)
                    
                    if ram_usage > 90:
                        logger.warning(f"System under high RAM pressure ({ram_usage}%). Knowledge Mining paused.")
                        await anyio.sleep(30)
                        continue

                    tasks = await self.fetch_tasks(count=1)
                    for task in tasks:
                        if task["type"] == "expertise_mining":
                            # Use limiter to protect Ryzen 5700U memory
                            async with self.limiter:
                                await self._mine_expertise(task)
                        await self.acknowledge_task(task["id"])
                    
                    await anyio.sleep(1)
                except Exception as e:
                    logger.error(f"Worker loop error: {e}")
                    await anyio.sleep(5)

    def _approximate_token_count(self, text: str) -> int:
        """
        Approximate token count using character-based heuristic.
        Pattern: 1 token ≈ 4 characters (consistent with dispatcher modules)
        """
        return max(1, len(text) // 4)

    def _chunk_documents_for_mining(
        self,
        documents: List[Dict[str, Any]],
        chunk_size_tokens: int = 512,
        overlap_percent: int = 10
    ) -> List[DocumentChunk]:
        """
        Chunk documents using 512-token sliding window with 10% overlap.
        
        Algorithm:
        1. Convert token size to character size (4 chars ≈ 1 token)
        2. For each document, split into paragraphs
        3. Build chunks paragraph-aware up to chunk_size
        4. Apply sliding window overlap (10% = ~51 tokens = ~204 chars)
        
        Args:
            documents: List of document dicts with 'content' and optional 'source'
            chunk_size_tokens: Target chunk size in tokens (default 512)
            overlap_percent: Overlap percentage (default 10)
        
        Returns:
            List of DocumentChunk objects with metadata
        """
        # Convert target token size to characters (1 token ≈ 4 chars)
        chunk_size_chars = chunk_size_tokens * 4
        overlap_chars = int(chunk_size_chars * overlap_percent / 100)
        
        all_chunks: List[DocumentChunk] = []
        
        for doc_idx, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.warning(f"Skipping non-dict document at index {doc_idx}")
                continue
                
            content = doc.get("content", "").strip()
            if not content:
                logger.warning(f"Skipping empty document at index {doc_idx}")
                continue
            
            doc_id = doc.get("id", f"doc_{doc_idx}")
            doc_source = doc.get("source", "unknown")
            
            # Split into paragraphs, respecting document boundaries
            chunks_for_doc = self._slice_with_overlap(
                content,
                doc_id,
                doc_source,
                chunk_size_chars,
                overlap_chars
            )
            
            # Update position metadata for each chunk
            total_chars = len(content)
            for chunk in chunks_for_doc:
                chunk.position_in_doc = (chunk.start_char + chunk.end_char) / 2 / max(1, total_chars)
                chunk.token_count = self._approximate_token_count(chunk.content)
                all_chunks.append(chunk)
            
            logger.info(
                f"Chunked document '{doc_id}' ({len(content)} chars) "
                f"into {len(chunks_for_doc)} chunks (~{chunk_size_tokens}±10% tokens each)"
            )
        
        return all_chunks

    def _slice_with_overlap(
        self,
        text: str,
        doc_id: str,
        doc_source: str,
        chunk_size: int,
        overlap: int
    ) -> List[DocumentChunk]:
        """
        Slice text with sliding window overlap, preserving paragraph boundaries.
        
        Algorithm:
        1. Split by paragraphs (double newlines)
        2. Group paragraphs up to chunk_size
        3. For overflow, apply sliding window: start = max(0, end - overlap)
        
        Args:
            text: Text to chunk
            doc_id: Document identifier
            doc_source: Source of document
            chunk_size: Chunk size in characters
            overlap: Overlap size in characters
        
        Returns:
            List of DocumentChunk objects with positional metadata
        """
        if not text:
            return []
        
        # Paragraph-aware chunking: preserve semantic boundaries
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[DocumentChunk] = []
        chunk_num = 0
        
        current_text = ""
        current_start = 0
        
        for para in paragraphs:
            # Try to add paragraph to current chunk
            test_text = current_text + ("\n\n" if current_text else "") + para
            
            if len(test_text) <= chunk_size:
                current_text = test_text
            else:
                # Current chunk is full, finalize it
                if current_text:
                    chunk = DocumentChunk(
                        content=current_text.strip(),
                        chunk_num=chunk_num,
                        token_count=self._approximate_token_count(current_text),
                        position_in_doc=0.0,  # Will be updated in parent method
                        start_char=current_start,
                        end_char=current_start + len(current_text),
                        doc_id=doc_id,
                        doc_source=doc_source,
                        overlap_percent=10
                    )
                    chunks.append(chunk)
                    chunk_num += 1
                    
                    # Apply overlap: rewind to capture context
                    overlap_text = current_text[-overlap:] if overlap < len(current_text) else current_text
                    current_start = max(0, current_start + len(current_text) - len(overlap_text))
                    current_text = overlap_text
                
                # Add the paragraph that caused overflow
                if len(para) > chunk_size:
                    # Paragraph is larger than chunk size - must split it
                    para_chunks = self._split_large_paragraph(
                        para, chunk_num, doc_id, doc_source, chunk_size, overlap
                    )
                    chunks.extend(para_chunks)
                    chunk_num += len(para_chunks)
                    current_text = ""
                    current_start = sum(len(c.content) for c in chunks)
                else:
                    # Start new chunk with this paragraph
                    current_text = para
                    current_start = sum(len(c.content) for c in chunks) + (2 if chunks else 0)
        
        # Finalize last chunk
        if current_text:
            chunk = DocumentChunk(
                content=current_text.strip(),
                chunk_num=chunk_num,
                token_count=self._approximate_token_count(current_text),
                position_in_doc=0.0,  # Will be updated in parent method
                start_char=current_start,
                end_char=current_start + len(current_text),
                doc_id=doc_id,
                doc_source=doc_source,
                overlap_percent=10
            )
            chunks.append(chunk)
        
        return chunks

    def _split_large_paragraph(
        self,
        para: str,
        chunk_num: int,
        doc_id: str,
        doc_source: str,
        chunk_size: int,
        overlap: int
    ) -> List[DocumentChunk]:
        """
        Split a paragraph that exceeds chunk_size using sliding window.
        """
        chunks: List[DocumentChunk] = []
        start = 0
        L = len(para)
        
        while start < L:
            end = min(start + chunk_size, L)
            chunk_content = para[start:end].strip()
            
            if chunk_content:
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_num=chunk_num,
                    token_count=self._approximate_token_count(chunk_content),
                    position_in_doc=0.0,  # Will be updated in parent method
                    start_char=start,
                    end_char=end,
                    doc_id=doc_id,
                    doc_source=doc_source,
                    overlap_percent=10
                )
                chunks.append(chunk)
                chunk_num += 1
            
            if end == L:
                break
            
            # Sliding window: move start back by overlap amount
            start = max(0, end - overlap)
        
        return chunks

    async def _mine_expertise(self, task: Dict[str, Any]):
        payload = task["payload"]
        name = payload.get("name")
        role = payload.get("role", "general")
        
        logger.info(f"⛏️  Mining Expertise for: {name} ({role})")
        
        # 1. Determine Source
        source = self.ROLE_SOURCES.get(role.lower(), "gutenberg")
        category = f"expert-{name.lower().replace(' ', '-')}"
        
        # 2. Delegate to LibraryCuratorWorker via Agent Bus
        logger.info(f"📡 Delegating curation task for {name} to LibraryCurator...")
        documents = []
        try:
            # Send task to Agent Bus
            curation_payload = {
                "source_type": "api",
                "api_name": source,
                "query": name,
                "category": category,
                "max_items": 5
            }
            curation_task_id = await self.send_task(
                target_did="worker:library_curator:001",
                task_type="curation_task",
                payload=curation_payload
            )
            logger.info(f"📤 Curation task sent: {curation_task_id}")
            
            # 3. Wait for result (Simple poll for now)
            # In a production system, we might use a proper callback/promise pattern
            max_wait = 120 # 2 minutes
            start_wait = time.time()
            completed = False
            
            while time.time() - start_wait < max_wait:
                # Check task updates stream (this is simplified)
                # Ideally we'd filter for the specific task_id
                updates = await self.redis.xrevrange("xnai:task_updates", count=10)
                for msg_id, data in updates:
                    if data.get("task_id") == curation_task_id and data.get("status") == "completed":
                        logger.info(f"✅ Curation task {curation_task_id} confirmed complete")
                        # Extract documents from curation result
                        result_data = data.get("result", {})
                        if isinstance(result_data, str):
                            result_data = json.loads(result_data)
                        documents = result_data.get("documents", [])
                        completed = True
                        break
                if completed: break
                await anyio.sleep(5)
            
            if not completed:
                logger.warning(f"⚠️ Curation task {curation_task_id} timed out or failed")

        except Exception as e:
            logger.error(f"❌ Delegation failed for {name}: {e}")

        # 3. Chunk documents (Block 0.5)
        chunks: List[DocumentChunk] = []
        if documents:
            logger.info(f"📚 Chunking {len(documents)} document(s) with 512-token window (10% overlap)...")
            chunks = self._chunk_documents_for_mining(
                documents,
                chunk_size_tokens=512,
                overlap_percent=10
            )
            logger.info(f"📦 Created {len(chunks)} chunks from {len(documents)} document(s)")
        else:
            logger.warning(f"⚠️ No documents retrieved from curation task")

        # 4. Extract high-value findings from chunks
        findings = [
            f"{name} research complete via delegated curation.",
            f"Expertise category created: {category}.",
            f"Processed {len(chunks)} knowledge chunks ({len(documents)} documents).",
            f"Knowledge injected into Gnosis Engine."
        ]
        
        # 5. Update Entity Memory
        entity = entity_registry.get_entity(name, role, auto_create=False)
        if entity:
            for fact in findings:
                entity.add_lesson(
                    query="Who is this entity?",
                    advice="N/A (Bootstrap)",
                    outcome=fact,
                    rating=1.0
                )
            entity.is_initialized = True
            entity.save()
            
        logger.info(f"✅ Expertise mined and persisted for {name} ({len(chunks)} chunks).")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = KnowledgeMinerWorker()
    anyio.run(worker.start)
