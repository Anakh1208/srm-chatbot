"""
Scrapers Module
--------------
Web scraping and crawling utilities for university website data collection.
"""

from .scraper import UniversityScraper
from .crawler import UniversityCrawler

__all__ = ['UniversityScraper', 'UniversityCrawler']