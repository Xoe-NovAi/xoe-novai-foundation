"""
Scraping Job Schema - Defines job structure for technical manual scraping.

Uses Pydantic v2 for validation, serialization, and type safety.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    """Job lifecycle states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobPriority(int, Enum):
    """Priority levels for job execution."""
    CRITICAL = 1  # Phase 5A-5E foundation services
    HIGH = 2      # Phase 6 AI/ML services
    MEDIUM = 3    # Phase 7-8 infrastructure


class ScraperTemplate(str, Enum):
    """Types of scraper templates."""
    GITHUB = "github"           # Clone repo + extract /docs/
    HTML = "html"               # crawl4ai-based website crawling
    OPENAPI = "openapi"         # Swagger/OpenAPI spec parsing
    PYPI = "pypi"               # PyPI package + bundled docs
    MIXED = "mixed"             # Multiple formats for same service


class ContentFormat(str, Enum):
    """Output content formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    TEXT = "text"


class ScrapingJobSchema(BaseModel):
    """Main scraping job definition."""
    
    # Identifiers
    id: str = Field(..., description="Unique job ID (e.g., 'scrape-redis-20260216-001')")
    service: str = Field(..., description="Service name (e.g., 'redis', 'postgresql')")
    
    # Execution config
    priority: JobPriority = Field(default=JobPriority.MEDIUM, description="Job priority")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    
    # Sources
    urls: List[str] = Field(..., description="Primary and fallback URLs to scrape")
    fallback_urls: Optional[List[str]] = Field(
        default=None, 
        description="Additional fallback sources if primary fails"
    )
    
    # Scraping strategy
    scraper_template: ScraperTemplate = Field(..., description="Which scraper to use")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template-specific config (depth limit, selectors, etc.)"
    )
    
    # Output format
    output_format: ContentFormat = Field(default=ContentFormat.MARKDOWN, description="Output format")
    output_path: Optional[str] = Field(
        default=None,
        description="Where to store scraped content (e.g., knowledge/technical_manuals/redis/)"
    )
    
    # Content handling
    dedup_hash: Optional[str] = Field(
        default=None,
        description="SHA256 hash of content for deduplication"
    )
    content_size_kb: Optional[float] = Field(
        default=None,
        description="Size of scraped content in KB (for validation)"
    )
    
    # Retry & error handling
    retry_count: int = Field(default=0, description="Number of retries performed")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    last_error: Optional[str] = Field(default=None, description="Last error message if failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation time")
    started_at: Optional[datetime] = Field(default=None, description="When execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When execution finished")
    
    # Metadata
    user_agent: str = Field(
        default="XNAi-Foundation/1.0 (https://github.com/xnai-foundation/xoe-novai)",
        description="User-Agent header for HTTP requests"
    )
    timeout_seconds: int = Field(default=30, description="Request timeout")
    rate_limit_delay_seconds: float = Field(default=2.0, description="Delay between requests")
    
    # Quality metrics (populated after execution)
    success: bool = Field(default=False, description="Whether job succeeded")
    sections_extracted: int = Field(default=0, description="Number of sections extracted")
    links_found: int = Field(default=0, description="Number of links discovered")
    images_found: int = Field(default=0, description="Number of images found")
    code_blocks_found: int = Field(default=0, description="Number of code blocks extracted")
    
    @field_validator('priority', mode='before')
    def validate_priority(cls, v):
        """Allow int or enum."""
        if isinstance(v, int):
            return JobPriority(v)
        return v
    
    class Config:
        """Pydantic config."""
        use_enum_values = False  # Keep enum objects, not strings


class ScrapingJobResult(BaseModel):
    """Result of a completed scraping job."""
    
    job_id: str
    service: str
    success: bool
    status: JobStatus
    
    # Content metadata
    total_content_kb: float = Field(description="Total content size")
    sections: int = Field(description="Number of sections/documents")
    
    # Quality metrics
    dedup_hash: Optional[str] = Field(default=None, description="Content hash for deduplication")
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score (0-1)"
    )
    
    # Details
    output_files: List[str] = Field(description="List of output files created")
    errors: Optional[List[str]] = Field(default=None, description="Any errors encountered")
    warnings: Optional[List[str]] = Field(default=None, description="Warnings during scraping")
    
    # Execution details
    duration_seconds: float = Field(description="How long the job took")
    urls_processed: int = Field(description="Number of URLs processed")
    urls_failed: int = Field(default=0, description="Number of URLs that failed")
    
    # Timestamps
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        use_enum_values = False


class ServiceMetadata(BaseModel):
    """Metadata for a service's documentation."""
    
    service_name: str
    priority: JobPriority
    
    # Version tracking
    version: str = Field(description="Documentation version (e.g., 'redis-7.2')")
    scrape_date: datetime
    source_urls: List[str] = Field(description="URLs where content came from")
    
    # Content metrics
    total_size_kb: float
    section_count: int
    estimated_read_time_minutes: float
    
    # Index metadata
    keywords: List[str] = Field(default_factory=list, description="Key topics covered")
    languages: List[str] = Field(default_factory=lambda: ["en"], description="Languages covered")
    
    # Quality
    completeness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How complete the documentation is (0-1)"
    )
    accuracy_verified: bool = Field(default=False, description="Has accuracy been spot-checked?")
    
    # Related services (for cross-referencing)
    related_services: List[str] = Field(default_factory=list, description="Services this depends on")
    
    class Config:
        """Pydantic config."""
        use_enum_values = False


class QueueStats(BaseModel):
    """Statistics about the scraping queue."""
    
    total_jobs: int
    pending: int
    in_progress: int
    completed: int
    failed: int
    
    total_content_kb: float = Field(description="Total scraped content size")
    avg_job_duration_seconds: float = Field(description="Average job duration")
    success_rate: float = Field(ge=0.0, le=1.0, description="Percentage of successful jobs")
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)
