"""
University Website Crawler
--------------------------
This module handles the crawling logic - discovering and visiting multiple pages.
"""

from typing import Set, List, Dict
import json
from urllib.parse import urlparse
from scrapers.scraper import UniversityScraper
from collections import deque


class UniversityCrawler:
    """
    A crawler that systematically visits and scrapes multiple pages on a website.
    """
    
    def __init__(self, 
                 start_url: str, 
                 max_pages: int = 100,
                 max_depth: int = 3,
                 delay: float = 1.0):
        """
        Initialize the crawler.
        
        Args:
            start_url: The URL to start crawling from
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth to crawl (0 = start page only, 1 = start + direct links, etc.)
            delay: Delay between requests in seconds
        """
        self.start_url = start_url.rstrip('/')  # Remove trailing slash
        self.max_pages = max_pages
        self.max_depth = max_depth
        
        # Initialize the scraper
        self.scraper = UniversityScraper(start_url, delay=delay)
        
        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()
        
        # Queue of URLs to visit (with their depth)
        # Format: (url, depth)
        self.to_visit: deque = deque([(self.start_url, 0)])
        
        # Store scraped data
        self.scraped_data: List[Dict[str, str]] = []
    
    def crawl(self) -> List[Dict[str, str]]:
        """
        Start the crawling process.
        
        Returns:
            List of dictionaries containing scraped data
        """
        print(f"🚀 Starting crawl from: {self.start_url}")
        print(f"📊 Settings: Max pages={self.max_pages}, Max depth={self.max_depth}")
        print("-" * 70)
        
        # Continue while there are URLs to visit and we haven't hit the limit
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            # Get the next URL to visit
            current_url, current_depth = self.to_visit.popleft()
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            # Skip if we've exceeded max depth
            if current_depth > self.max_depth:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Display progress
            print(f"\n[{len(self.visited_urls)}/{self.max_pages}] Depth {current_depth}: {current_url}")
            
            # Scrape the page
            page_data = self.scraper.scrape_page(current_url)
            
            # If scraping was successful, save the data
            if page_data:
                self.scraped_data.append(page_data)
                print(f"✅ Scraped: {page_data['page_title']}")
                
                # Only discover new links if we haven't reached max depth
                if current_depth < self.max_depth:
                    # Fetch the page again to extract links
                    response = self.scraper.fetch_page(current_url)
                    if response:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract links
                        new_links = self.scraper.extract_links(soup, current_url)
                        
                        # Add new links to the queue
                        for link in new_links:
                            if link not in self.visited_urls:
                                self.to_visit.append((link, current_depth + 1))
                        
                        print(f"🔗 Found {len(new_links)} new links")
            else:
                print(f"⚠️  Failed to scrape this page")
        
        print("\n" + "=" * 70)
        print(f"✨ Crawling complete!")
        print(f"📄 Total pages scraped: {len(self.scraped_data)}")
        print(f"🔍 Total pages visited: {len(self.visited_urls)}")
        print("=" * 70)
        
        return self.scraped_data
    
    def save_to_json(self, output_file: str):
        """
        Save scraped data to a JSON file.
        
        Args:
            output_file: Path to the output JSON file
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Data saved to: {output_file}")
            
            # Calculate and display statistics
            total_content_length = sum(len(item['content']) for item in self.scraped_data)
            avg_content_length = total_content_length / len(self.scraped_data) if self.scraped_data else 0
            
            print(f"\n📊 Statistics:")
            print(f"   - Total pages: {len(self.scraped_data)}")
            print(f"   - Total content: {total_content_length:,} characters")
            print(f"   - Average content per page: {avg_content_length:.0f} characters")
            
        except Exception as e:
            print(f"\n❌ Error saving to JSON: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get crawling statistics.
        
        Returns:
            Dictionary with crawling statistics
        """
        if not self.scraped_data:
            return {
                'total_pages': 0,
                'total_content_length': 0,
                'average_content_length': 0,
                'unique_titles': 0
            }
        
        total_content_length = sum(len(item['content']) for item in self.scraped_data)
        unique_titles = len(set(item['page_title'] for item in self.scraped_data))
        
        return {
            'total_pages': len(self.scraped_data),
            'total_content_length': total_content_length,
            'average_content_length': total_content_length / len(self.scraped_data),
            'unique_titles': unique_titles,
            'total_visited': len(self.visited_urls)
        }


if __name__ == "__main__":
    # Example usage
    print("🎓 University Website Crawler - Test Run\n")
    
    # Create crawler instance
    # NOTE: Replace with actual SRM website URL
    crawler = UniversityCrawler(
        start_url="https://www.srmist.edu.in",
        max_pages=10,      # Limit to 10 pages for testing
        max_depth=2,       # Crawl 2 levels deep
        delay=1.0          # 1 second delay between requests
    )
    
    # Start crawling
    data = crawler.crawl()
    
    # Save results
    crawler.save_to_json("../data/raw/scraped_data.json")
    
    # Display statistics
    stats = crawler.get_statistics()
    print(f"\n📈 Final Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")