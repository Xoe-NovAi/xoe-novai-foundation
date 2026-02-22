#!/usr/bin/env python3
"""
Autonomous execution script for Phase 3 technical manual scraping.

HIGH priority services with mixed GitHub+HTML scrapers.
Executes: Qdrant, llama-cpp-python, sentence-transformers, crawl4ai, OpenAI, Anthropic
"""

import anyio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys
import uuid

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


# Phase 3 Configuration: 6 HIGH priority services
PHASE_3_SERVICES = {
    "Qdrant": {
        "urls": [
            "https://github.com/qdrant/qdrant",
            "https://qdrant.tech/documentation/",
        ],
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
    "llama-cpp-python": {
        "urls": [
            "https://github.com/abetlen/llama-cpp-python",
            "https://llama-cpp-python.readthedocs.io/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 50,
            "include_patterns": ["documentation", "api", "guide"],
        },
    },
    "sentence-transformers": {
        "urls": [
            "https://github.com/UKPLab/sentence-transformers",
            "https://www.sbert.net/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 60,
            "include_patterns": ["documentation", "guide", "models"],
        },
    },
    "crawl4ai": {
        "urls": ["https://github.com/unclecode/crawl4ai", "https://crawl4ai.com/"],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 4,
            "max_pages": 30,
            "include_patterns": ["documentation", "guide", "api"],
        },
    },
    "OpenAI": {
        "urls": [
            "https://github.com/openai/openai-python",
            "https://platform.openai.com/docs/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 5,
            "max_pages": 100,
            "include_patterns": ["documentation", "api", "guide"],
        },
    },
    "Anthropic": {
        "urls": [
            "https://github.com/anthropics/anthropic-sdk-python",
            "https://docs.anthropic.com/",
        ],
        "github_config": {"max_depth": 3, "include_patterns": ["README", "docs/"]},
        "html_config": {
            "max_depth": 5,
            "max_pages": 100,
            "include_patterns": ["documentation", "api", "guide"],
        },
    },
}


class AutonomousScrapingExecutor:
    """Manages autonomous execution of Phase 3 scraping jobs."""

    def __init__(self, result_dir: str = "data/scraping_results"):
        """Initialize executor."""
        self.result_dir = Path(result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = TechnicalManualScraper()
        self.job_counter = 0
        self.execution_stats = {
            "phase": "Phase 3",
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
        """Execute all Phase 3 jobs autonomously."""
        logger.info("Starting autonomous Phase 3 execution (HIGH priority)")

        # Create jobs for all services
        jobs = []
        for service, config in PHASE_3_SERVICES.items():
            job = ScrapingJobSchema(
                id=self.generate_job_id(service),
                service=service,
                urls=config["urls"],
                scraper_template="mixed",
                config={
                    "github_config": config["github_config"],
                    "html_config": config["html_config"],
                },
                priority=JobPriority.HIGH,
                output_path=f"knowledge/technical_manuals/{service}",
            )
            jobs.append(job)
            self.scraper.queue.add_job(job)

        logger.info(f"Created {len(jobs)} jobs for Phase 3 (HIGH priority)")

        # Execute all jobs
        start_time = datetime.now()
        for job in jobs:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Executing: {job.service} (HIGH)")
            logger.info(f"{'=' * 60}")

            try:
                result = await self.scraper.execute_job(job)

                service_stats = {
                    "service": job.service,
                    "priority": "HIGH",
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
                    logger.error(f"  - Errors: {result.errors}")
                    self.execution_stats["failed"] += 1

            except Exception as e:
                logger.error(f"✗ {job.service} execution failed: {e}")
                self.execution_stats["failed"] += 1
                self.execution_stats["services"].append(
                    {
                        "service": job.service,
                        "priority": "HIGH",
                        "success": False,
                        "error": str(e),
                    }
                )

        # Save execution report
        duration = (datetime.now() - start_time).total_seconds()
        self.execution_stats["end_time"] = datetime.now().isoformat()
        self.execution_stats["duration_seconds"] = duration
        self.execution_stats["total_services"] = len(jobs)

        report_path = self.result_dir / "phase3_execution_report.json"
        with open(report_path, "w") as f:
            json.dump(self.execution_stats, f, indent=2)

        logger.info(f"\nExecution report saved to {report_path}")
        return self.execution_stats

    def print_summary(self):
        """Print execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 3 EXECUTION SUMMARY")
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
            logger.info("\n✓ All Phase 3 jobs completed successfully!")
            return 0
        else:
            logger.warning(f"\n⚠ {executor.execution_stats['failed']} jobs failed")
            return 1

    except Exception as e:
        logger.error(f"Fatal error during Phase 3 execution: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = anyio.run(main)
    exit(exit_code)
