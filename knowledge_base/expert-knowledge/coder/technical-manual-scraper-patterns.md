# Technical Manual Scraper Patterns

**Last Updated**: February 15, 2026
**Version**: v1.0.0
**Purpose**: Patterns and best practices for scraping technical manuals and documentation

## Overview

This knowledge card documents patterns for building robust technical manual scrapers that can extract structured information from various documentation sources while handling common challenges like authentication, rate limiting, and content extraction.

## Table of Contents

1. [Basic Scraper Architecture](#basic-scraper-architecture)
2. [Authentication Patterns](#authentication-patterns)
3. [Rate Limiting & Throttling](#rate-limiting--throttling)
4. [Content Extraction Patterns](#content-extraction-patterns)
5. [Error Handling & Resilience](#error-handling--resilience)
6. [Data Processing & Storage](#data-processing--storage)
7. [Testing & Validation](#testing--validation)

## Basic Scraper Architecture

### Core Components

```python
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import logging

@dataclass
class ScrapingConfig:
    """Configuration for scraping operations."""
    base_url: str
    max_concurrent: int = 5
    request_delay: float = 1.0
    timeout: int = 30
    retry_attempts: int = 3
    user_agent: str = "Mozilla/5.0 (compatible; TechnicalScraper/1.0)"

@dataclass
class ScrapedContent:
    """Represents scraped content from a URL."""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    links: List[str]
    status: str = "success"

class TechnicalManualScraper:
    """Base scraper for technical documentation."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.config.user_agent},
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
```

### URL Discovery Pattern

```python
class URLDiscovery:
    """Handles discovery of URLs to scrape."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.discovered_urls: set = set()
        self.visited_urls: set = set()
    
    async def discover_urls(self, session: aiohttp.ClientSession, 
                          start_url: str, max_depth: int = 2) -> set:
        """Discover URLs using breadth-first search."""
        queue = [(start_url, 0)]
        
        while queue:
            url, depth = queue.pop(0)
            
            if url in self.visited_urls or depth > max_depth:
                continue
            
            self.visited_urls.add(url)
            
            try:
                response = await session.get(url)
                if response.status == 200:
                    content = await response.text()
                    new_urls = self.extract_links(content, url)
                    
                    for new_url in new_urls:
                        if self.is_valid_target(new_url):
                            self.discovered_urls.add(new_url)
                            if depth < max_depth:
                                queue.append((new_url, depth + 1))
                                
            except Exception as e:
                self.logger.error(f"Error discovering URLs from {url}: {e}")
        
        return self.discovered_urls
    
    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        
        return links
    
    def is_valid_target(self, url: str) -> bool:
        """Determine if URL is a valid target for scraping."""
        parsed = urlparse(url)
        
        # Same domain check
        if parsed.netloc and parsed.netloc != urlparse(self.base_url).netloc:
            return False
        
        # Exclude certain file types
        excluded_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        # Include only documentation paths
        doc_paths = ['/docs/', '/manual/', '/guide/', '/reference/']
        if any(path in url for path in doc_paths):
            return True
        
        return False
```

## Authentication Patterns

### Session-Based Authentication

```python
class SessionAuthenticator:
    """Handles session-based authentication for scrapers."""
    
    def __init__(self, login_url: str, credentials: Dict[str, str]):
        self.login_url = login_url
        self.credentials = credentials
        self.authenticated = False
    
    async def authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate using form-based login."""
        try:
            # Get login page to extract CSRF tokens
            login_page = await session.get(self.login_url)
            login_html = await login_page.text()
            
            # Extract CSRF token if present
            csrf_token = self.extract_csrf_token(login_html)
            
            # Prepare login data
            login_data = self.credentials.copy()
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Submit login form
            response = await session.post(
                self.login_url,
                data=login_data,
                allow_redirects=True
            )
            
            # Check if authentication was successful
            self.authenticated = self.check_authentication(response)
            return self.authenticated
            
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            return False
    
    def extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from login page."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_input:
            return csrf_input.get('value')
        
        return None
    
    def check_authentication(self, response: aiohttp.ClientResponse) -> bool:
        """Check if authentication was successful."""
        # Check for authentication indicators
        if response.status == 200:
            content = response.url.path
            # Check if redirected to dashboard or profile
            if any(indicator in content for indicator in ['/dashboard', '/profile', '/home']):
                return True
        
        return False
```

### API Key Authentication

```python
class APIKeyAuthenticator:
    """Handles API key authentication."""
    
    def __init__(self, api_key: str, header_name: str = 'X-API-Key'):
        self.api_key = api_key
        self.header_name = header_name
    
    def add_auth_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add authentication headers to request."""
        headers[self.header_name] = self.api_key
        return headers
    
    async def validate_api_key(self, session: aiohttp.ClientSession, 
                             test_url: str) -> bool:
        """Validate API key by making test request."""
        try:
            headers = {self.header_name: self.api_key}
            response = await session.get(test_url, headers=headers)
            return response.status == 200
        except Exception:
            return False
```

## Rate Limiting & Throttling

### Adaptive Rate Limiting

```python
import time
from collections import deque
from datetime import datetime, timedelta

class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on server response."""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 30.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.last_adjustment = time.time()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Clean old timestamps
        cutoff = now - 60  # 1 minute window
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()
        
        # Check if we need to wait
        if len(self.request_times) >= 60:  # 60 requests per minute limit
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Apply current delay
        if self.current_delay > 0:
            await asyncio.sleep(self.current_delay)
    
    def record_request(self, response_status: int):
        """Record request and adjust rate limiting."""
        now = time.time()
        self.request_times.append(now)
        
        # Adjust delay based on response
        if response_status == 429:  # Too Many Requests
            self.current_delay = min(self.current_delay * 2, self.max_delay)
            self.error_count += 1
        elif response_status >= 500:  # Server errors
            self.current_delay = min(self.current_delay * 1.5, self.max_delay)
        elif response_status < 400:  # Success
            if self.error_count > 0:
                self.current_delay = max(self.base_delay, self.current_delay * 0.8)
                self.error_count = max(0, self.error_count - 1)
        
        self.last_adjustment = now
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status."""
        return {
            'current_delay': self.current_delay,
            'error_count': self.error_count,
            'requests_last_minute': len(self.request_times),
            'last_adjustment': self.last_adjustment
        }
```

### Request Scheduler

```python
class RequestScheduler:
    """Schedules requests with intelligent batching and prioritization."""
    
    def __init__(self, rate_limiter: AdaptiveRateLimiter):
        self.rate_limiter = rate_limiter
        self.pending_requests = asyncio.Queue()
        self.active_tasks = set()
    
    async def add_request(self, request_func, priority: int = 0):
        """Add request to scheduler."""
        await self.pending_requests.put((priority, request_func))
    
    async def run_scheduler(self):
        """Main scheduler loop."""
        while True:
            try:
                # Get next request
                priority, request_func = await asyncio.wait_for(
                    self.pending_requests.get(),
                    timeout=1.0
                )
                
                # Wait for rate limit
                await self.rate_limiter.wait_if_needed()
                
                # Execute request
                task = asyncio.create_task(self.execute_request(request_func))
                self.active_tasks.add(task)
                
                # Clean up completed tasks
                done_tasks = [t for t in self.active_tasks if t.done()]
                for task in done_tasks:
                    self.active_tasks.remove(task)
                    try:
                        await task
                    except Exception as e:
                        logging.error(f"Request failed: {e}")
                
            except asyncio.TimeoutError:
                continue
    
    async def execute_request(self, request_func):
        """Execute a single request with error handling."""
        try:
            result = await request_func()
            self.rate_limiter.record_request(200)
            return result
        except aiohttp.ClientResponseError as e:
            self.rate_limiter.record_request(e.status)
            raise
        except Exception as e:
            self.rate_limiter.record_request(500)
            raise
```

## Content Extraction Patterns

### Structured Content Parser

```python
from bs4 import BeautifulSoup
import re
from markdownify import markdownify as md

class ContentExtractor:
    """Extracts structured content from HTML."""
    
    def __init__(self):
        self.content_selectors = {
            'title': ['h1', '.title', '.page-title', '[data-testid="title"]'],
            'content': ['.content', '.main-content', '.article-body', '.documentation-content'],
            'navigation': ['.nav', '.sidebar', '.toc', '.table-of-contents'],
            'metadata': ['.meta', '.metadata', '.page-meta']
        }
    
    def extract_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = self.extract_title(soup)
        
        # Extract main content
        content_html = self.extract_main_content(soup)
        content_text = self.clean_html(content_html)
        content_markdown = md(content_html)
        
        # Extract metadata
        metadata = self.extract_metadata(soup, url)
        
        # Extract links
        links = self.extract_links(soup, url)
        
        # Extract code blocks
        code_blocks = self.extract_code_blocks(soup)
        
        return {
            'title': title,
            'content_html': content_html,
            'content_text': content_text,
            'content_markdown': content_markdown,
            'metadata': metadata,
            'links': links,
            'code_blocks': code_blocks,
            'url': url,
            'extracted_at': datetime.now().isoformat()
        }
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        for selector in self.content_selectors['title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)
        
        # Fallback to <title> tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return "Untitled"
    
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content area."""
        for selector in self.content_selectors['content']:
            content_elem = soup.select_one(selector)
            if content_elem:
                return str(content_elem)
        
        # Fallback to body
        body = soup.find('body')
        if body:
            return str(body)
        
        return ""
    
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata = {
            'url': url,
            'last_modified': None,
            'author': None,
            'tags': [],
            'section': None
        }
        
        # Extract from meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'last-modified':
                metadata['last_modified'] = content
            elif name == 'author':
                metadata['author'] = content
            elif name == 'keywords':
                metadata['tags'] = [tag.strip() for tag in content.split(',')]
        
        # Extract from Open Graph
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['og_title'] = og_title.get('content', '')
        
        return metadata
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links with context."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': text,
                'title': link.get('title', ''),
                'is_external': urlparse(absolute_url).netloc != urlparse(base_url).netloc
            })
        
        return links
    
    def extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks with syntax highlighting info."""
        code_blocks = []
        
        for code_elem in soup.find_all(['code', 'pre']):
            language = self.detect_language(code_elem)
            code_text = code_elem.get_text()
            
            code_blocks.append({
                'language': language,
                'content': code_text,
                'type': code_elem.name
            })
        
        return code_blocks
    
    def detect_language(self, code_elem) -> str:
        """Detect programming language from code element."""
        # Check for language classes
        class_names = code_elem.get('class', [])
        for class_name in class_names:
            if class_name.startswith('language-'):
                return class_name.replace('language-', '')
        
        # Check parent for language info
        parent = code_elem.parent
        if parent:
            parent_classes = parent.get('class', [])
            for class_name in parent_classes:
                if class_name.startswith('language-'):
                    return class_name.replace('language-', '')
        
        return 'text'
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML content for text extraction."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        
        return '\n'.join(cleaned_lines)
```

## Error Handling & Resilience

### Retry Strategy

```python
import random
from typing import Callable, Type, Union

class RetryStrategy:
    """Advanced retry strategy with exponential backoff and jitter."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                # Calculate delay
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                
                if self.jitter:
                    delay *= random.uniform(0.5, 1.5)
                
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
        
        raise last_exception

def should_retry(exception: Exception) -> bool:
    """Determine if exception should trigger retry."""
    retryable_errors = (
        aiohttp.ClientConnectionError,
        aiohttp.ClientTimeout,
        asyncio.TimeoutError
    )
    
    non_retryable_errors = (
        aiohttp.ClientResponseError,
        ValueError,  # Invalid URL
        PermissionError  # Authentication failed
    )
    
    if isinstance(exception, retryable_errors):
        return True
    elif isinstance(exception, non_retryable_errors):
        return False
    
    # For other exceptions, check status code if available
    if hasattr(exception, 'status'):
        return 500 <= exception.status < 600
    
    return False
```

### Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for handling service failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # Require 3 successes to close
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
```

## Data Processing & Storage

### Content Pipeline

```python
import hashlib
import json
from pathlib import Path

class ContentPipeline:
    """Pipeline for processing and storing scraped content."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_content(self, scraped_content: ScrapedContent) -> Dict[str, Any]:
        """Process scraped content through pipeline."""
        # 1. Validate content
        if not self.validate_content(scraped_content):
            raise ValueError("Invalid content")
        
        # 2. Generate content ID
        content_id = self.generate_content_id(scraped_content)
        
        # 3. Enrich metadata
        enriched_metadata = await self.enrich_metadata(scraped_content)
        
        # 4. Process content
        processed_content = self.process_content_text(scraped_content.content)
        
        # 5. Store content
        await self.store_content(content_id, {
            'id': content_id,
            'url': scraped_content.url,
            'title': scraped_content.title,
            'content': processed_content,
            'metadata': enriched_metadata,
            'scraped_at': scraped_content.metadata.get('scraped_at'),
            'links': scraped_content.links
        })
        
        return {
            'content_id': content_id,
            'status': 'processed',
            'stored_at': str(self.output_dir / f"{content_id}.json")
        }
    
    def validate_content(self, content: ScrapedContent) -> bool:
        """Validate scraped content."""
        if not content.title or not content.content:
            return False
        
        # Check for minimum content length
        if len(content.content) < 100:
            return False
        
        # Check for duplicate content
        content_hash = hashlib.md5(content.content.encode()).hexdigest()
        if self._is_duplicate(content_hash):
            return False
        
        return True
    
    def generate_content_id(self, content: ScrapedContent) -> str:
        """Generate unique ID for content."""
        url_hash = hashlib.md5(content.url.encode()).hexdigest()[:8]
        title_hash = hashlib.md5(content.title.encode()).hexdigest()[:8]
        return f"{url_hash}_{title_hash}"
    
    async def enrich_metadata(self, content: ScrapedContent) -> Dict[str, Any]:
        """Enrich content metadata."""
        metadata = content.metadata.copy()
        
        # Add content analysis
        metadata['content_analysis'] = {
            'word_count': len(content.content.split()),
            'char_count': len(content.content),
            'line_count': len(content.content.split('\n')),
            'has_code_blocks': any('```' in content.content, '<code>' in content.content)
        }
        
        # Add URL analysis
        metadata['url_analysis'] = {
            'domain': urlparse(content.url).netloc,
            'path_depth': len(urlparse(content.url).path.split('/')),
            'is_documentation': any(path in content.url for path in ['/docs/', '/manual/', '/guide/'])
        }
        
        return metadata
    
    def process_content_text(self, content: str) -> str:
        """Process and clean content text."""
        # Remove excessive whitespace
        processed = re.sub(r'\n\s*\n', '\n\n', content)
        processed = re.sub(r' +', ' ', processed)
        
        # Normalize line endings
        processed = processed.replace('\r\n', '\n').replace('\r', '\n')
        
        return processed.strip()
    
    async def store_content(self, content_id: str, content_data: Dict[str, Any]):
        """Store processed content."""
        file_path = self.output_dir / f"{content_id}.json"
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(content_data, indent=2, ensure_ascii=False))
    
    def _is_duplicate(self, content_hash: str) -> bool:
        """Check if content is a duplicate."""
        # This would typically check against a database or file index
        # For now, return False to allow all content
        return False
```

## Testing & Validation

### Test Framework

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestTechnicalManualScraper:
    """Test suite for technical manual scraper."""
    
    @pytest.fixture
    async def scraper(self):
        """Create test scraper instance."""
        config = ScrapingConfig(
            base_url="https://example.com",
            max_concurrent=2,
            request_delay=0.1  # Fast for testing
        )
        
        async with TechnicalManualScraper(config) as scraper:
            yield scraper
    
    @pytest.mark.asyncio
    async def test_url_discovery(self, scraper):
        """Test URL discovery functionality."""
        discovery = URLDiscovery("https://example.com")
        
        # Mock session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = """
        <html>
            <body>
                <a href="/docs/guide">Guide</a>
                <a href="/manual/api">API Manual</a>
                <a href="https://external.com">External</a>
            </body>
        </html>
        """
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        urls = await discovery.discover_urls(mock_session, "https://example.com")
        
        assert len(urls) == 2  # Only internal documentation links
        assert any("/docs/guide" in url for url in urls)
        assert any("/manual/api" in url for url in urls)
    
    @pytest.mark.asyncio
    async def test_content_extraction(self):
        """Test content extraction functionality."""
        extractor = ContentExtractor()
        
        html_content = """
        <html>
            <head><title>Test Manual</title></head>
            <body>
                <h1>Manual Title</h1>
                <div class="content">
                    <p>This is the main content.</p>
                    <pre><code class="language-python">print("Hello World")</code></pre>
                </div>
            </body>
        </html>
        """
        
        result = extractor.extract_content(html_content, "https://example.com/manual")
        
        assert result['title'] == "Manual Title"
        assert "main content" in result['content_text']
        assert len(result['code_blocks']) == 1
        assert result['code_blocks'][0]['language'] == 'python'
    
    @pytest.mark.asyncio
    async def test_retry_strategy(self):
        """Test retry strategy with failures."""
        retry_strategy = RetryStrategy(max_retries=2, base_delay=0.1)
        
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise aiohttp.ClientConnectionError("Connection failed")
            return "success"
        
        result = await retry_strategy.execute_with_retry(failing_func)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # Cause failures
        with pytest.raises(Exception):
            await circuit_breaker.call(self._failing_request)
        
        with pytest.raises(Exception):
            await circuit_breaker.call(self._failing_request)
        
        # Circuit should be open
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await circuit_breaker.call(self._failing_request)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Should allow one request in half-open state
        with pytest.raises(Exception):
            await circuit_breaker.call(self._failing_request)
    
    async def _failing_request(self):
        """Mock failing request."""
        raise aiohttp.ClientConnectionError("Connection failed")
```

### Integration Tests

```python
class IntegrationTestSuite:
    """Integration tests for complete scraping workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_scraping_workflow(self):
        """Test complete scraping workflow from discovery to storage."""
        config = ScrapingConfig(
            base_url="https://docs.example.com",
            max_concurrent=3,
            request_delay=0.5
        )
        
        output_dir = "/tmp/test_scraped_content"
        
        async with TechnicalManualScraper(config) as scraper:
            # 1. Discover URLs
            discovery = URLDiscovery(config.base_url)
            urls = await discovery.discover_urls(scraper.session, config.base_url)
            
            # 2. Scrape content
            scraped_content = []
            for url in list(urls)[:5]:  # Limit to first 5 URLs
                try:
                    content = await scraper.scrape_url(url)
                    scraped_content.append(content)
                except Exception as e:
                    logging.warning(f"Failed to scrape {url}: {e}")
            
            # 3. Process content
            pipeline = ContentPipeline(output_dir)
            processed_results = []
            
            for content in scraped_content:
                try:
                    result = await pipeline.process_content(content)
                    processed_results.append(result)
                except Exception as e:
                    logging.error(f"Failed to process content: {e}")
            
            # 4. Verify results
            assert len(processed_results) > 0
            
            # Check that files were created
            output_path = Path(output_dir)
            assert output_path.exists()
            json_files = list(output_path.glob("*.json"))
            assert len(json_files) > 0
            
            # Verify content structure
            with open(json_files[0]) as f:
                content_data = json.load(f)
                assert 'id' in content_data
                assert 'title' in content_data
                assert 'content' in content_data
                assert 'metadata' in content_data
```

## Best Practices

### 1. Respect robots.txt
```python
import urllib.robotparser

def check_robots_txt(base_url: str, user_agent: str = '*') -> bool:
    """Check if scraping is allowed by robots.txt."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    rp.read()
    return rp.can_fetch(user_agent, base_url)
```

### 2. Use Proper Headers
```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; TechnicalScraper/1.0; research@xoe-novai.org)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache'
}
```

### 3. Handle Different Content Types
```python
async def handle_content_type(response: aiohttp.ClientResponse, content: bytes):
    """Handle different content types appropriately."""
    content_type = response.headers.get('Content-Type', '').lower()
    
    if 'text/html' in content_type:
        return content.decode('utf-8', errors='ignore')
    elif 'application/json' in content_type:
        return json.loads(content.decode('utf-8'))
    elif 'text/plain' in content_type:
        return content.decode('utf-8', errors='ignore')
    else:
        # Handle binary content
        return content
```

### 4. Monitor and Log
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = 'scraper.log'):
    """Set up comprehensive logging for scraper."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

This comprehensive guide provides patterns for building robust technical manual scrapers that can handle real-world challenges while maintaining good performance and reliability.

---

**Last Updated**: February 15, 2026
**Version**: v1.0.0
**Maintainer**: Xoe-NovAi Foundation Team