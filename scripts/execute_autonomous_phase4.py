#!/usr/bin/env python3
"""
Autonomous execution script for Phase 4 technical manual scraping.

MEDIUM priority services.
Executes: OpenTelemetry, Jaeger, FastAPI, redis-py, SQLAlchemy
"""

import anyio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
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


# Phase 4 Configuration: 5 MEDIUM priority services
PHASE_4_SERVICES = {
    "OpenTelemetry": {
        "urls": [
            "https://github.com/open-telemetry/opentelemetry-python",
            "https://opentelemetry.io/docs/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 60,
            "include_patterns": ["documentation", "guide"],
        },
    },
    "Jaeger": {
        "urls": [
            "https://github.com/jaegertracing/jaeger",
            "https://www.jaegertracing.io/docs/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 50,
            "include_patterns": ["documentation", "guide"],
        },
    },
    "FastAPI": {
        "urls": [
            "https://github.com/tiangolo/fastapi",
            "https://fastapi.tiangolo.com/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 80,
            "include_patterns": ["documentation", "guide", "tutorial"],
        },
    },
    "redis-py": {
        "urls": [
            "https://github.com/redis/redis-py",
            "https://redis-py.readthedocs.io/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 40,
            "include_patterns": ["documentation", "api"],
        },
    },
    "SQLAlchemy": {
        "urls": [
            "https://github.com/sqlalchemy/sqlalchemy",
            "https://docs.sqlalchemy.org/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 100,
            "include_patterns": ["documentation", "tutorial"],
        },
    },
}


class AutonomousScrapingExecutor:
    """Manages autonomous execution of Phase 4 scraping jobs."""

    def __init__(self, result_dir: str = "data/scraping_results"):
        """Initialize executor."""
        self.result_dir = Path(result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = TechnicalManualScraper()
        self.job_counter = 0
        self.execution_stats = {
            "phase": "Phase 4",
            "start_time": datetime.now().isoformat(),
            "services": [],
            "total_services": 0,
            "successful": 0,
            "failed": 0,
            "total_content_kb": 0,
        }

    def generate_job_id(self, service_name: str) -> str:
        """Generate a unique job ID."""
        self.job_counter += 1
        service_slug = service_name.lower().replace("-", "_")
        date_str = datetime.now().strftime("%Y%m%d")
        return f"scrape-{service_slug}-{date_str}-{self.job_counter:03d}"

    async def execute_all_jobs(self):
        """Execute all Phase 4 jobs autonomously."""
        logger.info("Starting autonomous Phase 4 execution (MEDIUM priority)")

        # Create jobs for all services
        jobs = []
        for service, config in PHASE_4_SERVICES.items():
            job = ScrapingJobSchema(
                id=self.generate_job_id(service),
                service=service,
                urls=config["urls"],
                scraper_template="mixed",
                config={
                    "github_config": config["github_config"],
                    "html_config": config["html_config"],
                },
                priority=JobPriority.MEDIUM,
                output_path=f"knowledge/technical_manuals/{service}",
            )
            jobs.append(job)
            self.scraper.queue.add_job(job)

        logger.info(f"Created {len(jobs)} jobs for Phase 4 (MEDIUM priority)")

        # Execute all jobs
        start_time = datetime.now()
        for job in jobs:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Executing: {job.service} (MEDIUM)")
            logger.info(f"{'=' * 60}")

            try:
                result = await self.scraper.execute_job(job)

                service_stats = {
                    "service": job.service,
                    "priority": "MEDIUM",
                    "success": result.success,
                    "size_kb": result.total_content_kb,
                    "files": result.sections,
                    "urls_processed": result.urls_processed,
                }
                self.execution_stats["services"].append(service_stats)

                if result.success:
                    logger.info(f"✓ {job.service} completed successfully")
                    logger.info(f"  - Size: {result.total_content_kb:.2f} KB")
                    logger.info(f"  - Files: {result.sections}")
                    logger.info(f"  - URLs processed: {result.urls_processed}")
                    self.execution_stats["successful"] += 1
                    self.execution_stats["total_content_kb"] += result.total_content_kb
                else:
                    logger.error(f"✗ {job.service} failed")
                    self.execution_stats["failed"] += 1

            except Exception as e:
                logger.error(f"✗ {job.service} execution failed: {e}")
                self.execution_stats["failed"] += 1
                self.execution_stats["services"].append(
                    {
                        "service": job.service,
                        "priority": "MEDIUM",
                        "success": False,
                        "error": str(e),
                    }
                )

        # Save execution report
        duration = (datetime.now() - start_time).total_seconds()
        self.execution_stats["end_time"] = datetime.now().isoformat()
        self.execution_stats["duration_seconds"] = duration
        self.execution_stats["total_services"] = len(jobs)

        report_path = self.result_dir / "phase4_execution_report.json"
        with open(report_path, "w") as f:
            json.dump(self.execution_stats, f, indent=2)

        logger.info(f"\nExecution report saved to {report_path}")
        return self.execution_stats

    def print_summary(self):
        """Print execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 4 EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Start time: {self.execution_stats['start_time']}")
        logger.info(
            f"Duration: {self.execution_stats.get('duration_seconds', 0):.1f} seconds"
        )
        logger.info(f"Total services: {self.execution_stats['total_services']}")
        logger.info(f"Successful: {self.execution_stats['successful']}")
        logger.info(f"Failed: {self.execution_stats['failed']}")
        logger.info(f"Total content: {self.execution_stats['total_content_kb']:.2f} KB")

        logger.info("\nResults by service:")
        logger.info("-" * 60)
        for service in self.execution_stats["services"]:
            if service.get("success", False):
                logger.info(
                    f"✓ {service['service']:25} {service.get('size_kb', 0):8.2f} KB  {service.get('files', 0):3} files"
                )
            else:
                logger.info(f"✗ {service['service']:25} FAILED")
        logger.info("-" * 60)
        logger.info("=" * 60)


async def main():
    """Main execution function."""
    executor = AutonomousScrapingExecutor()

    try:
        # Execute all jobs
        stats = await executor.execute_all_jobs()

        # Print summary
        executor.print_summary()

        # Return success code
        if executor.execution_stats["failed"] == 0:
            logger.info("\n✓ All Phase 4 jobs completed successfully!")
            return 0
        else:
            logger.warning(f"\n⚠ {executor.execution_stats['failed']} jobs failed")
            return 1

    except Exception as e:
        logger.error(f"Fatal error during Phase 4 execution: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = anyio.run(main)
    exit(exit_code)
