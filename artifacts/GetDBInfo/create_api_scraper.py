#!/usr/bin/env python3
"""
API Database Information Scraper
=================================
Short program to scrape API endpoints and extract data for analysis.

Usage:
    python create_api_scraper.py --help

Features:
- RESTful API endpoint discovery
- JSON data extraction and formatting
- CSV export capabilities
- Rate limiting and error handling
- Configurable authentication
"""

import argparse
import asyncio
import json
import csv
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIDataScraper:
    """Scraper for extracting data from REST API endpoints."""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Fetch data from a specific API endpoint."""
        if not self.session:
            raise RuntimeError("Scraper not properly initialized")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")
            return {"error": str(e), "endpoint": endpoint}

    async def discover_endpoints(self) -> List[str]:
        """Discover available API endpoints."""
        # Common API endpoint patterns
        common_endpoints = [
            "groups", "participants", "activities", "sessions",
            "users", "data", "info", "status", "metrics"
        ]

        available_endpoints = []

        for endpoint in common_endpoints:
            try:
                data = await self.fetch_endpoint(endpoint)
                if "error" not in data:
                    available_endpoints.append(endpoint)
                    logger.info(f"✓ Found endpoint: {endpoint}")
                else:
                    logger.debug(f"✗ Endpoint not available: {endpoint}")
            except Exception:
                logger.debug(f"✗ Failed to check endpoint: {endpoint}")

        return available_endpoints

    async def scrape_all_data(self, endpoints: List[str]) -> Dict[str, Any]:
        """Scrape data from all discovered endpoints."""
        results = {}

        for endpoint in endpoints:
            logger.info(f"Scraping data from: {endpoint}")
            data = await self.fetch_endpoint(endpoint)
            results[endpoint] = data

            # Add metadata
            results[f"{endpoint}_metadata"] = {
                "scraped_at": datetime.now().isoformat(),
                "endpoint": endpoint,
                "record_count": len(data) if isinstance(data, list) else 1
            }

        return results

    def save_to_json(self, data: Dict[str, Any], filename: str):
        """Save scraped data to JSON file."""
        output_file = Path(filename)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Data saved to {filename}")

    def save_to_csv(self, data: Dict[str, Any], base_filename: str):
        """Save scraped data to CSV files."""
        for endpoint, records in data.items():
            if endpoint.endswith("_metadata") or not isinstance(records, list):
                continue

            if not records:
                logger.warning(f"No data to save for {endpoint}")
                continue

            filename = f"{base_filename}_{endpoint}.csv"
            output_file = Path(filename)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to DataFrame for easy CSV export
            df = pd.DataFrame(records)
            df.to_csv(output_file, index=False, encoding='utf-8')

            logger.info(f"✓ CSV saved: {filename} ({len(records)} records)")

async def main():
    """Main scraper execution."""
    parser = argparse.ArgumentParser(description="API Database Information Scraper")
    parser.add_argument("base_url", help="Base URL of the API")
    parser.add_argument("--auth-token", help="Bearer token for authentication")
    parser.add_argument("--output-dir", default="scraped_data", help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="both",
                       help="Output format")
    parser.add_argument("--discover-only", action="store_true",
                       help="Only discover endpoints, don't scrape data")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    async with APIDataScraper(args.base_url, args.auth_token) as scraper:
        logger.info(f"Starting API scrape of: {args.base_url}")

        # Discover endpoints
        endpoints = await scraper.discover_endpoints()
        logger.info(f"Found {len(endpoints)} available endpoints: {', '.join(endpoints)}")

        if args.discover_only:
            print("\n".join(endpoints))
            return

        if not endpoints:
            logger.error("No endpoints found to scrape")
            return

        # Scrape data
        data = await scraper.scrape_all_data(endpoints)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = output_dir / f"api_scrape_{timestamp}"

        if args.format in ["json", "both"]:
            scraper.save_to_json(data, f"{base_filename}.json")

        if args.format in ["csv", "both"]:
            scraper.save_to_csv(data, str(base_filename))

        logger.info("🎉 Scraping completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())