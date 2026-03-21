#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 1 v0.1.4-stable - Library Ingestion System (ENTERPRISE-GRADE)
# ============================================================================
# Purpose: Enterprise-grade content ingestion from APIs, RSS feeds, and local sources
# Guide Reference: Section 4.4 (Library Ingestion Pipeline)
# Last Updated: 2026-03-09 (SI1 Qdrant-First Storage + Insecure TLS Fix)
# ============================================================================

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import hashlib
import re
import urllib.parse
from collections import defaultdict, Counter
import anyio

# Third-party imports (with graceful fallbacks)
try:
    import feedparser
    _HAS_FEEDPARSER = True
except ImportError:
    feedparser = None
    _HAS_FEEDPARSER = False

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    requests = None
    _HAS_REQUESTS = False

try:
    import magic
    _HAS_MAGIC = True
except ImportError:
    magic = None
    _HAS_MAGIC = False

# Local imports
from XNAi_rag_app.core.config_loader import load_config, get_config_value
from XNAi_rag_app.core.dependencies import get_embeddings, get_vectorstore, get_redis_client, get_vectorstore_async
from XNAi_rag_app.services.library_api_integrations import LibraryEnrichmentEngine, DomainCategory
from XNAi_rag_app.core.logging_config import setup_logging, get_logger, PerformanceLogger
from XNAi_rag_app.core.infrastructure.resource_hub import ResourceHub
from XNAi_rag_app.core.xnai_zram_monitor import wait_for_resource_availability

# Setup logging
setup_logging()
logger = get_logger(__name__)
perf_logger = PerformanceLogger(logger)

# Load configuration
CONFIG = load_config()

@dataclass
class ScholarlyMetadata:
    isbn: Optional[str] = None
    doi: Optional[str] = None
    issn: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    era: Optional[str] = None
    genre: Optional[str] = None

@dataclass
class ContentMetadata:
    source: str
    source_url: str
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    content_type: str = 'text'
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    language: str = 'en'
    tags: List[str] = field(default_factory=list)
    ingestion_timestamp: Optional[str] = None
    last_modified: Optional[str] = None
    quality_score: float = 0.0
    scholarly: Optional[ScholarlyMetadata] = None
    summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {k: v for k, v in self.__dict__.items() if k != 'scholarly'}
        if self.scholarly:
            result['scholarly'] = {k: v for k, v in self.scholarly.__dict__.items()}
        return result

@dataclass
class IngestionStats:
    total_processed: int = 0
    total_ingested: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    duplicates_found: int = 0
    api_calls_made: int = 0
    rss_feeds_processed: int = 0
    files_processed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    processing_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class ScholarlyTextCurator:
    def curate(self, content: str, metadata: ContentMetadata) -> ContentMetadata:
        return metadata

class EnterpriseIngestionEngine:
    """
    Enterprise-grade content ingestion engine with SI1 Ollama integration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or CONFIG
        self.redis_client = get_redis_client()
        self.enrichment_engine = LibraryEnrichmentEngine()
        self.scholarly_curator = ScholarlyTextCurator()
        self.resource_hub = ResourceHub()
        self.embeddings = None
        self.vectorstore = None
        self.processed_checksums: Set[str] = set()
        self.last_api_call = 0
        self.api_call_interval = 1.0
        self.min_quality_score = 0.4
        self.min_content_length = 100
        self.magic = magic if _HAS_MAGIC else None
        self.supported_extensions = {
            'text': ['.md', '.txt', '.rst'],
            'pdf': ['.pdf'],
            'audio': ['.mp3', '.wav']
        }

    def _calculate_checksum(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def _summarize_content(self, content: str, title: str) -> Dict[str, Any]:
        """SI1: Summarize content using Ollama API (host-local)."""
        try:
            # Fixed gateway IP for Ollama access from internal bridge
            api_url = os.getenv("LLM_API_URL", "http://10.89.0.1:11434/v1/chat/completions")
            model = os.getenv("LLM_MODEL_NAME", "qwen2.5:0.5b")
            
            truncated = content[:2000]
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Summarize text briefly and extract 5 keywords. Output JSON."},
                    {"role": "user", "content": f"Title: {title}\nText: {truncated}"}
                ],
                "response_format": {"type": "json_object"}
            }
            
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                content_resp = data['choices'][0]['message']['content']
                
                if "{" in content_resp:
                    json_str = content_resp[content_resp.find("{"):content_resp.rfind("}")+1]
                    return json.loads(json_str)
                return {"summary": content_resp[:200], "keywords": []}
                    
        except Exception as e:
            logger.warning(f"Ollama summarization failed: {e}")
            return {"summary": "Summarization unavailable", "keywords": []}

    def _is_duplicate(self, checksum: str) -> bool:
        if checksum in self.processed_checksums: return True
        try:
            cache_key = f"ingestion:checksum:{checksum}"
            return self.redis_client.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}")
            return False

    def _cache_processed_checksum(self, checksum: str):
        self.processed_checksums.add(checksum)
        try:
            cache_key = f"ingestion:checksum:{checksum}"
            self.redis_client.setex(cache_key, 86400 * 30, "1")
        except Exception as e:
            logger.error(f"Checksum caching failed: {e}")

    async def ingest_from_api(self, api_name: str, query: str, max_items: int = 50) -> IngestionStats:
        stats = IngestionStats()
        stats.start_time = time.time()
        try:
            # 🔱 RESOURCE HARDENING GATE
            await wait_for_resource_availability()
            
            api_client = self.enrichment_engine.get_api_client(api_name)
            if not api_client: raise ValueError(f"Unknown API: {api_name}")
            results = await anyio.to_thread.run_sync(lambda: api_client.search(query, max_results=max_items))
            for result in results:
                stats.total_processed += 1
                metadata = ContentMetadata(
                    source=f'api_{api_name}',
                    source_url=result.get('url') or '',
                    title=result.get('title', 'Unknown'),
                    content=result.get('content') or result.get('text') or '',
                    ingestion_timestamp=datetime.now().isoformat()
                )
                checksum = self._calculate_checksum(metadata.content + metadata.title)
                if self._is_duplicate(checksum):
                    stats.duplicates_found += 1
                    continue
                if metadata.content:
                    summary_data = await self._summarize_content(metadata.content, metadata.title)
                    metadata.summary = summary_data.get("summary")
                    metadata.tags = summary_data.get("keywords", [])
                    if await self._store_in_vectorstore(metadata.content, metadata):
                        stats.total_ingested += 1
                        self._cache_processed_checksum(checksum)
        except Exception as e:
            logger.error(f"API ingestion failed: {e}")
        stats.end_time = time.time()
        return stats

    async def ingest_from_directory(self, directory_path: str, recursive: bool = True) -> IngestionStats:
        stats = IngestionStats()
        stats.start_time = time.time()
        try:
            # 🔱 RESOURCE HARDENING GATE
            await wait_for_resource_availability()
            
            directory = Path(directory_path)
            files = []
            for ext in ['.md', '.txt']:
                if recursive:
                    files.extend(directory.rglob(f"*{ext}"))
                else:
                    files.extend(directory.glob(f"*{ext}"))
            for file_path in files:
                stats.total_processed += 1
                try:
                    mime_type = "text/plain"
                    if self.magic:
                        mime_type = await anyio.to_thread.run_sync(lambda: self.magic.from_file(str(file_path), mime=True))
                    async with await anyio.open_file(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                        content = await f.read()
                    metadata = ContentMetadata(
                        source='local_file',
                        source_url=str(file_path),
                        title=file_path.stem,
                        content=content,
                        mime_type=mime_type,
                        ingestion_timestamp=datetime.now().isoformat()
                    )
                    checksum = self._calculate_checksum(content + str(file_path))
                    if self._is_duplicate(checksum):
                        stats.duplicates_found += 1
                        continue
                    summary_data = await self._summarize_content(content, metadata.title)
                    metadata.summary = summary_data.get("summary")
                    metadata.tags = summary_data.get("keywords", [])
                    if await self._store_in_vectorstore(content, metadata):
                        stats.total_ingested += 1
                        self._cache_processed_checksum(checksum)
                except Exception as e:
                    logger.error(f"File error {file_path}: {e}")
        except Exception as e:
            logger.error(f"Dir error: {e}")
        stats.end_time = time.time()
        return stats

    def _assess_content_quality(self, content: str, metadata: ContentMetadata) -> float:
        return 0.8

    def _enrich_metadata(self, metadata: ContentMetadata) -> ContentMetadata:
        return metadata

    def _apply_scholarly_enhancements(self, metadata: ContentMetadata) -> ContentMetadata:
        return metadata

    async def _store_in_vectorstore(self, content: str, metadata: ContentMetadata) -> bool:
        try:
            if not self.embeddings:
                # 🔱 RESOURCE HARDENING: Use Singleton Managed Hub
                self.embeddings = await self.resource_hub.get_model('embeddings')
            
            # Prioritize Qdrant (Central Vector Hub)
            if not self.vectorstore:
                try:
                    # Attempt to get central Qdrant store
                    self.vectorstore = await get_vectorstore_async(embeddings=self.embeddings)
                    logger.info("✓ Connected to central Qdrant vectorstore")
                except Exception as ve:
                    logger.warning(f"Qdrant connection failed, falling back to local FAISS: {ve}")
                    self.vectorstore = get_vectorstore(embeddings=self.embeddings)
            
            if not self.vectorstore:
                logger.error("Vectorstore not available for storage")
                return False
                
            from langchain_core.documents import Document
            doc = Document(page_content=content, metadata=metadata.to_dict())
            
            # Check if vectorstore has async support
            if hasattr(self.vectorstore, "aadd_documents"):
                await self.vectorstore.aadd_documents([doc])
            else:
                await anyio.to_thread.run_sync(lambda: self.vectorstore.add_documents([doc]))
                
            return True
        except Exception as e:
            logger.error(f"Store failed in vectorstore: {e}")
            return False

    def _rate_limit_api_call(self):
        elapsed = time.time() - self.last_api_call
        if elapsed < self.api_call_interval:
            time.sleep(self.api_call_interval - elapsed)
        self.last_api_call = time.time()

async def ingest_library(library_path: str = "/library") -> Tuple[int, float]:
    engine = EnterpriseIngestionEngine()
    stats = await engine.ingest_from_directory(library_path)
    return stats.total_ingested, stats.end_time - stats.start_time

async def ingest_from_library_mode(library_path: str = None) -> Tuple[int, float]:
    return await ingest_library(library_path or "/library")

__all__ = ["EnterpriseIngestionEngine", "ingest_library", "ingest_from_library_mode", "ContentMetadata", "IngestionStats"]
