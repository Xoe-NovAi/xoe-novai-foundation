#!/usr/bin/env python3
"""
XNAi Foundation - Offline Library Manager
==========================================

Purpose: Manage the offline library of manuals and books.
1. Download/Crawl manuals from official sources (with Deep Crawl support).
2. Scan local library for new files.
3. Ingest files into the curation pipeline.
4. Track status in config/offline-library.yaml.
5. Extract scholarly metadata (BibTeX, DOI, etc.).
6. Process multimedia (Images, Audio, Video).

Usage:
    python scripts/offline_library_manager.py --sync
    python scripts/offline_library_manager.py --download redis --deep
    python scripts/offline_library_manager.py --download plato --scholarly
    python scripts/offline_library_manager.py --ingest
"""

import os
import yaml
import redis
import json
import logging
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration paths
CONFIG_PATH = "config/offline-library.yaml"
LIBRARY_BASE_PATH = "library"
BOOKDROP_PATH = "library/bookdrop"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

class MultimediaHandler:
    def __init__(self):
        self.has_ffmpeg = self._check_ffmpeg()
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            self.Image = Image
            self.TAGS = TAGS
            self.has_pillow = True
        except ImportError:
            self.has_pillow = False
            logger.warning("Pillow not installed. Image processing disabled.")

    def _check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            logger.warning("ffmpeg not found. Audio/Video processing disabled.")
            return False

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from multimedia files."""
        ext = os.path.splitext(file_path)[1].lower()
        metadata = {}

        if ext in ['.jpg', '.jpeg', '.png', '.webp'] and self.has_pillow:
            metadata = self._process_image(file_path)
        elif ext in ['.mp3', '.wav', '.flac', '.mp4', '.mkv', '.mov'] and self.has_ffmpeg:
            metadata = self._process_av(file_path)
        
        return metadata

    def _process_image(self, file_path: str) -> Dict[str, Any]:
        try:
            with self.Image.open(file_path) as img:
                meta = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                }
                # Extract EXIF
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = self.TAGS.get(tag_id, tag_id)
                        if isinstance(value, (str, int, float)):
                            meta[f"exif_{tag}"] = value
                return meta
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return {}

    def _process_av(self, file_path: str) -> Dict[str, Any]:
        try:
            # Use ffprobe for metadata
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            format_info = data.get("format", {})
            return {
                "duration": float(format_info.get("duration", 0)),
                "format_name": format_info.get("format_name"),
                "bit_rate": int(format_info.get("bit_rate", 0)),
                "size": int(format_info.get("size", 0)),
                "streams": len(data.get("streams", []))
            }
        except Exception as e:
            logger.error(f"Error processing A/V {file_path}: {e}")
            return {}

class OfflineLibraryManager:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()
        self.redis_conn = self._get_redis_conn()
        self.multimedia = MultimediaHandler()

    def _load_config(self) -> Dict:
        """Load configuration from YAML."""
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            return {"manuals": {}, "books": []}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _save_config(self):
        """Save updated configuration to YAML."""
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.config, f, sort_keys=False)

    def _get_redis_conn(self):
        """Connect to Redis."""
        try:
            return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            return None

    def download_manual(self, service_name: str, deep: bool = False, scholarly: bool = False):
        """Download/Crawl a manual for a service."""
        manual_info = None
        url = None
        local_path = None

        if service_name in self.config.get("manuals", {}):
            manual_info = self.config["manuals"][service_name]
            url = manual_info["url"]
            local_path = manual_info["local_path"]
        else:
            # Check if it's in books
            for book in self.config.get("books", []):
                if book.get("id") == service_name or book.get("title").lower() == service_name.lower():
                    manual_info = book
                    url = book.get("url")
                    local_path = book.get("local_path")
                    break
        
        if not manual_info or not url:
            logger.error(f"Target {service_name} not found in config or has no URL.")
            return False

        logger.info(f"Downloading {service_name} from {url} (Deep: {deep}, Scholarly: {scholarly})...")

        # Prepare directory
        os.makedirs(BOOKDROP_PATH, exist_ok=True)
        filename = os.path.basename(local_path)
        target_path = os.path.join(BOOKDROP_PATH, filename)
        
        # Determine crawl strategy
        max_depth = 2 if deep else 1
        max_pages = 50 if deep else 1

        crawl_script = f"""
import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

async def main():
    # Deep Crawl Strategy
    strategy = BFSDeepCrawlStrategy(
        max_depth={max_depth},
        include_external=False,
        max_pages={max_pages}
    )

    # Run Config - Use DefaultMarkdownGenerator for high-quality MD
    config = CrawlerRunConfig(
        deep_crawl_strategy=strategy if {deep} else None,
        verbose=True,
        markdown_generator=DefaultMarkdownGenerator()
    )

    async with AsyncWebCrawler() as crawler:
        # For deep crawl, result is a list
        if {deep}:
            results = await crawler.arun(url="{url}", config=config)
            if results:
                # Save as a multi-part documentation set
                base_dir = "{target_path}".replace(".md", "")
                os.makedirs(base_dir, exist_ok=True)
                
                # Combined markdown for ingestion
                combined_md = ""
                for i, res in enumerate(results):
                    if res.markdown:
                        filename = f"part_{{i}}.md"
                        with open(os.path.join(base_dir, filename), "w") as f:
                            f.write(res.markdown)
                        combined_md += f"\\n\\n# SOURCE: {{res.url}}\\n\\n" + res.markdown
                
                with open("{target_path}", "w") as f:
                    f.write(combined_md)
                return True
        else:
            result = await crawler.arun(url="{url}", config=config)
            if result and result.markdown:
                content = result.markdown
                
                # Scholarly Metadata Extraction (Simulated for BERT-readiness)
                if {scholarly}:
                    metadata = {{
                        "title": result.metadata.get("title", ""),
                        "url": "{url}",
                        "crawled_at": "{datetime.now().isoformat()}",
                        "scholarly": True
                    }}
                    content = f"--- metadata ---\\n{{json.dumps(metadata, indent=2)}}\\n--- content ---\\n" + content
                
                with open("{target_path}", "w") as f:
                    f.write(content)
                return True
        return False

if __name__ == "__main__":
    if asyncio.run(main()):
        print("SUCCESS")
    else:
        print("FAILED")
"""
        temp_script = f"temp_crawl_{service_name}.py"
        with open(temp_script, "w") as f:
            f.write(crawl_script)

        try:
            process = subprocess.run(["python3", temp_script], capture_output=True, text=True)
            if "SUCCESS" in process.stdout:
                logger.info(f"Successfully downloaded {service_name} to {target_path}")
                manual_info["status"] = "downloaded"
                manual_info["last_downloaded"] = datetime.now().isoformat()
                manual_info["is_deep"] = deep
                manual_info["is_scholarly"] = scholarly
                self._save_config()
                return True
            else:
                logger.error(f"Failed to download {service_name}: {process.stderr}")
                manual_info["status"] = "failed"
                self._save_config()
                return False
        finally:
            if os.path.exists(temp_script):
                os.remove(temp_script)

    def ingest_library(self):
        """Scan library and ingest pending files into curation queue."""
        logger.info("Scanning library for ingestion...")
        
        # 1. Ingest Manuals
        for service, info in self.config.get("manuals", {}).items():
            if info["status"] == "downloaded" or (os.path.exists(info["local_path"]) and info["status"] == "pending"):
                self._ingest_file(info["local_path"], domain="infrastructure", metadata=info)
                info["status"] = "ingested"
                info["last_ingested"] = datetime.now().isoformat()

        # 2. Ingest Books
        for book in self.config.get("books", []):
            if book.get("status") == "downloaded" or (os.path.exists(book["local_path"]) and book.get("status") == "pending"):
                domain = book.get("domain", "books")
                self._ingest_file(book["local_path"], domain=domain, metadata=book)
                book["status"] = "ingested"
                book["last_ingested"] = datetime.now().isoformat()

        # 3. Ingest Multimedia (Scan library recursively)
        for root, _, files in os.walk(LIBRARY_BASE_PATH):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.webp', '.mp3', '.wav', '.flac', '.mp4', '.mkv', '.mov']:
                    file_path = os.path.join(root, file)
                    media_meta = self.multimedia.process_file(file_path)
                    if media_meta:
                        media_meta["original_filename"] = file
                        self._ingest_file(file_path, domain="multimedia", metadata=media_meta)

        self._save_config()

    def _ingest_file(self, file_path: str, domain: str, metadata: Dict):
        """Push file metadata to curation_queue."""
        if not self.redis_conn:
            logger.error("Redis connection not available for ingestion.")
            return

        task = {
            "file_path": file_path,
            "domain": domain,
            "metadata": metadata,
            "ingested_at": datetime.now().isoformat(),
            "source": "local_library"
        }

        self.redis_conn.rpush("curation_queue", json.dumps(task))
        logger.info(f"Ingested {file_path} into curation_queue")

    def sync_status(self):
        """Sync YAML status with filesystem reality."""
        logger.info("Syncing library status with filesystem...")
        
        SORTED_PATH = "library/sorted"

        for service, info in self.config.get("manuals", {}).items():
            filename = os.path.basename(info["local_path"])
            # Check in bookdrop or sorted
            in_drop = os.path.exists(os.path.join(BOOKDROP_PATH, filename))
            in_sorted = os.path.exists(os.path.join(SORTED_PATH, filename))
            
            if in_drop or in_sorted or os.path.exists(info["local_path"]):
                if info["status"] == "pending" or info["status"] == "failed":
                    info["status"] = "downloaded"
            else:
                if info["status"] == "downloaded" or info["status"] == "ingested":
                    info["status"] = "pending"

        for book in self.config.get("books", []):
            filename = os.path.basename(book["local_path"])
            in_drop = os.path.exists(os.path.join(BOOKDROP_PATH, filename))
            in_sorted = os.path.exists(os.path.join(SORTED_PATH, filename))

            if in_drop or in_sorted or os.path.exists(book["local_path"]):
                if book.get("status") == "pending":
                    book["status"] = "available"
            else:
                book["status"] = "pending"

        self._save_config()

def main():
    parser = argparse.ArgumentParser(description="XNAi Offline Library Manager")
    parser.add_argument("--sync", action="store_true", help="Sync status with filesystem")
    parser.add_argument("--download", type=str, help="Download target (manual or book ID)")
    parser.add_argument("--deep", action="store_true", help="Enable deep crawl (multi-page)")
    parser.add_argument("--scholarly", action="store_true", help="Extract scholarly metadata")
    parser.add_argument("--ingest", action="store_true", help="Ingest pending files into curation queue")
    args = parser.parse_args()

    manager = OfflineLibraryManager()

    if args.sync:
        manager.sync_status()
    
    if args.download:
        manager.download_manual(args.download, deep=args.deep, scholarly=args.scholarly)

    if args.ingest:
        manager.ingest_library()

    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()
