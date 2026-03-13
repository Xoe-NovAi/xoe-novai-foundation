"""
XNAi Curator - Continuous Content Curation Pipeline

This module provides the core curation pipeline for the XNAi Knowledge Synthesis Engine,
handling 24/7 automated content collection and processing.
"""

import anyio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from uuid import UUID, uuid4
from urllib.parse import urljoin, urlparse
import aiofiles
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from PIL import Image
import pytesseract
import magic

from ..core.llm_router import LLMRouter
from ..core.memory_bank import MemoryBank
from ..core.qdrant_manager import QdrantManager
from ..core.redis_streams import RedisStreamManager
from ..core.security.knowledge_access import KnowledgeAccessControl
from ..core.utils import sanitize_filename
from ..core.async_patterns import migrate_from_asyncio_gather
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ContentSource(BaseModel):
    """Represents a content source for curation."""
    
    id: UUID
    source_type: str  # "web", "rss", "document", "code"
    url: str
    title: str
    description: str
    categories: List[str] = Field(default_factory=list)
    priority: int = 5  # 1-10, higher is more important
    enabled: bool = True
    last_crawled: Optional[datetime] = None
    crawl_interval: int = 3600  # seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CuratedContent(BaseModel):
    """Represents curated content ready for processing."""
    
    id: UUID
    source_id: UUID
    title: str
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    content_type: str  # "article", "blog", "paper", "code", "document"
    language: str = "en"
    content: str
    summary: Optional[str] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    quality_score: float = 0.0
    processing_status: str = "pending"  # "pending", "processing", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CurationPipeline:
    """Main curation pipeline for continuous content collection."""
    
    def __init__(
        self,
        llm_router: LLMRouter,
        memory_bank: MemoryBank,
        qdrant_manager: QdrantManager,
        redis_manager: RedisStreamManager,
        access_control: KnowledgeAccessControl
    ):
        self.llm_router = llm_router
        self.memory_bank = memory_bank
        self.qdrant_manager = qdrant_manager
        self.redis_manager = redis_manager
        self.access_control = access_control
        
        # Content sources
        self.sources: Dict[UUID, ContentSource] = {}
        
        # Processing queues using AnyIO
        self.web_queue: anyio.from_thread.Queue = anyio.from_thread.Queue()
        self.rss_queue: anyio.from_thread.Queue = anyio.from_thread.Queue()
        self.document_queue: anyio.from_thread.Queue = anyio.from_thread.Queue()
        self.code_queue: anyio.from_thread.Queue = anyio.from_thread.Queue()
        
        # Processing state
        self.is_running = False
        self.processing_tasks: List[anyio.Task] = []
        
        # Quality assessment models
        self.quality_model = None
        
    async def start(self):
        """Start the curation pipeline."""
        if self.is_running:
            logger.warning("Curation pipeline already running")
            return
            
        self.is_running = True
        logger.info("Starting XNAi Curator pipeline")
        
        # Load content sources
        await self._load_content_sources()
        
        # Start processing tasks using AnyIO TaskGroup
        async with anyio.create_task_group() as tg:
            tg.start_soon(self._web_processor)
            tg.start_soon(self._rss_processor)
            tg.start_soon(self._document_processor)
            tg.start_soon(self._code_processor)
            tg.start_soon(self._scheduler)
            tg.start_soon(self._quality_assessor)
        
        logger.info("XNAi Curator pipeline started successfully")
    
    async def stop(self):
        """Stop the curation pipeline."""
        if not self.is_running:
            return
            
        self.is_running = False
        logger.info("Stopping XNAi Curator pipeline")
        
        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await anyio.to_thread.run_sync(
            lambda: asyncio.run(asyncio.gather(*self.processing_tasks, return_exceptions=True))
        )
        
        # Clean up queues
        for queue in [self.web_queue, self.rss_queue, self.document_queue, self.code_queue]:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except anyio.from_thread.QueueEmpty:
                    break
        
        logger.info("XNAi Curator pipeline stopped successfully")
    
    async def add_content_source(self, source: ContentSource):
        """Add a new content source."""
        self.sources[source.id] = source
        
        # Save to memory bank
        await self.memory_bank.save_to_archival(
            f"content_source_{source.id}",
            source.dict()
        )
        
        # Add to appropriate queue based on type
        if source.source_type == "web":
            await self.web_queue.put(source)
        elif source.source_type == "rss":
            await self.rss_queue.put(source)
        elif source.source_type == "document":
            await self.document_queue.put(source)
        elif source.source_type == "code":
            await self.code_queue.put(source)
    
    async def _load_content_sources(self):
        """Load content sources from memory bank."""
        # This would load from persistent storage
        # For now, we'll create some default sources
        default_sources = [
            ContentSource(
                id=uuid4(),
                source_type="rss",
                url="https://feeds.feedburner.com/oreilly/radar",
                title="O'Reilly Radar",
                description="Insights from the O'Reilly team",
                categories=["technology", "ai", "programming"],
                priority=8
            ),
            ContentSource(
                id=uuid4(),
                source_type="rss",
                url="https://feeds.feedburner.com/TechCrunch/",
                title="TechCrunch",
                description="Startup and technology news",
                categories=["technology", "startups", "business"],
                priority=7
            )
        ]
        
        for source in default_sources:
            await self.add_content_source(source)
    
    async def _scheduler(self):
        """Scheduler for periodic content source processing."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for source in self.sources.values():
                    if not source.enabled:
                        continue
                    
                    # Check if it's time to crawl this source
                    if (source.last_crawled is None or 
                        (current_time - source.last_crawled).total_seconds() >= source.crawl_interval):
                        
                        await self._schedule_source(source)
                        source.last_crawled = current_time
                        
                        # Save updated source
                        await self.memory_bank.save_to_archival(
                            f"content_source_{source.id}",
                            source.dict()
                        )
                
                # Wait before next scheduling cycle
                await anyio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await anyio.sleep(60)
    
    async def _schedule_source(self, source: ContentSource):
        """Schedule a source for processing."""
        if source.source_type == "web":
            await self.web_queue.put(source)
        elif source.source_type == "rss":
            await self.rss_queue.put(source)
        elif source.source_type == "document":
            await self.document_queue.put(source)
        elif source.source_type == "code":
            await self.code_queue.put(source)
    
    async def _web_processor(self):
        """Process web content sources."""
        while self.is_running:
            try:
                source = await self.web_queue.get()
                
                # Crawl the web page
                content = await self._crawl_web_page(source.url)
                if content:
                    curated_content = await self._process_web_content(source, content)
                    await self._store_curated_content(curated_content)
                
        # Respect politeness policy
        await anyio.sleep(source.metadata.get("politeness_delay", 2.0))
                
            except Exception as e:
                logger.error(f"Error processing web source {source.id}: {e}")
    
    async def _crawl_web_page(self, url: str) -> Optional[str]:
        """Crawl a web page and extract content."""
        try:
            headers = {
                'User-Agent': 'XNAi-Curator/1.0 (Educational Research Bot)'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to crawl {url}: HTTP {response.status}")
                        return None
                    
                    html = await response.text()
                    
                    # Parse HTML content
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                        element.decompose()
                    
                    # Extract main content
                    # Try common content selectors
                    content_selectors = [
                        'article', 'main', '.content', '.post-content',
                        '.entry-content', '.article-body'
                    ]
                    
                    content = ""
                    for selector in content_selectors:
                        elements = soup.select(selector)
                        if elements:
                            content = ' '.join([elem.get_text(strip=True) for elem in elements])
                            if len(content) > 500:  # Minimum content length
                                break
                    
                    # Fallback to body if no specific content found
                    if not content:
                        body = soup.find('body')
                        if body:
                            content = body.get_text(strip=True)
                    
                    # Clean up content
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    return content if len(content) > 100 else None
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None
    
    async def _process_web_content(self, source: ContentSource, content: str) -> CuratedContent:
        """Process web content and create curated content."""
        # Extract metadata
        title = source.title
        author = None
        publish_date = None
        
        # Quality assessment
        quality_score = await self._assess_content_quality(content, source)
        
        # Content analysis
        analysis = await self._analyze_content(content)
        
        curated_content = CuratedContent(
            id=uuid4(),
            source_id=source.id,
            title=title,
            author=author,
            publish_date=publish_date,
            content_type="article",
            content=content,
            summary=analysis.get("summary"),
            entities=analysis.get("entities", []),
            quality_score=quality_score,
            metadata={
                "source_url": source.url,
                "categories": source.categories,
                "analysis": analysis
            }
        )
        
        return curated_content
    
    async def _rss_processor(self):
        """Process RSS feed sources."""
        while self.is_running:
            try:
                source = await self.rss_queue.get()
                
                # Parse RSS feed
                feed = await self._parse_rss_feed(source.url)
                if feed:
                    for entry in feed.entries:
                        content = await self._process_rss_entry(source, entry)
                        if content:
                            await self._store_curated_content(content)
                
        # Respect feed refresh interval
        await anyio.sleep(source.crawl_interval)
                
            except Exception as e:
                logger.error(f"Error processing RSS source {source.id}: {e}")
    
    async def _parse_rss_feed(self, url: str) -> Optional[Any]:
        """Parse an RSS feed."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch RSS feed {url}: HTTP {response.status}")
                        return None
                    
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    if feed.bozo:
                        logger.warning(f"RSS feed {url} is malformed: {feed.bozo_exception}")
                    
                    return feed
                    
        except Exception as e:
            logger.error(f"Error parsing RSS feed {url}: {e}")
            return None
    
    async def _process_rss_entry(self, source: ContentSource, entry: Any) -> Optional[CuratedContent]:
        """Process an RSS feed entry."""
        try:
            # Extract content from entry
            title = entry.title
            url = entry.link
            summary = entry.summary if hasattr(entry, 'summary') else ""
            
            # Get full content if available
            content = summary
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            
            # Clean content
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(strip=True)
            
            if len(content) < 100:
                return None
            
            # Quality assessment
            quality_score = await self._assess_content_quality(content, source)
            
            # Content analysis
            analysis = await self._analyze_content(content)
            
            curated_content = CuratedContent(
                id=uuid4(),
                source_id=source.id,
                title=title,
                author=getattr(entry, 'author', None),
                publish_date=datetime.fromtimestamp(time.mktime(entry.published_parsed)) if hasattr(entry, 'published_parsed') else None,
                content_type="blog",
                content=content,
                summary=analysis.get("summary"),
                entities=analysis.get("entities", []),
                quality_score=quality_score,
                metadata={
                    "source_url": url,
                    "categories": source.categories,
                    "analysis": analysis
                }
            )
            
            return curated_content
            
        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            return None
    
    async def _document_processor(self):
        """Process document sources."""
        while self.is_running:
            try:
                source = await self.document_queue.get()
                
                # Process document
                content = await self._process_document(source.url)
                if content:
                    curated_content = await self._process_document_content(source, content)
                    await self._store_curated_content(curated_content)
                
            except Exception as e:
                logger.error(f"Error processing document source {source.id}: {e}")
    
    async def _process_document(self, file_path: str) -> Optional[str]:
        """Process a document file."""
        try:
            file_type = magic.from_file(file_path, mime=True)
            
            if file_type == 'application/pdf':
                return await self._extract_pdf_content(file_path)
            elif file_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return await self._extract_docx_content(file_path)
            else:
                logger.warning(f"Unsupported document type: {file_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return None
    
    async def _extract_pdf_content(self, file_path: str) -> Optional[str]:
        """Extract content from PDF file."""
        try:
            # Extract text content
            text_content = extract_text(file_path, laparams=LAParams())
            
            # Try OCR if text extraction fails
            if len(text_content.strip()) < 100:
                # This would require image processing and OCR
                # For now, return what we have
                pass
            
            return text_content if len(text_content.strip()) > 100 else None
            
        except Exception as e:
            logger.error(f"Error extracting PDF content {file_path}: {e}")
            return None
    
    async def _extract_docx_content(self, file_path: str) -> Optional[str]:
        """Extract content from DOCX file."""
        try:
            import docx
            
            doc = docx.Document(file_path)
            content = []
            
            for para in doc.paragraphs:
                content.append(para.text)
            
            full_content = '\n'.join(content)
            return full_content if len(full_content) > 100 else None
            
        except Exception as e:
            logger.error(f"Error extracting DOCX content {file_path}: {e}")
            return None
    
    async def _code_processor(self):
        """Process code repository sources."""
        while self.is_running:
            try:
                source = await self.code_queue.get()
                
                # Process code repository
                content = await self._process_code_repository(source.url)
                if content:
                    curated_content = await self._process_code_content(source, content)
                    await self._store_curated_content(curated_content)
                
            except Exception as e:
                logger.error(f"Error processing code source {source.id}: {e}")
    
    async def _process_code_repository(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """Process a code repository."""
        try:
            # This would integrate with GitHub/GitLab APIs
            # For now, return placeholder
            return {
                "repository_url": repo_url,
                "description": "Code repository content",
                "files": [],
                "languages": [],
                "commits": []
            }
            
        except Exception as e:
            logger.error(f"Error processing code repository {repo_url}: {e}")
            return None
    
    async def _assess_content_quality(self, content: str, source: ContentSource) -> float:
        """Assess the quality of content."""
        try:
            # Use LLM for quality assessment
            prompt = f"""
            Assess the quality of the following content on a scale of 0.0 to 1.0.
            Consider factors like:
            - Relevance to categories: {', '.join(source.categories)}
            - Content depth and substance
            - Writing quality and clarity
            - Originality and value
            
            Content:
            {content[:2000]}  <!-- Limit content length -->
            
            Quality Score (0.0-1.0):
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "quality_assessment"},
                model_preference="quality-assessment-model"
            )
            
            # Parse response
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5  # Default score if parsing fails
                
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            return 0.5
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for entities, summary, etc."""
        try:
            # Entity extraction
            entities = await self._extract_entities(content)
            
            # Summarization
            summary = await self._generate_summary(content)
            
            return {
                "entities": entities,
                "summary": summary,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"entities": [], "summary": content[:500]}
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from content."""
        try:
            prompt = f"""
            Extract entities from the following content. Return in JSON format:
            {{
                "people": [],
                "organizations": [],
                "locations": [],
                "concepts": []
            }}
            
            Content:
            {content[:1000]}
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "entity_extraction"},
                model_preference="entity-extraction-model"
            )
            
            return json.loads(response) if response else []
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def _generate_summary(self, content: str) -> str:
        """Generate a summary of the content."""
        try:
            prompt = f"""
            Generate a concise summary (3-5 sentences) of the following content:
            
            {content[:1500]}
            
            Summary:
            """
            
            response = await self.llm_router.route_request(
                prompt=prompt,
                context={"operation": "summarization"},
                model_preference="summarization-model"
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return content[:500]
    
    async def _quality_assessor(self):
        """Quality assessment task for processed content."""
        while self.is_running:
            try:
                # This would monitor and re-assess content quality
                await anyio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in quality assessor: {e}")
    
    async def _store_curated_content(self, content: CuratedContent):
        """Store curated content in the system."""
        try:
            # Save to memory bank
            await self.memory_bank.save_to_archival(
                f"curated_content_{content.id}",
                content.dict()
            )
            
            # Generate embeddings and store in Qdrant
            embedding = await self._generate_content_embedding(content.content)
            
            collection_name = "curated_content"
            await self.qdrant_manager.upsert_vectors(
                collection_name=collection_name,
                vectors=[embedding],
                payloads=[{
                    "content_id": str(content.id),
                    "title": content.title,
                    "source_id": str(content.source_id),
                    "content_type": content.content_type,
                    "quality_score": content.quality_score,
                    "created_at": content.created_at.isoformat(),
                    "metadata": content.metadata
                }]
            )
            
            # Notify Redis stream
            await self.redis_manager.publish_message(
                stream_name="xnai:curated_content",
                message={
                    "event": "content_curated",
                    "content_id": str(content.id),
                    "title": content.title,
                    "quality_score": content.quality_score,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Stored curated content: {content.id}")
            
        except Exception as e:
            logger.error(f"Error storing curated content: {e}")
    
    async def _generate_content_embedding(self, content: str) -> List[float]:
        """Generate embedding for content."""
        try:
            # Use LLM router for embedding generation
            response = await self.llm_router.route_request(
                prompt=f"Generate embedding for: {content[:1000]}",
                context={"operation": "embedding"},
                model_preference="embedding-model"
            )
            
            # Parse embedding from response
            # This would depend on the specific embedding model format
            return response.get("embedding", [])
            
        except Exception as e:
            logger.error(f"Error generating content embedding: {e}")
            return []
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "is_running": self.is_running,
            "sources_count": len(self.sources),
            "queue_sizes": {
                "web": self.web_queue.qsize(),
                "rss": self.rss_queue.qsize(),
                "document": self.document_queue.qsize(),
                "code": self.code_queue.qsize()
            },
            "processing_tasks": len(self.processing_tasks)
        }