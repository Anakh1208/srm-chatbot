#!/usr/bin/env python3
"""
Debug Scraper - Test specific URLs
----------------------------------
Use this to debug why certain pages aren't scraping properly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.scraper import UniversityScraper
import time


def test_url(url: str):
    """Test scraping a specific URL with detailed output."""
    
    print("\n" + "="*70)
    print(f"🧪 TESTING URL: {url}")
    print("="*70)
    
    # Create scraper with lower minimum content length
    scraper = UniversityScraper(
        base_url="https://www.srmist.edu.in",
        min_content_length=50  # Lower threshold for testing
    )
    
    # Try scraping
    result = scraper.scrape_page(url)
    
    if result:
        print("\n✅ SCRAPING SUCCESSFUL!")
        print(f"\n📄 Title: {result['page_title']}")
        print(f"🔗 URL: {result['url']}")
        print(f"📏 Content Length: {len(result['content'])} characters")
        print(f"\n📝 Content Preview (first 500 chars):")
        print("-" * 70)
        print(result['content'][:500])
        print("-" * 70)
        
        # Check for links
        from bs4 import BeautifulSoup
        response = scraper.fetch_page(url)
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = scraper.extract_links(soup, url)
            print(f"\n🔗 Found {len(links)} internal links")
            if links:
                print("Sample links:")
                for i, link in enumerate(list(links)[:5], 1):
                    print(f"  {i}. {link}")
    else:
        print("\n❌ SCRAPING FAILED!")
        print("\n💡 Possible reasons:")
        print("   1. Page is JavaScript-heavy (content loads dynamically)")
        print("   2. Page has very little text content")
        print("   3. Page returned an error or redirect")
        print("   4. Content is in an unusual structure")
        
        print("\n🔧 Suggestions:")
        print("   - Try a different page on the website")
        print("   - Check if the page loads in a browser")
        print("   - Look at the page source to see the HTML structure")


def main():
    """Main function with multiple test URLs."""
    
    print("\n" + "="*70)
    print("🎓 SRM UNIVERSITY SCRAPER - DEBUG MODE")
    print("="*70)
    
    # List of URLs to test
    test_urls = [
        "https://www.srmist.edu.in",
        "https://www.srmist.edu.in/about",
        "https://www.srmist.edu.in/admissions",
        "https://www.srmist.edu.in/program/btech-computer-science-engineering-artificial-intelligence-machine-learning",
        "https://www.srmist.edu.in/contact",
    ]
    
    print("\n📋 Testing multiple URLs...\n")
    
    successful = 0
    failed = 0
    
    for url in test_urls:
        test_url(url)
        
        # Check result
        from scrapers.scraper import UniversityScraper
        scraper = UniversityScraper("https://www.srmist.edu.in", min_content_length=50)
        result = scraper.scrape_page(url)
        
        if result:
            successful += 1
        else:
            failed += 1
        
        print("\n" + "="*70)
        time.sleep(1)  # Polite delay
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {successful}/{len(test_urls)} ({100*successful//len(test_urls)}%)")
    
    if successful > 0:
        print("\n💡 Good news! Some pages are working.")
        print("   → Try running the full crawler with working URLs")
    else:
        print("\n⚠️  No pages scraped successfully.")
        print("   → The website might be heavily JavaScript-based")
        print("   → Consider using Selenium for dynamic content")
        print("   → Or try other university pages that are more static")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)