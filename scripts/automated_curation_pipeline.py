#!/usr/bin/env python3
"""
Automated Curation Pipeline
===========================
24/7 background automation for content discovery, processing, and integration.

This pipeline continuously monitors and curates content from various sources,
integrating with the Foundation stack for intelligent processing and storage.

Author: XNAi Foundation
Created: 2026-02-28
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import aiohttp
import feedparser
from PIL import Image
import pytesseract
import requests
from urllib.parse import urljoin, urlparse
import hashlib
import mimetypes

# Foundation stack imports
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.model_router import ModelRouter
from app.XNAi_rag_app.core.memory_bank import MemoryBankLoader
from app.XNAi_rag_app.core.iam_db import IAMDatabase
from app.XNAi_rag_app.core.iam_handshake import IAMHandshake

# Configuration
CONFIG_PATH = Path("configs/automated-curation-pipeline.yaml")
LOG_LEVEL = logging.INFO

@dataclass
class ContentSource:
    """Configuration for a content source."""
    name: str
    type: str  # web, rss, file, api
    url: str
    enabled: bool
    interval_minutes: int
    filters: Dict[str, Any]
    priority: str

@dataclass
class CuratedContent:
    """Curated content item."""
    id: str
    source: str
    title: str
    url: str
    content: str
    content_type: str
    metadata: Dict[str, Any]
    created_at: str
    processed: bool = False
    tags: List[str] = None

class AutomatedCurationPipeline:
    """24/7 automated content curation pipeline."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_config()
        self.sources = self._load_sources()
        
        # Foundation stack integration
        self.agent_bus = AgentBusClient()
        self.model_router = ModelRouter()
        self.memory_bank = MemoryBankLoader()
        self.iam_db = IAMDatabase()
        self.iam_handshake = IAMHandshake()
        
        # Pipeline state
        self.is_running = False
        self.active_tasks = {}
        self.content_queue = asyncio.Queue()
        self.processed_content = []
        
        self.logger.info("Automated Curation Pipeline initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/automated-curation-pipeline.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration."""
        if CONFIG_PATH.exists():
            import yaml
            with open(CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "pipeline": {
                "enabled": True,
                "max_concurrent_sources": 5,
                "max_queue_size": 1000,
                "processing_timeout": 300,
                "retry_attempts": 3,
                "retry_delay": 60
            },
            "sources": {
                "web": {
                    "enabled": True,
                    "max_pages_per_source": 10,
                    "crawl_depth": 2,
                    "user_agent": "XNAi-Curation-Bot/1.0"
                },
                "rss": {
                    "enabled": True,
                    "max_items_per_feed": 20,
                    "update_interval": 30
                },
                "file": {
                    "enabled": True,
                    "watch_directories": ["./watched_files/"],
                    "supported_extensions": [".pdf", ".docx", ".txt", ".md"]
                },
                "api": {
                    "enabled": True,
                    "rate_limit": 100,
                    "timeout": 30
                }
            },
            "processing": {
                "ocr_enabled": True,
                "text_extraction": True,
                "summarization": True,
                "tagging": True,
                "translation": False
            },
            "storage": {
                "memory_bank_integration": True,
                "qdrant_integration": True,
                "local_storage": True,
                "storage_path": "curated_content/"
            }
        }
    
    def _load_sources(self) -> List[ContentSource]:
        """Load content sources from configuration."""
        sources_config = self.config.get("sources", {})
        sources = []
        
        # Web sources
        if sources_config.get("web", {}).get("enabled", False):
            web_sources = [
                ContentSource(
                    name="Tech News",
                    type="web",
                    url="https://techcrunch.com",
                    enabled=True,
                    interval_minutes=60,
                    filters={"keywords": ["AI", "ML", "tech"]},
                    priority="high"
                ),
                ContentSource(
                    name="AI Research",
                    type="web",
                    url="https://arxiv.org",
                    enabled=True,
                    interval_minutes=120,
                    filters={"keywords": ["machine learning", "artificial intelligence"]},
                    priority="medium"
                )
            ]
            sources.extend(web_sources)
        
        # RSS sources
        if sources_config.get("rss", {}).get("enabled", False):
            rss_sources = [
                ContentSource(
                    name="Hacker News",
                    type="rss",
                    url="https://hnrss.org/frontpage",
                    enabled=True,
                    interval_minutes=30,
                    filters={"keywords": ["programming", "tech"]},
                    priority="high"
                ),
                ContentSource(
                    name="AI Weekly",
                    type="rss",
                    url="https://aiweekly.co/feed/",
                    enabled=True,
                    interval_minutes=60,
                    filters={"keywords": ["AI", "machine learning"]},
                    priority="medium"
                )
            ]
            sources.extend(rss_sources)
        
        # File sources
        if sources_config.get("file", {}).get("enabled", False):
            file_sources = [
                ContentSource(
                    name="Local Documents",
                    type="file",
                    url="./watched_files/",
                    enabled=True,
                    interval_minutes=10,
                    filters={"extensions": [".pdf", ".docx", ".txt"]},
                    priority="low"
                )
            ]
            sources.extend(file_sources)
        
        return sources
    
    async def start(self):
        """Start the automated curation pipeline."""
        if self.is_running:
            self.logger.warning("Pipeline already running")
            return
        
        self.is_running = True
        self.logger.info("Starting Automated Curation Pipeline...")
        
        # Create storage directory
        storage_path = Path(self.config["storage"]["storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Start monitoring tasks
        tasks = []
        
        # Content discovery tasks
        for source in self.sources:
            if source.enabled:
                task = asyncio.create_task(self._monitor_source(source))
                tasks.append(task)
        
        # Content processing task
        processing_task = asyncio.create_task(self._process_content_queue())
        tasks.append(processing_task)
        
        # Health monitoring task
        health_task = asyncio.create_task(self._monitor_pipeline_health())
        tasks.append(health_task)
        
        self.logger.info(f"Pipeline started with {len(tasks)} monitoring tasks")
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("Pipeline stopped by user")
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the automated curation pipeline."""
        self.is_running = False
        self.logger.info("Stopping Automated Curation Pipeline...")
    
    async def _monitor_source(self, source: ContentSource):
        """Monitor a content source for new content."""
        self.logger.info(f"Monitoring source: {source.name}")
        
        while self.is_running:
            try:
                if source.type == "web":
                    await self._crawl_web_source(source)
                elif source.type == "rss":
                    await self._monitor_rss_source(source)
                elif source.type == "file":
                    await self._monitor_file_source(source)
                elif source.type == "api":
                    await self._monitor_api_source(source)
                
                # Wait for next interval
                await asyncio.sleep(source.interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Error monitoring source {source.name}: {e}")
                await asyncio.sleep(self.config["pipeline"]["retry_delay"])
    
    async def _crawl_web_source(self, source: ContentSource):
        """Crawl web source for new content."""
        self.logger.debug(f"Crawling web source: {source.name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Extract links and content
                        links = self._extract_links(content, source.url)
                        
                        for link in links[:self.config["sources"]["web"]["max_pages_per_source"]]:
                            if self._should_process_link(link, source):
                                curated_content = await self._process_web_content(link, source)
                                if curated_content:
                                    await self.content_queue.put(curated_content)
        
        except Exception as e:
            self.logger.error(f"Error crawling web source {source.name}: {e}")
    
    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        import re
        link_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, html_content)
        
        # Convert relative URLs to absolute
        absolute_links = []
        for link in links:
            absolute_link = urljoin(base_url, link)
            if self._is_valid_content_link(absolute_link):
                absolute_links.append(absolute_link)
        
        return absolute_links
    
    def _is_valid_content_link(self, url: str) -> bool:
        """Check if URL is a valid content link."""
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
        
        # Skip common non-content URLs
        skip_patterns = [
            '/login', '/signup', '/register', '/contact', '/about',
            '/terms', '/privacy', '/help', '/support'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def _should_process_link(self, link: str, source: ContentSource) -> bool:
        """Check if link should be processed based on filters."""
        # Check if already processed recently
        if self._is_recently_processed(link):
            return False
        
        # Check keyword filters
        if "keywords" in source.filters:
            keywords = source.filters["keywords"]
            for keyword in keywords:
                if keyword.lower() in link.lower():
                    return True
            return False
        
        return True
    
    def _is_recently_processed(self, url: str) -> bool:
        """Check if URL was recently processed."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for content in self.processed_content:
            if content.id == url_hash and datetime.fromisoformat(content.created_at) > cutoff_time:
                return True
        
        return False
    
    async def _process_web_content(self, url: str, source: ContentSource) -> Optional[CuratedContent]:
        """Process web content and extract information."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract content using simple heuristics
                        title = self._extract_title(content)
                        text_content = self._extract_text_content(content)
                        
                        if len(text_content) > 100:  # Minimum content length
                            content_id = hashlib.md5(url.encode()).hexdigest()
                            
                            curated_content = CuratedContent(
                                id=content_id,
                                source=source.name,
                                title=title,
                                url=url,
                                content=text_content,
                                content_type="web",
                                metadata={
                                    "source_type": "web",
                                    "crawl_depth": 1,
                                    "extracted_at": datetime.now().isoformat()
                                },
                                created_at=datetime.now().isoformat()
                            )
                            
                            return curated_content
        
        except Exception as e:
            self.logger.error(f"Error processing web content {url}: {e}")
        
        return None
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content."""
        import re
        title_pattern = r'<title[^>]*>([^<]+)</title>'
        match = re.search(title_pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Untitled"
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract text content from HTML."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up text
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        
        return ' '.join(cleaned_lines)
    
    async def _monitor_rss_source(self, source: ContentSource):
        """Monitor RSS feed for new content."""
        self.logger.debug(f"Monitoring RSS source: {source.name}")
        
        try:
            feed = feedparser.parse(source.url)
            
            if feed.entries:
                for entry in feed.entries[:self.config["sources"]["rss"]["max_items_per_feed"]]:
                    if self._should_process_rss_entry(entry, source):
                        curated_content = await self._process_rss_entry(entry, source)
                        if curated_content:
                            await self.content_queue.put(curated_content)
        
        except Exception as e:
            self.logger.error(f"Error monitoring RSS source {source.name}: {e}")
    
    def _should_process_rss_entry(self, entry, source: ContentSource) -> bool:
        """Check if RSS entry should be processed."""
        # Check if already processed
        entry_id = getattr(entry, 'id', entry.link)
        if self._is_recently_processed(entry_id):
            return False
        
        # Check keyword filters
        if "keywords" in source.filters:
            keywords = source.filters["keywords"]
            content = f"{entry.title} {getattr(entry, 'summary', '')}"
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    return True
            return False
        
        return True
    
    async def _process_rss_entry(self, entry, source: ContentSource) -> Optional[CuratedContent]:
        """Process RSS entry and create curated content."""
        try:
            content_id = hashlib.md5(entry.link.encode()).hexdigest()
            
            curated_content = CuratedContent(
                id=content_id,
                source=source.name,
                title=entry.title,
                url=entry.link,
                content=getattr(entry, 'summary', ''),
                content_type="rss",
                metadata={
                    "source_type": "rss",
                    "published": getattr(entry, 'published', ''),
                    "author": getattr(entry, 'author', ''),
                    "extracted_at": datetime.now().isoformat()
                },
                created_at=datetime.now().isoformat()
            )
            
            return curated_content
        
        except Exception as e:
            self.logger.error(f"Error processing RSS entry {entry.title}: {e}")
            return None
    
    async def _monitor_file_source(self, source: ContentSource):
        """Monitor file directory for new content."""
        self.logger.debug(f"Monitoring file source: {source.name}")
        
        try:
            watch_dir = Path(source.url)
            if not watch_dir.exists():
                watch_dir.mkdir(parents=True, exist_ok=True)
                return
            
            # Check for new files
            supported_extensions = self.config["sources"]["file"]["supported_extensions"]
            
            for file_path in watch_dir.iterdir():
                if file_path.suffix.lower() in supported_extensions:
                    if self._should_process_file(file_path, source):
                        curated_content = await self._process_file(file_path, source)
                        if curated_content:
                            await self.content_queue.put(curated_content)
        
        except Exception as e:
            self.logger.error(f"Error monitoring file source {source.name}: {e}")
    
    def _should_process_file(self, file_path: Path, source: ContentSource) -> bool:
        """Check if file should be processed."""
        # Check if already processed
        file_hash = self._get_file_hash(file_path)
        if self._is_recently_processed(file_hash):
            return False
        
        return True
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get file hash for deduplication."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    async def _process_file(self, file_path: Path, source: ContentSource) -> Optional[CuratedContent]:
        """Process file and extract content."""
        try:
            content_type = mimetypes.guess_type(file_path)[0]
            
            if file_path.suffix.lower() == '.pdf':
                text_content = self._extract_pdf_content(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                text_content = self._extract_docx_content(file_path)
            elif file_path.suffix.lower() in ['.txt', '.md']:
                text_content = self._extract_text_file_content(file_path)
            else:
                return None
            
            if len(text_content) > 50:  # Minimum content length
                file_hash = self._get_file_hash(file_path)
                
                curated_content = CuratedContent(
                    id=file_hash,
                    source=source.name,
                    title=file_path.name,
                    url=str(file_path),
                    content=text_content,
                    content_type="file",
                    metadata={
                        "source_type": "file",
                        "file_path": str(file_path),
                        "file_size": file_path.stat().st_size,
                        "file_type": content_type,
                        "extracted_at": datetime.now().isoformat()
                    },
                    created_at=datetime.now().isoformat()
                )
                
                return curated_content
        
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
        
        return None
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text content from PDF file."""
        import PyPDF2
        
        text_content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
        
        except Exception as e:
            self.logger.error(f"Error extracting PDF content {file_path}: {e}")
        
        return text_content
    
    def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text content from DOCX file."""
        import docx
        
        text_content = ""
        try:
            doc = docx.Document(file_path)
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        
        except Exception as e:
            self.logger.error(f"Error extracting DOCX content {file_path}: {e}")
        
        return text_content
    
    def _extract_text_file_content(self, file_path: Path) -> str:
        """Extract text content from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error extracting text file content {file_path}: {e}")
            return ""
    
    async def _monitor_api_source(self, source: ContentSource):
        """Monitor API source for new content."""
        self.logger.debug(f"Monitoring API source: {source.name}")
        
        # Placeholder for API monitoring implementation
        pass
    
    async def _process_content_queue(self):
        """Process content from the queue."""
        self.logger.info("Starting content processing queue")
        
        while self.is_running:
            try:
                # Get content from queue with timeout
                content = await asyncio.wait_for(
                    self.content_queue.get(),
                    timeout=30
                )
                
                # Process content
                await self._process_curated_content(content)
                
                # Mark task as done
                self.content_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing content queue: {e}")
    
    async def _process_curated_content(self, content: CuratedContent):
        """Process curated content through Foundation stack."""
        self.logger.info(f"Processing curated content: {content.title}")
        
        try:
            # Enhance content with AI processing
            enhanced_content = await self._enhance_content_with_ai(content)
            
            # Store in Foundation stack
            await self._store_content(enhanced_content)
            
            # Update processed content list
            self.processed_content.append(enhanced_content)
            
            # Keep only recent processed content in memory
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.processed_content = [
                c for c in self.processed_content
                if datetime.fromisoformat(c.created_at) > cutoff_time
            ]
            
            self.logger.info(f"Successfully processed content: {content.title}")
        
        except Exception as e:
            self.logger.error(f"Error processing content {content.title}: {e}")
    
    async def _enhance_content_with_ai(self, content: CuratedContent) -> CuratedContent:
        """Enhance content using AI models."""
        try:
            # Summarization
            if self.config["processing"]["summarization"]:
                summary = await self._generate_summary(content.content)
                content.metadata["summary"] = summary
            
            # Tagging
            if self.config["processing"]["tagging"]:
                tags = await self._generate_tags(content.content)
                content.tags = tags
            
            # Translation (if enabled)
            if self.config["processing"]["translation"]:
                translated = await self._translate_content(content.content)
                content.metadata["translated_content"] = translated
            
            return content
        
        except Exception as e:
            self.logger.error(f"Error enhancing content {content.title}: {e}")
            return content
    
    async def _generate_summary(self, content: str) -> str:
        """Generate summary using AI model."""
        # Use Foundation stack model router for summarization
        model = self.model_router.select_model(
            task_type="summarization",
            complexity="medium",
            context_length=len(content)
        )
        
        # This would integrate with the actual model execution
        # For now, return a placeholder
        return f"Summary of content ({len(content)} characters)"
    
    async def _generate_tags(self, content: str) -> List[str]:
        """Generate tags using AI model."""
        # Use Foundation stack for tag generation
        # For now, return placeholder tags
        return ["curated", "automated", "content"]
    
    async def _translate_content(self, content: str) -> str:
        """Translate content using AI model."""
        # Use Foundation stack for translation
        # For now, return original content
        return content
    
    async def _store_content(self, content: CuratedContent):
        """Store content in Foundation stack."""
        try:
            # Store in Memory Bank
            if self.config["storage"]["memory_bank_integration"]:
                await self._store_in_memory_bank(content)
            
            # Store in Qdrant
            if self.config["storage"]["qdrant_integration"]:
                await self._store_in_qdrant(content)
            
            # Store locally
            if self.config["storage"]["local_storage"]:
                await self._store_locally(content)
        
        except Exception as e:
            self.logger.error(f"Error storing content {content.title}: {e}")
    
    async def _store_in_memory_bank(self, content: CuratedContent):
        """Store content in Memory Bank."""
        # This would integrate with the actual Memory Bank API
        self.logger.debug(f"Storing in Memory Bank: {content.title}")
    
    async def _store_in_qdrant(self, content: CuratedContent):
        """Store content in Qdrant."""
        # This would integrate with the actual Qdrant API
        self.logger.debug(f"Storing in Qdrant: {content.title}")
    
    async def _store_locally(self, content: CuratedContent):
        """Store content locally."""
        storage_path = Path(self.config["storage"]["storage_path"])
        file_path = storage_path / f"{content.id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(asdict(content), f, indent=2)
    
    async def _monitor_pipeline_health(self):
        """Monitor pipeline health and performance."""
        self.logger.info("Starting pipeline health monitoring")
        
        while self.is_running:
            try:
                # Check queue size
                queue_size = self.content_queue.qsize()
                self.logger.debug(f"Content queue size: {queue_size}")
                
                # Check active tasks
                active_count = len(self.active_tasks)
                self.logger.debug(f"Active tasks: {active_count}")
                
                # Check processed content count
                processed_count = len(self.processed_content)
                self.logger.debug(f"Processed content: {processed_count}")
                
                # Send health metrics to Agent Bus
                health_metrics = {
                    "queue_size": queue_size,
                    "active_tasks": active_count,
                    "processed_content": processed_count,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.agent_bus.publish("curation_pipeline_health", health_metrics)
                
                # Wait before next health check
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "is_running": self.is_running,
            "queue_size": self.content_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "processed_content": len(self.processed_content),
            "sources": len([s for s in self.sources if s.enabled])
        }

async def main():
    """Main pipeline execution."""
    pipeline = AutomatedCurationPipeline()
    
    try:
        await pipeline.start()
    except KeyboardInterrupt:
        pipeline.stop()

if __name__ == "__main__":
    asyncio.run(main())