"""
Base Scraper - Abstract base class for all scraper templates.

Provides common functionality: deduplication, retry logic, content validation,
logging, and error handling.
"""

import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ScrapedContent:
    """Represents successfully scraped content."""
    
    service: str
    title: str
    content: str
    format: str = "markdown"
    metadata: Dict[str, Any] = None
    source_urls: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.source_urls is None:
            self.source_urls = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @property
    def content_hash(self) -> str:
        """SHA256 hash of content for deduplication."""
        return hashlib.sha256(self.content.encode()).hexdigest()
    
    @property
    def size_kb(self) -> float:
        """Content size in KB."""
        return len(self.content) / 1024
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "service": self.service,
            "title": self.title,
            "content": self.content,
            "format": self.format,
            "metadata": self.metadata,
            "source_urls": self.source_urls,
            "timestamp": self.timestamp.isoformat(),
            "hash": self.content_hash,
            "size_kb": self.size_kb,
        }


class BaseScraper(ABC):
    """Abstract base class for all scraper implementations."""
    
    def __init__(
        self,
        service: str,
        user_agent: str = "XNAi-Foundation/1.0",
        timeout: int = 30,
        rate_limit_delay: float = 2.0,
        max_retries: int = 3,
    ):
        """
        Initialize base scraper.
        
        Args:
            service: Service name (e.g., 'redis', 'postgresql')
            user_agent: User-Agent header for HTTP requests
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.service = service
        self.user_agent = user_agent
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        
        # Deduplication cache
        self._dedup_cache: Dict[str, str] = {}  # hash -> service
        
        # Statistics
        self.stats = {
            "urls_processed": 0,
            "urls_failed": 0,
            "content_items": 0,
            "total_size_kb": 0.0,
            "start_time": datetime.utcnow(),
        }
    
    @abstractmethod
    async def scrape(self, urls: List[str], config: Dict[str, Any] = None) -> List[ScrapedContent]:
        """
        Scrape content from given URLs.
        
        Args:
            urls: List of URLs to scrape
            config: Template-specific configuration
        
        Returns:
            List of ScrapedContent objects
        """
        pass
    
    async def _fetch_with_retry(
        self,
        fetch_func,
        url: str,
        retries: int = None,
    ) -> Optional[Any]:
        """
        Execute a fetch function with exponential backoff retries.
        
        Args:
            fetch_func: Async function to call (should accept url)
            url: URL to fetch
            retries: Number of retries (uses max_retries if None)
        
        Returns:
            Result from fetch_func or None if all retries failed
        """
        if retries is None:
            retries = self.max_retries
        
        for attempt in range(retries + 1):
            try:
                await asyncio.sleep(self.rate_limit_delay)
                result = await fetch_func(url)
                self.stats["urls_processed"] += 1
                return result
            except Exception as e:
                self.stats["urls_failed"] += 1
                logger.warning(
                    f"Fetch attempt {attempt + 1}/{retries + 1} failed for {url}: {e}"
                )
                if attempt < retries:
                    backoff_seconds = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(backoff_seconds)
                else:
                    logger.error(f"All retries exhausted for {url}")
                    return None
    
    def check_dedup(self, content_hash: str) -> bool:
        """
        Check if content already exists (deduplication).
        
        Args:
            content_hash: SHA256 hash of content
        
        Returns:
            True if hash already exists (duplicate)
        """
        return content_hash in self._dedup_cache
    
    def register_dedup(self, content_hash: str, service: str) -> None:
        """
        Register a content hash as processed.
        
        Args:
            content_hash: SHA256 hash of content
            service: Service name where content came from
        """
        self._dedup_cache[content_hash] = service
    
    def validate_content(
        self,
        content: str,
        min_length: int = 100,
        max_length: int = 10_000_000,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate scraped content quality.
        
        Args:
            content: Content to validate
            min_length: Minimum content length in characters
            max_length: Maximum content length in characters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Content is empty"
        
        if len(content) < min_length:
            return False, f"Content too short ({len(content)} < {min_length} chars)"
        
        if len(content) > max_length:
            return False, f"Content too large ({len(content)} > {max_length} chars)"
        
        # Check for minimum meaningful content (not just HTML tags)
        text_content = content.replace("<", "").replace(">", "")
        if len(text_content) < min_length / 2:
            return False, "Content appears to be mostly HTML markup"
        
        return True, None
    
    async def save_content(
        self,
        content: ScrapedContent,
        output_dir: Path,
    ) -> Path:
        """
        Save scraped content to disk.
        
        Args:
            content: ScrapedContent object
            output_dir: Directory to save to
        
        Returns:
            Path to saved file
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize title for filename
        filename = content.title.lower().replace(" ", "_").replace("/", "_")[:50]
        filepath = output_dir / f"{filename}.md"
        
        # Add content hash to filename if already exists
        if filepath.exists():
            filepath = output_dir / f"{filename}_{content.content_hash[:8]}.md"
        
        # Save markdown with metadata header
        markdown_content = self._format_markdown(content)
        filepath.write_text(markdown_content, encoding="utf-8")
        
        logger.info(f"Saved content to {filepath}")
        return filepath
    
    def _format_markdown(self, content: ScrapedContent) -> str:
        """
        Format content as markdown with metadata header.
        
        Args:
            content: ScrapedContent object
        
        Returns:
            Formatted markdown string
        """
        header = f"""---
title: {content.title}
service: {content.service}
source_urls: {json.dumps(content.source_urls)}
scraped_at: {content.timestamp.isoformat()}
content_hash: {content.content_hash}
size_kb: {content.size_kb:.2f}
---

"""
        return header + content.content
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        duration_seconds = (
            datetime.utcnow() - self.stats["start_time"]
        ).total_seconds()
        
        return {
            "service": self.service,
            "urls_processed": self.stats["urls_processed"],
            "urls_failed": self.stats["urls_failed"],
            "content_items": self.stats["content_items"],
            "total_size_kb": self.stats["total_size_kb"],
            "duration_seconds": duration_seconds,
            "avg_per_url_kb": (
                self.stats["total_size_kb"] / self.stats["urls_processed"]
                if self.stats["urls_processed"] > 0
                else 0
            ),
        }
    
    def _update_stats(self, content: ScrapedContent) -> None:
        """Update statistics with new content."""
        self.stats["content_items"] += 1
        self.stats["total_size_kb"] += content.size_kb
