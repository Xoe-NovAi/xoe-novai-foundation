"""
Technical Manual Scraper - Main orchestrator for scraping jobs.

Manages job queue, execution, deduplication, and result storage.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge.schemas.scraping_job_schema import (
    ScrapingJobSchema, ScrapingJobResult, JobStatus, JobPriority
)
from scrapers.github_scraper import GitHubScraper
from scrapers.html_scraper import HTMLScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScrapingQueueManager:
    """Manages the scraping job queue."""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize queue manager.
        
        Args:
            base_dir: Base directory for storing jobs and results
        """
        self.base_dir = Path(base_dir or Path.cwd())
        self.jobs_dir = self.base_dir / "data" / "scraping_jobs"
        self.results_dir = self.base_dir / "data" / "scraping_results"
        
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory queue (priority queue)
        self.pending_jobs: List[ScrapingJobSchema] = []
        self.active_jobs: Dict[str, ScrapingJobSchema] = {}
        self.completed_jobs: List[ScrapingJobResult] = []
        
        # Deduplication tracking
        self.seen_hashes: Dict[str, str] = {}  # hash -> service
        
        logger.info(f"Initialized queue manager with base_dir={self.base_dir}")
    
    def add_job(self, job: ScrapingJobSchema) -> None:
        """Add a job to the queue."""
        self.pending_jobs.append(job)
        self.pending_jobs.sort(key=lambda j: j.priority.value)  # Sort by priority
        logger.info(f"Added job {job.id} (priority {job.priority.name})")
    
    def get_next_job(self) -> Optional[ScrapingJobSchema]:
        """Get the next job from the queue."""
        if not self.pending_jobs:
            return None
        return self.pending_jobs.pop(0)
    
    def mark_active(self, job: ScrapingJobSchema) -> None:
        """Mark a job as in progress."""
        job.status = JobStatus.IN_PROGRESS
        job.started_at = datetime.utcnow()
        self.active_jobs[job.id] = job
        logger.info(f"Marked {job.id} as IN_PROGRESS")
    
    def mark_completed(self, job: ScrapingJobSchema, result: ScrapingJobResult) -> None:
        """Mark a job as completed."""
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.success = result.success
        
        if job.id in self.active_jobs:
            del self.active_jobs[job.id]
        
        self.completed_jobs.append(result)
        logger.info(f"Marked {job.id} as COMPLETED (success={result.success})")
    
    def mark_failed(self, job: ScrapingJobSchema, error: str) -> None:
        """Mark a job as failed."""
        job.last_error = error
        
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.RETRYING
            self.pending_jobs.append(job)  # Re-queue for retry
            logger.warning(f"Job {job.id} failed, re-queued (attempt {job.retry_count})")
        else:
            job.status = JobStatus.FAILED
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]
            logger.error(f"Job {job.id} failed after {job.max_retries} retries: {error}")
    
    def check_dedup(self, content_hash: str) -> bool:
        """Check if content hash already exists."""
        return content_hash in self.seen_hashes
    
    def register_hash(self, content_hash: str, service: str) -> None:
        """Register a content hash."""
        self.seen_hashes[content_hash] = service
        logger.debug(f"Registered hash {content_hash[:8]}... for {service}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "pending": len(self.pending_jobs),
            "active": len(self.active_jobs),
            "completed": len(self.completed_jobs),
            "total": len(self.pending_jobs) + len(self.active_jobs) + len(self.completed_jobs),
            "success_rate": (
                sum(1 for j in self.completed_jobs if j.success) / len(self.completed_jobs)
                if self.completed_jobs else 0
            ),
        }
    
    def save_state(self) -> None:
        """Save queue state to disk (for persistence)."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self.get_stats(),
            "seen_hashes": self.seen_hashes,
            "completed_count": len(self.completed_jobs),
        }
        
        state_file = self.results_dir / "queue_state.json"
        state_file.write_text(json.dumps(state, indent=2))
        logger.info(f"Saved queue state to {state_file}")


class TechnicalManualScraper:
    """Main scraper orchestrator."""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize scraper.
        
        Args:
            base_dir: Base directory for project
        """
        self.base_dir = Path(base_dir or Path.cwd())
        self.queue = ScrapingQueueManager(self.base_dir)
        self.scrapers: Dict[str, Any] = {}  # Template -> scraper class
        
        logger.info("Initialized TechnicalManualScraper")
    
    def register_scraper(self, template: str, scraper_class: type) -> None:
        """Register a scraper template."""
        self.scrapers[template] = scraper_class
        logger.info(f"Registered scraper template: {template}")
    
    async def execute_job(self, job: ScrapingJobSchema) -> ScrapingJobResult:
        """
        Execute a single scraping job.
        
        Args:
            job: Job to execute
        
        Returns:
            Job result
        """
        logger.info(f"Executing job {job.id} ({job.service})")
        self.queue.mark_active(job)
        
        try:
            content_items = []
            output_files = []
            total_size_kb = 0
            urls_processed = 0
            urls_failed = 0
            
            # Handle MIXED template (both GitHub and HTML)
            if job.scraper_template.value == "mixed":
                logger.info(f"Using MIXED scraper for {job.service}")
                
                # Split URLs by type
                github_urls = [u for u in job.urls if "github.com" in u]
                html_urls = [u for u in job.urls if "github.com" not in u]
                
                # Get config
                github_config = job.config.get("github_config", {})
                html_config = job.config.get("html_config", {})
                
                # Try GitHub scraper first
                if github_urls:
                    logger.info(f"  GitHub phase: {len(github_urls)} URLs")
                    try:
                        github_scraper = GitHubScraper(
                            service=job.service,
                            user_agent=job.user_agent,
                            timeout=job.timeout_seconds,
                            rate_limit_delay=job.rate_limit_delay_seconds,
                        )
                        github_items = await github_scraper.scrape(github_urls, github_config)
                        content_items.extend(github_items)
                        stats = github_scraper.get_stats()
                        urls_processed += stats["urls_processed"]
                        urls_failed += stats["urls_failed"]
                        logger.info(f"  GitHub phase complete: {len(github_items)} items")
                    except Exception as e:
                        logger.warning(f"  GitHub scraper failed: {e}")
                        urls_failed += len(github_urls)
                
                # Try HTML scraper
                if html_urls:
                    logger.info(f"  HTML phase: {len(html_urls)} URLs")
                    try:
                        html_scraper = HTMLScraper(
                            service=job.service,
                            user_agent=job.user_agent,
                            timeout=job.timeout_seconds,
                            rate_limit_delay=job.rate_limit_delay_seconds,
                        )
                        html_items = await html_scraper.scrape(html_urls, html_config)
                        content_items.extend(html_items)
                        stats = html_scraper.get_stats()
                        urls_processed += stats["urls_processed"]
                        urls_failed += stats["urls_failed"]
                        logger.info(f"  HTML phase complete: {len(html_items)} items")
                    except Exception as e:
                        logger.warning(f"  HTML scraper failed: {e}")
                        urls_failed += len(html_urls)
            else:
                # Single scraper template
                scraper_class = self.scrapers.get(job.scraper_template.value)
                if not scraper_class:
                    raise ValueError(f"Unknown scraper template: {job.scraper_template}")
                
                scraper = scraper_class(
                    service=job.service,
                    user_agent=job.user_agent,
                    timeout=job.timeout_seconds,
                    rate_limit_delay=job.rate_limit_delay_seconds,
                    max_retries=job.max_retries,
                )
                
                logger.info(f"Starting scrape for {job.service} with template {job.scraper_template}")
                content_items = await scraper.scrape(job.urls, job.config)
                
                stats = scraper.get_stats()
                urls_processed = stats["urls_processed"]
                urls_failed = stats["urls_failed"]
            
            if not content_items:
                raise ValueError("No content scraped")
            
            # Save content and check for duplicates
            output_dir = Path(job.output_path or f"knowledge/technical_manuals/{job.service}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for content in content_items:
                # Check deduplication
                if self.queue.check_dedup(content.content_hash):
                    logger.debug(f"Duplicate content detected: {content.content_hash[:8]}...")
                    continue
                
                # Create a temporary scraper just for saving
                temp_scraper = GitHubScraper(service=job.service)
                filepath = await temp_scraper.save_content(content, output_dir)
                output_files.append(str(filepath))
                
                # Register hash
                self.queue.register_hash(content.content_hash, job.service)
                
                total_size_kb += content.size_kb
            
            # Build result
            result = ScrapingJobResult(
                job_id=job.id,
                service=job.service,
                success=True,
                status=JobStatus.COMPLETED,
                total_content_kb=total_size_kb,
                sections=len(output_files),
                output_files=output_files,
                duration_seconds=0,
                urls_processed=urls_processed,
                urls_failed=urls_failed,
            )
            
            # Update job
            job.content_size_kb = total_size_kb
            job.dedup_hash = (
                hashlib.sha256(
                    "".join(output_files).encode()
                ).hexdigest()
            )
            
            self.queue.mark_completed(job, result)
            logger.info(f"Job {job.id} completed successfully ({total_size_kb:.2f} KB)")
            
            return result
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}", exc_info=True)
            result = ScrapingJobResult(
                job_id=job.id,
                service=job.service,
                success=False,
                status=JobStatus.FAILED,
                total_content_kb=0,
                sections=0,
                output_files=[],
                duration_seconds=0,
                urls_processed=0,
                errors=[str(e)],
            )
            
            self.queue.mark_failed(job, str(e))
            return result
    
    async def execute_queue(self, max_concurrent: int = 1, pause_every_n: int = 2):
        """
        Execute all jobs in queue.
        
        Args:
            max_concurrent: Maximum concurrent jobs
            pause_every_n: Pause after this many jobs for review
        """
        jobs_processed = 0
        
        while self.queue.pending_jobs:
            job = self.queue.get_next_job()
            if not job:
                break
            
            # Execute job
            result = await self.execute_job(job)
            jobs_processed += 1
            
            # Pause for review every N jobs
            if jobs_processed % pause_every_n == 0:
                logger.info(f"\n{'='*70}")
                logger.info(f"PAUSE CHECKPOINT: {jobs_processed} jobs completed")
                logger.info(f"{'='*70}")
                logger.info(f"Queue stats: {self.queue.get_stats()}")
                logger.info(f"Last result: {result.service} - Success: {result.success}")
                logger.info(f"{'='*70}\n")
                
                # Save state
                self.queue.save_state()
                
                # Pause execution
                print("\n" + "="*70)
                print(f"PAUSE CHECKPOINT: {jobs_processed} jobs completed")
                print("="*70)
                print(f"Service: {result.service}")
                print(f"Success: {result.success}")
                print(f"Content: {result.total_content_kb:.2f} KB in {result.sections} sections")
                if result.errors:
                    print(f"Errors: {result.errors}")
                print(f"Queue stats: {self.queue.get_stats()}")
                print("="*70)
                print("\nReady for review and adjustment before continuing...")
                print("Send 'continue' or 'adjust' command or press Enter to proceed.")
                
                await asyncio.sleep(1)  # Brief pause for user to see message
                break  # Pause execution
        
        # Save final state
        self.queue.save_state()
        
        stats = self.queue.get_stats()
        logger.info(f"Execution complete. Stats: {stats}")
    
    def print_status(self) -> None:
        """Print current queue and result status."""
        stats = self.queue.get_stats()
        print("\n" + "="*70)
        print("SCRAPING QUEUE STATUS")
        print("="*70)
        print(f"Pending jobs: {stats['pending']}")
        print(f"Active jobs: {stats['active']}")
        print(f"Completed jobs: {stats['completed']}")
        print(f"Success rate: {stats['success_rate']*100:.1f}%")
        print(f"Total jobs: {stats['total']}")
        print("="*70 + "\n")
