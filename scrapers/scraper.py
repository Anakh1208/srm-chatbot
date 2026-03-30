"""
University Website Scraper - Enhanced Version
---------------------------------------------
This module handles the actual scraping of web pages with improved content extraction.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
import re


class UniversityScraper:
    """
    A scraper class to extract content from university web pages.
    """
    
    def __init__(self, base_url: str, timeout: int = 10, delay: float = 1.0, min_content_length: int = 50):
        """
        Initialize the scraper.
        
        Args:
            base_url: The root URL of the university website
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
            min_content_length: Minimum content length to accept (default: 50, lowered from 100)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.delay = delay
        self.min_content_length = min_content_length
        
        # Parse the base domain
        parsed_url = urlparse(base_url)
        self.base_domain = parsed_url.netloc
        
        # Enhanced headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a webpage with error handling.
        """
        try:
            time.sleep(self.delay)
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout error for URL: {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {str(e)}")
            return None
    
    def extract_text_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract clean text content from HTML with improved extraction.
        """
        # Remove unwanted tags
        unwanted_tags = ['script', 'style', 'noscript', 'iframe', 'svg']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Try multiple strategies to find main content
        content_text = ""
        
        # Strategy 1: Look for main content areas
        main_selectors = [
            ('main', {}),
            ('article', {}),
            ('div', {'id': re.compile('content|main', re.I)}),
            ('div', {'class': re.compile('content|main|body', re.I)}),
            ('div', {'role': 'main'}),
        ]
        
        for tag, attrs in main_selectors:
            main_content = soup.find(tag, attrs)
            if main_content:
                print(f"   📍 Found content in <{tag}> tag")
                content_text = main_content.get_text(separator=' ', strip=True)
                if len(content_text) > self.min_content_length:
                    break
        
        # Strategy 2: If main content not found, try body
        if len(content_text) < self.min_content_length:
            print(f"   📍 Trying <body> tag")
            body = soup.find('body')
            if body:
                # Remove navigation, footer, header
                for unwanted in body.find_all(['nav', 'footer', 'header', 'aside']):
                    unwanted.decompose()
                content_text = body.get_text(separator=' ', strip=True)
        
        # Strategy 3: Get all paragraphs if still insufficient
        if len(content_text) < self.min_content_length:
            print(f"   📍 Extracting all paragraphs")
            paragraphs = soup.find_all('p')
            content_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        # Clean up the text
        content_text = re.sub(r'\s+', ' ', content_text)
        content_text = content_text.strip()
        
        print(f"   📏 Extracted content length: {len(content_text)} characters")
        
        return content_text
    
    def extract_page_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the page title.
        """
        # Try <title> tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try <h1> tag
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        # Try og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        return "No Title"
    
    def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a single page and extract structured data.
        """
        print(f"🔍 Scraping: {url}")
        
        # Fetch the page
        response = self.fetch_page(url)
        if not response:
            return None
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            print(f"⚠️  Skipping non-HTML content: {url} (Type: {content_type})")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data
        page_title = self.extract_page_title(soup)
        print(f"   📄 Title: {page_title}")
        
        content = self.extract_text_content(soup, url)
        
        # Check content length
        if len(content) < self.min_content_length:
            print(f"⚠️  Content too short ({len(content)} chars, need {self.min_content_length})")
            print(f"   💡 Tip: This page might be JavaScript-heavy or have little text content")
            return None
        
        print(f"✅ Successfully scraped!")
        
        return {
            'url': url,
            'page_title': page_title,
            'content': content
        }
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid for crawling.
        """
        parsed = urlparse(url)
        
        # Check domain
        if parsed.netloc and parsed.netloc != self.base_domain:
            return False
        
        # Skip file extensions
        skip_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz',
            '.mp3', '.mp4', '.avi', '.mov'
        ]
        
        url_lower = url.lower()
        if any(url_lower.endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip common patterns
        skip_patterns = ['login', 'logout', 'signin', 'signup', 'register']
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        # Only HTTP/HTTPS
        if parsed.scheme not in ['http', 'https', '']:
            return False
        
        return True
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> set:
        """
        Extract all internal links from a page.
        """
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert to absolute URL
            absolute_url = urljoin(current_url, href)
            
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            
            # Remove trailing slash
            absolute_url = absolute_url.rstrip('/')
            
            # Validate and add
            if self.is_valid_url(absolute_url):
                links.add(absolute_url)
        
        return links


if __name__ == "__main__":
    # Test with SRM website
    print("Testing scraper with SRM website...\n")
    
    scraper = UniversityScraper("https://www.srmist.edu.in", min_content_length=50)
    
    # Test URLs - try different pages
    test_urls = [
        "https://www.srmist.edu.in",
        "https://www.srmist.edu.in/about",
        "https://www.srmist.edu.in/admissions",
    ]
    
    for url in test_urls:
        print(f"\n{'='*70}")
        result = scraper.scrape_page(url)
        
        if result:
            print(f"✅ Success!")
            print(f"Preview: {result['content'][:200]}...")
        else:
            print(f"❌ Failed")
        print(f"{'='*70}")
        
        time.sleep(2)  # Delay between tests