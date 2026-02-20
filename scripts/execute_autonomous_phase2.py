#!/usr/bin/env python3
"""
Autonomous Phase 2-4 Execution: Mixed GitHub + HTML Scraping

Strategy:
- Use mixed GitHub + HTML scrapers for comprehensive coverage
- Run autonomously without pausing between jobs
- Track metrics and adjust approach dynamically
- Log results for post-execution analysis
"""

import anyio
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from technical_manual_scraper import TechnicalManualScraper
from scrapers.github_scraper import GitHubScraper
from scrapers.html_scraper import HTMLScraper
from knowledge.schemas.scraping_job_schema import (
    ScrapingJobSchema,
    ScraperTemplate,
    JobPriority,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/scraping_execution.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AutonomousScrapingExecutor:
    """Manages autonomous scraping with dynamic adjustments."""

    # Service configurations with sources
    PHASE_2_SERVICES = [
        # Redis - CRITICAL
        {
            "id": "scrape-redis-20260217-001",
            "service": "redis",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/redis/redis"],
                "html": ["https://redis.io/docs/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 30,
                    "allowed_domains": ["redis.io"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
        # PostgreSQL - CRITICAL
        {
            "id": "scrape-postgresql-20260217-001",
            "service": "postgresql",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/postgres/postgres"],
                "html": ["https://www.postgresql.org/docs/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 50,
                    "allowed_domains": ["postgresql.org"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
        # Docker - CRITICAL
        {
            "id": "scrape-docker-20260217-001",
            "service": "docker",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/moby/moby"],
                "html": ["https://docs.docker.com/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 40,
                    "allowed_domains": ["docker.com"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
        # Podman - CRITICAL
        {
            "id": "scrape-podman-20260217-001",
            "service": "podman",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/containers/podman"],
                "html": ["https://podman.io/docs/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 30,
                    "allowed_domains": ["podman.io"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
        # Prometheus - CRITICAL
        {
            "id": "scrape-prometheus-20260217-001",
            "service": "prometheus",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/prometheus/prometheus"],
                "html": ["https://prometheus.io/docs/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 35,
                    "allowed_domains": ["prometheus.io"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
        # Grafana - CRITICAL
        {
            "id": "scrape-grafana-20260217-001",
            "service": "grafana",
            "priority": JobPriority.CRITICAL,
            "sources": {
                "github": ["https://github.com/grafana/grafana"],
                "html": ["https://grafana.com/docs/"],
            },
            "config": {
                "github": {
                    "max_depth": 2,
                    "include_readme": True,
                },
                "html": {
                    "max_depth": 2,
                    "max_pages": 40,
                    "allowed_domains": ["grafana.com"],
                    "include_patterns": ["/docs/"],
                },
            },
        },
    ]

    def __init__(self, base_dir: Path = None):
        """Initialize executor."""
        self.base_dir = Path(base_dir or Path.cwd())
        self.scraper = TechnicalManualScraper(base_dir=self.base_dir)
        self.scraper.register_scraper("github", GitHubScraper)
        self.scraper.register_scraper("html", HTMLScraper)

        self.execution_stats = {
            "total_jobs": 0,
            "completed": 0,
            "succeeded": 0,
            "failed": 0,
            "total_content_kb": 0.0,
            "start_time": datetime.utcnow(),
            "results": [],
        }

        logger.info("Initialized AutonomousScrapingExecutor")

    def create_mixed_jobs(self, service_specs: List[Dict[str, Any]]) -> None:
        """
        Create jobs with mixed GitHub + HTML scrapers.

        Args:
            service_specs: List of service specifications
        """
        for spec in service_specs:
            job = ScrapingJobSchema(
                id=spec["id"],
                service=spec["service"],
                priority=spec["priority"],
                urls=(spec["sources"]["github"] + spec["sources"]["html"]),
                scraper_template=ScraperTemplate.MIXED,
                config={
                    "github_config": spec["config"].get("github", {}),
                    "html_config": spec["config"].get("html", {}),
                },
                output_path=str(
                    self.base_dir / "knowledge" / "technical_manuals" / spec["service"]
                ),
            )
            self.scraper.queue.add_job(job)
            logger.info(f"Queued mixed job for {spec['service']}")

        self.execution_stats["total_jobs"] = len(service_specs)

    async def execute_all_jobs(self) -> Dict[str, Any]:
        """
        Execute all jobs autonomously.

        Returns:
            Execution summary
        """
        logger.info(
            f"Starting autonomous execution of {len(self.scraper.queue.pending_jobs)} jobs"
        )

        while self.scraper.queue.pending_jobs:
            job = self.scraper.queue.get_next_job()
            if not job:
                break

            logger.info(f"Executing {job.service}...")
            result = await self.scraper.execute_job(job)

            # Track stats
            self.execution_stats["completed"] += 1
            if result.success:
                self.execution_stats["succeeded"] += 1
                self.execution_stats["total_content_kb"] += result.total_content_kb
            else:
                self.execution_stats["failed"] += 1

            self.execution_stats["results"].append(
                {
                    "service": result.service,
                    "success": result.success,
                    "content_kb": result.total_content_kb,
                    "sections": result.sections,
                }
            )

            # Rate limiting between jobs
            await asyncio.sleep(2)

        self.execution_stats["end_time"] = datetime.utcnow()
        duration = (
            self.execution_stats["end_time"] - self.execution_stats["start_time"]
        ).total_seconds()
        self.execution_stats["duration_seconds"] = duration

        logger.info(f"Execution complete in {duration:.1f}s")
        return self.execution_stats

    def save_execution_report(self) -> Path:
        """Save execution report to disk."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_stats": {
                "total_jobs": self.execution_stats["total_jobs"],
                "completed": self.execution_stats["completed"],
                "succeeded": self.execution_stats["succeeded"],
                "failed": self.execution_stats["failed"],
                "total_content_kb": self.execution_stats["total_content_kb"],
                "duration_seconds": self.execution_stats.get("duration_seconds", 0),
            },
            "results": self.execution_stats["results"],
        }

        report_path = (
            self.base_dir / "data" / "scraping_results" / "execution_report.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2))

        logger.info(f"Saved execution report to {report_path}")
        return report_path

    def print_summary(self) -> None:
        """Print execution summary."""
        duration = self.execution_stats.get("duration_seconds", 0)

        print("\n" + "=" * 70)
        print("AUTONOMOUS EXECUTION COMPLETE")
        print("=" * 70)
        print(f"Total jobs: {self.execution_stats['total_jobs']}")
        print(f"Completed: {self.execution_stats['completed']}")
        print(f"Succeeded: {self.execution_stats['succeeded']}")
        print(f"Failed: {self.execution_stats['failed']}")
        print(f"Total content: {self.execution_stats['total_content_kb']:.2f} KB")
        print(f"Duration: {duration:.1f} seconds ({duration / 60:.1f} minutes)")
        print("=" * 70)

        print("\nResults by service:")
        print("-" * 70)
        for result in self.execution_stats["results"]:
            status = "✓" if result["success"] else "✗"
            print(
                f"{status} {result['service']:15} {result['content_kb']:8.2f} KB {result['sections']:3} sections"
            )
        print("-" * 70 + "\n")


async def main():
    """Main execution function."""
    executor = AutonomousScrapingExecutor()

    # Create mixed jobs for Phase 2 (CRITICAL services)
    logger.info("Creating Phase 2 jobs (CRITICAL services)")
    executor.create_mixed_jobs(executor.PHASE_2_SERVICES)

    # Execute all jobs
    stats = await executor.execute_all_jobs()

    # Save report
    executor.save_execution_report()

    # Print summary
    executor.print_summary()

    return stats


if __name__ == "__main__":
    stats = anyio.run(main)
