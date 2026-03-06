#!/usr/bin/env python3
"""
Xoe-NovAi Crawler Service
=========================
Simplified and robust crawler for knowledge mining.
"""

import argparse
import os
import time
import anyio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import toml

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

logger = logging.getLogger("xnai_crawler")
logging.basicConfig(level=logging.INFO)

def sanitize_for_prompt_injection(content: str) -> str:
    if not content: return ""
    return content.replace("ignore previous instructions", "[REDACTED]")

async def curate_from_youtube(query: str, category: str, max_items: int = 5) -> List[Dict]:
    if not YT_DLP_AVAILABLE:
        logger.warning("yt-dlp not available.")
        return []
    results = []
    ydl_opts = {'skip_download': True, 'extract_flat': True, 'quiet': True}
    try:
        def fetch_info():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch{max_items}:{query}", download=False)
        info = await anyio.to_thread(fetch_info)
        for entry in info.get('entries', []):
            results.append({
                'id': f"youtube_{entry.get('id')}",
                'content': f"Title: {entry.get('title')}\nChannel: {entry.get('uploader')}\nDescription: {entry.get('description', '')}",
                'metadata': {
                    'source': 'youtube', 'category': category, 'query': query,
                    'title': entry.get('title'), 'author': entry.get('uploader'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'timestamp': datetime.now().isoformat()
                }
            })
    except Exception as e:
        logger.error(f"YouTube failed: {e}")
    return results

async def initialize_crawler():
    if not CRAWL4AI_AVAILABLE: return None
    try:
        browser_config = BrowserConfig(browser_type="chromium", headless=True,
                                     extra_args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--single-process"])
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.warmup()
        return crawler
    except Exception as e:
        logger.error(f"Crawler init failed: {e}")
        return None

async def curate_from_source(source: str, category: str, query: str, max_items: int = 10, embed: bool = True, dry_run: bool = False) -> Tuple[int, float]:
    start_time = time.time()
    results = []
    if source == 'youtube':
        results = await curate_from_youtube(query, category, max_items)
    else:
        logger.info(f"Source {source} not fully implemented, mocking...")
        results = [{'id': f"{source}_0", 'content': f"Mock {source} content", 'metadata': {'source': source, 'category': category, 'query': query}}]

    if dry_run: return len(results), time.time() - start_time

    # Save logic
    lib_path = Path(os.getenv('LIBRARY_PATH', '/library')) / category
    lib_path.mkdir(parents=True, exist_ok=True)
    for r in results:
        with open(lib_path / f"{r['id']}.txt", 'w') as f:
            f.write(r['content'])

    # Metadata logic
    meta_path = Path(os.getenv('KNOWLEDGE_PATH', '/knowledge')) / 'curator' / 'index.toml'
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {}
    if meta_path.exists():
        with open(meta_path, 'r') as f: metadata = toml.load(f)
    for r in results: metadata[r['id']] = r['metadata']
    with open(meta_path, 'w') as f: toml.dump(metadata, f)

    return len(results), time.time() - start_time

async def main():
    print("XNAi Crawler Service initialized.")

if __name__ == "__main__":
    anyio.run(main)
