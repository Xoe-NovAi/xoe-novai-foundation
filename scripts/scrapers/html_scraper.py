"""
HTML Scraper - Template 3 for web-based documentation scraping.

Uses crawl4ai for JavaScript rendering and recursive crawling.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

from scrapers.base_scraper import BaseScraper, ScrapedContent

logger = logging.getLogger(__name__)

# Try to import crawl4ai
try:
    from crawl4ai import AsyncWebCrawler, CrawlResult
    CRAWL4AI_AVAILABLE = True
except ImportError:
    logger.warning("crawl4ai not available - HTML scraper will be limited")
    CRAWL4AI_AVAILABLE = False


class HTMLScraper(BaseScraper):
    """Scraper for HTML-based documentation using crawl4ai."""
    
    DEFAULT_CONFIG = {
        "max_depth": 2,
        "max_pages": 50,
        "allowed_domains": [],  # Restrict to specific domains
        "exclude_patterns": [
            "/blog/",
            "/news/",
            "/forum/",
            "/community/",
            "/download/",
        ],
        "include_patterns": [
            "/docs/",
            "/documentation/",
            "/guide/",
            "/tutorial/",
            "/manual/",
            "/api/",
        ],
        "js_rendering": True,
        "wait_time": 2,  # seconds for JS to render
    }
    
    async def scrape(
        self,
        urls: List[str],
        config: Dict[str, Any] = None
    ) -> List[ScrapedContent]:
        """
        Scrape documentation from HTML websites.
        
        Args:
            urls: List of documentation URLs
            config: Configuration with keys like max_depth, max_pages, etc.
        
        Returns:
            List of ScrapedContent objects
        """
        config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        if not CRAWL4AI_AVAILABLE:
            logger.error("crawl4ai not installed - cannot scrape HTML")
            return []
        
        content_items = []
        visited_urls = set()
        
        try:
            async with AsyncWebCrawler() as crawler:
                for start_url in urls:
                    logger.info(f"Starting HTML scrape from {start_url}")
                    
                    items = await self._crawl_recursive(
                        crawler,
                        start_url,
                        visited_urls,
                        config,
                    )
                    content_items.extend(items)
                    logger.info(f"Completed crawl of {start_url}")
        
        except Exception as e:
            logger.error(f"HTML scraping failed: {e}", exc_info=True)
        
        logger.info(f"HTML scraper completed: {len(content_items)} total items")
        return content_items
    
    async def _crawl_recursive(
        self,
        crawler,
        url: str,
        visited: set,
        config: Dict[str, Any],
        depth: int = 0,
    ) -> List[ScrapedContent]:
        """
        Recursively crawl documentation pages.
        
        Args:
            crawler: AsyncWebCrawler instance
            url: URL to crawl
            visited: Set of visited URLs
            config: Crawling configuration
            depth: Current recursion depth
        
        Returns:
            List of ScrapedContent objects
        """
        max_depth = config.get("max_depth", 2)
        max_pages = config.get("max_pages", 50)
        
        # Check depth limit
        if depth > max_depth:
            return []
        
        # Check page limit
        if len(visited) >= max_pages:
            logger.info(f"Reached max pages limit ({max_pages})")
            return []
        
        # Skip if already visited
        if url in visited:
            return []
        
        # Parse URL
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Check allowed domains
        allowed_domains = config.get("allowed_domains", [])
        if allowed_domains and not any(domain.endswith(d) for d in allowed_domains):
            logger.debug(f"Domain not allowed: {domain}")
            return []
        
        # Check exclusion patterns
        path = parsed.path
        exclude_patterns = config.get("exclude_patterns", [])
        if any(pattern in path for pattern in exclude_patterns):
            logger.debug(f"Path excluded: {path}")
            return []
        
        visited.add(url)
        logger.debug(f"Crawling: {url} (depth={depth})")
        
        content_items = []
        
        try:
            # Crawl the page
            result: CrawlResult = await asyncio.wait_for(
                crawler.arun(
                    url,
                    wait_time=config.get("wait_time", 2),
                ),
                timeout=self.timeout,
            )
            
            if not result.success:
                logger.warning(f"Failed to crawl {url}: {result.status_code}")
                self.stats["urls_failed"] += 1
                return []
            
            # Extract content (crawl4ai uses extracted_content or cleaned_html)
            content = result.extracted_content or result.cleaned_html or result.html or ""
            
            if not content:
                logger.warning(f"No content extracted from {url}")
                return []
            
            # Validate content
            is_valid, error = self.validate_content(content)
            if not is_valid:
                logger.warning(f"Invalid content from {url}: {error}")
                return []
            
            # Create content item (crawl4ai doesn't have title attribute, derive from URL)
            title = url.split("/")[-1] or "Page"
            
            content_obj = ScrapedContent(
                service=self.service,
                title=title,
                content=content,
                format="markdown",
                metadata={
                    "url": url,
                    "status_code": result.status_code,
                    "depth": depth,
                },
                source_urls=[url],
            )
            
            # Check dedup
            if not self.check_dedup(content_obj.content_hash):
                content_items.append(content_obj)
                self.register_dedup(content_obj.content_hash, self.service)
                self._update_stats(content_obj)
                self.stats["urls_processed"] += 1
                logger.info(f"Added: {title} ({content_obj.size_kb:.2f} KB)")
            
            # Extract and crawl child links (if not at max depth)
            if depth < max_depth and len(visited) < max_pages:
                child_links = result.links or []
                
                include_patterns = config.get("include_patterns", [])
                for link_text, link_url in child_links:
                    # Normalize link
                    full_url = urljoin(url, link_url)
                    
                    # Skip if already visited
                    if full_url in visited:
                        continue
                    
                    # Check if should include
                    if include_patterns:
                        if not any(pattern in full_url for pattern in include_patterns):
                            continue
                    
                    # Recursively crawl
                    child_items = await self._crawl_recursive(
                        crawler,
                        full_url,
                        visited,
                        config,
                        depth=depth + 1,
                    )
                    content_items.extend(child_items)
                    
                    # Check limits again
                    if len(visited) >= max_pages:
                        break
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout crawling {url}")
            self.stats["urls_failed"] += 1
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            self.stats["urls_failed"] += 1
        
        return content_items
