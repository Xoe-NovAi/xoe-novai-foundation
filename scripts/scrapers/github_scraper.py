"""
GitHub Scraper - Template 1 for scraping documentation from GitHub repositories.

Handles:
- Cloning repositories (shallow clone)
- Extracting docs/ and /docs/ folders
- Parsing README.md files
- Converting markdown to normalized format
"""

import asyncio
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from scrapers.base_scraper import BaseScraper, ScrapedContent


logger = logging.getLogger(__name__)


class GitHubScraper(BaseScraper):
    """Scraper for GitHub repositories."""
    
    MARKDOWN_FOLDERS = [
        "docs",
        "documentation", 
        "doc",
        "manual",
        "guides",
    ]
    
    README_FILES = [
        "README.md",
        "readme.md",
        "README",
    ]
    
    async def scrape(
        self, 
        urls: List[str], 
        config: Dict[str, Any] = None
    ) -> List[ScrapedContent]:
        """
        Scrape documentation from GitHub repositories.
        
        Args:
            urls: List of GitHub URLs (e.g., https://github.com/redis/redis)
            config: Config with optional keys:
                - max_depth: Maximum folder depth to traverse
                - include_readme: Whether to include README.md (default: True)
                - filter_patterns: List of filename patterns to include
        
        Returns:
            List of ScrapedContent objects
        """
        config = config or {}
        max_depth = config.get("max_depth", 3)
        include_readme = config.get("include_readme", True)
        filter_patterns = config.get("filter_patterns", ["*.md"])
        
        content_items = []
        
        for url in urls:
            logger.info(f"Scraping GitHub repo: {url}")
            
            try:
                # Clone repository
                with tempfile.TemporaryDirectory() as tmpdir:
                    repo_content = await self._clone_and_extract(
                        url,
                        tmpdir,
                        max_depth=max_depth,
                        include_readme=include_readme,
                        filter_patterns=filter_patterns,
                    )
                    
                    if repo_content:
                        content_items.extend(repo_content)
                        logger.info(f"Successfully scraped {len(repo_content)} documents from {url}")
                    else:
                        logger.warning(f"No documents found in {url}")
            
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                self.stats["urls_failed"] += 1
        
        logger.info(f"GitHub scraper completed: {len(content_items)} total items")
        return content_items
    
    async def _clone_and_extract(
        self,
        url: str,
        tmpdir: str,
        max_depth: int = 3,
        include_readme: bool = True,
        filter_patterns: List[str] = None,
    ) -> List[ScrapedContent]:
        """
        Clone a GitHub repo and extract documentation.
        
        Args:
            url: GitHub repository URL
            tmpdir: Temporary directory for cloning
            max_depth: Maximum depth to traverse
            include_readme: Include README.md files
            filter_patterns: Filename patterns to include
        
        Returns:
            List of ScrapedContent objects
        """
        filter_patterns = filter_patterns or ["*.md"]
        
        # Normalize URL
        if not url.endswith(".git"):
            url = url.rstrip("/") + ".git"
        
        repo_path = Path(tmpdir) / "repo"
        
        try:
            # Shallow clone (depth=1)
            logger.info(f"Cloning {url} to {repo_path}")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(repo_path)],
                capture_output=True,
                timeout=60,
                text=True,
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")
            
            # Extract docs
            content_items = []
            
            # Look for documentation folders
            for doc_folder in self.MARKDOWN_FOLDERS:
                doc_path = repo_path / doc_folder
                if doc_path.exists():
                    logger.info(f"Found documentation folder: {doc_path}")
                    items = await self._extract_markdown_files(
                        doc_path,
                        max_depth=max_depth,
                        filter_patterns=filter_patterns,
                    )
                    content_items.extend(items)
            
            # Extract README.md
            if include_readme:
                for readme_file in self.README_FILES:
                    readme_path = repo_path / readme_file
                    if readme_path.exists():
                        logger.info(f"Found README: {readme_path}")
                        try:
                            content = readme_path.read_text(encoding="utf-8")
                            
                            # Validate content
                            is_valid, error = self.validate_content(content)
                            if is_valid:
                                item = ScrapedContent(
                                    service=self.service,
                                    title=f"README - {self.service}",
                                    content=content,
                                    format="markdown",
                                    metadata={"type": "readme"},
                                    source_urls=[url],
                                )
                                
                                # Check deduplication
                                if not self.check_dedup(item.content_hash):
                                    content_items.append(item)
                                    self.register_dedup(item.content_hash, self.service)
                                    self._update_stats(item)
                                    logger.info(f"Added README ({item.size_kb:.2f} KB)")
                        
                        except Exception as e:
                            logger.error(f"Failed to read {readme_path}: {e}")
            
            self.stats["urls_processed"] += 1
            return content_items
        
        except Exception as e:
            logger.error(f"Error cloning repository {url}: {e}")
            self.stats["urls_failed"] += 1
            return []
    
    async def _extract_markdown_files(
        self,
        root_path: Path,
        max_depth: int = 3,
        filter_patterns: List[str] = None,
        current_depth: int = 0,
    ) -> List[ScrapedContent]:
        """
        Recursively extract markdown files from a directory.
        
        Args:
            root_path: Root directory to search
            max_depth: Maximum recursion depth
            filter_patterns: Filename patterns to include
            current_depth: Current recursion depth
        
        Returns:
            List of ScrapedContent objects
        """
        filter_patterns = filter_patterns or ["*.md"]
        content_items = []
        
        if current_depth >= max_depth:
            return content_items
        
        try:
            for item in sorted(root_path.iterdir()):
                # Skip hidden files/dirs
                if item.name.startswith("."):
                    continue
                
                if item.is_dir():
                    # Recurse into subdirectories
                    sub_items = await self._extract_markdown_files(
                        item,
                        max_depth=max_depth,
                        filter_patterns=filter_patterns,
                        current_depth=current_depth + 1,
                    )
                    content_items.extend(sub_items)
                
                elif item.is_file():
                    # Check if file matches patterns
                    if any(item.match(pattern) for pattern in filter_patterns):
                        try:
                            content = item.read_text(encoding="utf-8")
                            
                            # Validate
                            is_valid, error = self.validate_content(content)
                            if not is_valid:
                                logger.debug(f"Skipping {item.name}: {error}")
                                continue
                            
                            # Create content item
                            relative_path = item.relative_to(root_path.parent)
                            title = item.stem.replace("_", " ").replace("-", " ").title()
                            
                            content_obj = ScrapedContent(
                                service=self.service,
                                title=title,
                                content=content,
                                format="markdown",
                                metadata={
                                    "file_path": str(relative_path),
                                    "file_size_bytes": item.stat().st_size,
                                },
                                source_urls=[str(item)],
                            )
                            
                            # Check dedup
                            if not self.check_dedup(content_obj.content_hash):
                                content_items.append(content_obj)
                                self.register_dedup(content_obj.content_hash, self.service)
                                self._update_stats(content_obj)
                                logger.debug(f"Added {item.name} ({content_obj.size_kb:.2f} KB)")
                            else:
                                logger.debug(f"Skipped {item.name} (duplicate hash)")
                        
                        except Exception as e:
                            logger.error(f"Failed to read {item}: {e}")
        
        except Exception as e:
            logger.error(f"Error traversing {root_path}: {e}")
        
        return content_items
