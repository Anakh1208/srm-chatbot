#!/usr/bin/env python3
"""
Scrape Website Script
--------------------
Main script to run the university website crawler.
This can be run from the command line or scheduled with cron.

Usage:
    python scripts/scrape_website.py
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.crawler import UniversityCrawler


def load_config(config_path: str = "scrapers/config.json") -> dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dictionary with configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config['scraping_config']
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_path}")
        print("Using default configuration...")
        return {
            'start_url': 'https://www.srmist.edu.in',
            'max_pages': 50,
            'max_depth': 2,
            'delay_between_requests': 1.0,
            'output_file': 'data/raw/scraped_data.json'
        }
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        sys.exit(1)


def ensure_directories():
    """
    Ensure required directories exist.
    """
    directories = [
        'data/raw',
        'data/processed',
        'data/vectorstore',
        'data/metadata'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Ensured directory exists: {directory}")


def main():
    """
    Main function to run the scraper.
    """
    print("=" * 70)
    print("🎓 SRM UNIVERSITY WEBSITE CRAWLER")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure directories exist
    ensure_directories()
    
    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()
    
    print(f"\n🔧 Configuration:")
    print(f"   - Start URL: {config['start_url']}")
    print(f"   - Max Pages: {config['max_pages']}")
    print(f"   - Max Depth: {config['max_depth']}")
    print(f"   - Delay: {config['delay_between_requests']}s")
    print(f"   - Output: {config['output_file']}\n")
    
    # Create crawler instance
    crawler = UniversityCrawler(
        start_url=config['start_url'],
        max_pages=config['max_pages'],
        max_depth=config['max_depth'],
        delay=config['delay_between_requests']
    )
    
    # Start crawling
    try:
        data = crawler.crawl()
        
        # Save results
        crawler.save_to_json(config['output_file'])
        
        # Save metadata
        metadata = {
            'crawl_date': datetime.now().isoformat(),
            'start_url': config['start_url'],
            'total_pages_scraped': len(data),
            'total_pages_visited': len(crawler.visited_urls),
            'statistics': crawler.get_statistics()
        }
        
        metadata_file = 'data/metadata/last_crawl.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n📝 Metadata saved to: {metadata_file}")
        
        print("\n" + "=" * 70)
        print("✨ CRAWLING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Crawling interrupted by user!")
        print(f"📊 Pages scraped before interruption: {len(crawler.scraped_data)}")
        
        # Save partial results
        if crawler.scraped_data:
            output_file = config['output_file'].replace('.json', '_partial.json')
            crawler.save_to_json(output_file)
            print(f"💾 Partial results saved to: {output_file}")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error during crawling: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()