#!/usr/bin/env python3
"""
Retry failed services from Phase 3-4 now that Playwright is installed.

Retries: Qdrant (Phase 3), SQLAlchemy (Phase 4)
"""

import anyio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge.schemas.scraping_job_schema import (
    ScrapingJobSchema,
    JobStatus,
    JobPriority,
)
from technical_manual_scraper import TechnicalManualScraper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


RETRY_SERVICES = {
    "Qdrant": {
        "urls": [
            "https://github.com/qdrant/qdrant",
            "https://qdrant.tech/documentation/",
        ],
        "priority": JobPriority.HIGH,
        "github_config": {
            "max_depth": 3,
            "include_patterns": ["README", "docs/", "guide/"],
        },
        "html_config": {
            "max_depth": 4,
            "max_pages": 80,
            "include_patterns": ["documentation", "guide", "api"],
        },
    },
    "SQLAlchemy": {
        "urls": [
            "https://github.com/sqlalchemy/sqlalchemy",
            "https://docs.sqlalchemy.org/",
        ],
        "priority": JobPriority.MEDIUM,
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 100,
            "include_patterns": ["documentation", "tutorial"],
        },
    },
}


class RetryExecutor:
    """Manages retry of failed services."""

    def __init__(self, result_dir: str = "data/scraping_results"):
        """Initialize executor."""
        self.result_dir = Path(result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = TechnicalManualScraper()
        self.execution_stats = {
            "phase": "Retry",
            "start_time": datetime.now().isoformat(),
            "services": [],
            "total_services": 0,
            "successful": 0,
            "failed": 0,
            "total_content_kb": 0,
        }

    def generate_job_id(self, service_name: str) -> str:
        """Generate a unique job ID."""
        service_slug = service_name.lower().replace("-", "_")
        date_str = datetime.now().strftime("%Y%m%d")
        return f"scrape-{service_slug}-{date_str}-retry"

    async def execute_retries(self):
        """Execute retry jobs."""
        logger.info("Starting retry execution for failed services")

        jobs = []
        for service, config in RETRY_SERVICES.items():
            job = ScrapingJobSchema(
                id=self.generate_job_id(service),
                service=service,
                urls=config["urls"],
                scraper_template="mixed",
                config={
                    "github_config": config["github_config"],
                    "html_config": config["html_config"],
                },
                priority=config["priority"],
                output_path=f"knowledge/technical_manuals/{service}",
            )
            jobs.append(job)
            self.scraper.queue.add_job(job)

        logger.info(f"Created {len(jobs)} retry jobs")

        start_time = datetime.now()
        for job in jobs:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"RETRY: {job.service}")
            logger.info(f"{'=' * 60}")

            try:
                result = await self.scraper.execute_job(job)

                if result.success:
                    logger.info(f"✓ {job.service} RETRY SUCCESSFUL!")
                    logger.info(f"  - Size: {result.total_content_kb:.2f} KB")
                    logger.info(f"  - Files: {result.sections}")
                    self.execution_stats["successful"] += 1
                    self.execution_stats["total_content_kb"] += result.total_content_kb
                else:
                    logger.error(f"✗ {job.service} retry still failing")
                    self.execution_stats["failed"] += 1

                self.execution_stats["services"].append(
                    {
                        "service": job.service,
                        "success": result.success,
                        "size_kb": result.total_content_kb,
                        "files": result.sections,
                    }
                )

            except Exception as e:
                logger.error(f"✗ {job.service} retry failed: {e}")
                self.execution_stats["failed"] += 1

        duration = (datetime.now() - start_time).total_seconds()
        self.execution_stats["end_time"] = datetime.now().isoformat()
        self.execution_stats["duration_seconds"] = duration
        self.execution_stats["total_services"] = len(jobs)

        report_path = self.result_dir / "retry_execution_report.json"
        with open(report_path, "w") as f:
            json.dump(self.execution_stats, f, indent=2)

        logger.info(f"\nRetry report saved to {report_path}")
        return self.execution_stats

    def print_summary(self):
        """Print execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("RETRY EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Duration: {self.execution_stats.get('duration_seconds', 0):.1f}s")
        logger.info(
            f"Successful: {self.execution_stats['successful']}/{self.execution_stats['total_services']}"
        )
        logger.info(
            f"Failed: {self.execution_stats['failed']}/{self.execution_stats['total_services']}"
        )
        logger.info(f"Total content: {self.execution_stats['total_content_kb']:.2f} KB")

        for service in self.execution_stats["services"]:
            if service["success"]:
                logger.info(
                    f"✓ {service['service']:25} {service['size_kb']:8.2f} KB  {service['files']:3} files"
                )
            else:
                logger.info(f"✗ {service['service']:25} FAILED")
        logger.info("=" * 60)


async def main():
    """Main execution function."""
    executor = RetryExecutor()

    try:
        stats = await executor.execute_retries()
        executor.print_summary()

        if executor.execution_stats["failed"] == 0:
            logger.info("\n✓ All retries successful!")
            return 0
        else:
            logger.warning(
                f"\n⚠ {executor.execution_stats['failed']} retries still failing"
            )
            return 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = anyio.run(main)
    exit(exit_code)
