#!/usr/bin/env python3
"""
Xoe-NovAi Curation Job Dispatcher
=================================

This script provides a CLI entrypoint to manually trigger curation jobs.
It leverages the existing `crawler_curation` service functions to crawl
a URL and queue it for processing by the `curation_worker`.

Usage:
  python3 scripts/curate.py --url <URL>
  python3 scripts/curate.py --url https://docs.vikunja.io/api/
"""

import os
import sys
import argparse
import anyio
import redis

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.XNAi_rag_app.services.crawler_curation import (
    crawl_and_curate,
    queue_for_curation,
)
from crawl4ai import AsyncWebCrawler


async def main():
    """Main function to parse args and dispatch curation job."""
    parser = argparse.ArgumentParser(description="XNAi Curation Job Dispatcher")
    parser.add_argument("--url", required=True, help="The URL to scrape and curate.")
    args = parser.parse_args()

    url_to_curate = args.url

    print(f"🚀 Starting curation job for: {url_to_curate}")

    # --- 1. Crawl the URL ---
    print("[1/3] Crawling URL...")
    crawler = AsyncWebCrawler()
    crawled_doc = await crawl_and_curate(crawler, url_to_curate)

    if not crawled_doc:
        print(f"❌ Crawling failed for {url_to_curate}. Aborting.")
        sys.exit(1)

    print(f"✅ Crawling successful. Word count: {crawled_doc.metadata.word_count}")

    # --- 2. Save Raw Content to Staging ---
    print("[2/3] Saving raw content to _staging...")
    staging_path = os.path.join(PROJECT_ROOT, "library", "_staging")
    os.makedirs(staging_path, exist_ok=True)

    file_name = f"{crawled_doc.metadata.content_hash}.md"
    staging_file_path = os.path.join(staging_path, file_name)

    with open(staging_file_path, "w", encoding="utf-8") as f:
        f.write(crawled_doc.content)

    print(f"✅ Raw content saved to: {staging_file_path}")

    # --- 3. Queue for Curation Worker ---
    print("[3/3] Queueing for curation worker...")
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD")

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )
        r.ping()  # Check connection

        if queue_for_curation(crawled_doc, r):
            print("✅ Successfully queued for async processing.")
        else:
            print("❌ Failed to queue for curation.")

    except redis.exceptions.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("Please ensure Redis is running and accessible.")
        sys.exit(1)

    print("🎉 Curation job dispatched successfully!")


if __name__ == "__main__":
    anyio.run(main)
