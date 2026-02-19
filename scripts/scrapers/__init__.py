"""
Scrapers package - Template implementations for scraping different documentation formats.
"""

from .base_scraper import BaseScraper, ScrapedContent
from .github_scraper import GitHubScraper
from .html_scraper import HTMLScraper

__all__ = [
    "BaseScraper",
    "ScrapedContent",
    "GitHubScraper",
    "HTMLScraper",
]
