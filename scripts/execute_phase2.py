#!/usr/bin/env python3
"""
Execute Phase 2 scraping: Redis and PostgreSQL (first 2 CRITICAL services).

This script:
1. Creates scraping jobs for Redis and PostgreSQL
2. Executes them with pause after each for review
3. Saves results for analysis
"""

import anyio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from technical_manual_scraper import TechnicalManualScraper
from scrapers.github_scraper import GitHubScraper
from knowledge.schemas.scraping_job_schema import (
    ScrapingJobSchema,
    ScraperTemplate,
    JobPriority,
)


async def main():
    """Run Phase 2 scraping."""

    # Initialize scraper
    base_dir = Path(__file__).parent.parent
    scraper = TechnicalManualScraper(base_dir=base_dir)

    # Register GitHub scraper
    scraper.register_scraper("github", GitHubScraper)

    # Create first 2 jobs (CRITICAL priority)
    jobs = [
        {
            "id": "scrape-redis-20260216-001",
            "service": "redis",
            "priority": JobPriority.CRITICAL,
            "urls": [
                "https://github.com/redis/redis",
            ],
            "scraper_template": ScraperTemplate.GITHUB,
            "config": {
                "max_depth": 3,
                "include_readme": True,
                "filter_patterns": ["*.md"],
            },
            "output_path": str(base_dir / "knowledge" / "technical_manuals" / "redis"),
        },
        {
            "id": "scrape-postgresql-20260216-001",
            "service": "postgresql",
            "priority": JobPriority.CRITICAL,
            "urls": [
                "https://github.com/postgres/postgres",
            ],
            "scraper_template": ScraperTemplate.GITHUB,
            "config": {
                "max_depth": 2,  # PostgreSQL docs can be deep
                "include_readme": True,
                "filter_patterns": ["*.md"],
            },
            "output_path": str(
                base_dir / "knowledge" / "technical_manuals" / "postgresql"
            ),
        },
    ]

    # Add jobs to queue
    for job_spec in jobs:
        job = ScrapingJobSchema(
            id=job_spec["id"],
            service=job_spec["service"],
            priority=job_spec["priority"],
            urls=job_spec["urls"],
            scraper_template=job_spec["scraper_template"],
            config=job_spec["config"],
            output_path=job_spec["output_path"],
        )
        scraper.queue.add_job(job)
        print(f"✓ Added job: {job.id}")

    print("\n" + "=" * 70)
    print("PHASE 2: Scraping First 2 CRITICAL Services")
    print("=" * 70)
    print("Services: Redis, PostgreSQL")
    print("Priority: CRITICAL")
    print("Strategy: Pause after each job for review")
    print("=" * 70 + "\n")

    # Execute with pause every 1 job (so we pause after each)
    await scraper.execute_queue(max_concurrent=1, pause_every_n=1)

    # Print final status
    scraper.print_status()

    # Show completed results
    if scraper.queue.completed_jobs:
        print("\nCOMPLETED JOB RESULTS:")
        print("=" * 70)
        for result in scraper.queue.completed_jobs:
            print(f"Service: {result.service}")
            print(f"Success: {result.success}")
            print(
                f"Content: {result.total_content_kb:.2f} KB in {result.sections} sections"
            )
            if result.errors:
                print(f"Errors: {result.errors}")
            print(f"Duration: {result.duration_seconds:.2f} seconds")
            print(f"Output files: {len(result.output_files)}")
            print("-" * 70)


if __name__ == "__main__":
    anyio.run(main)
