# 🎓 SRM University AI Chatbot - Web Scraper

## Overview

This is the web scraping module for the SRM University AI-powered chatbot. It crawls the university website, extracts clean text content, and stores it in JSON format for later processing.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
# From the project root directory
python scripts/scrape_website.py
```

### 3. Check the Output

The scraped data will be saved to `data/raw/scraped_data.json`

## 📁 Project Structure

```
scrapers/
├── __init__.py           # Module initialization
├── scraper.py           # Core scraping logic (BeautifulSoup)
├── crawler.py           # Crawling orchestration
└── config.json          # Scraping configuration

scripts/
└── scrape_website.py    # Main script to run the crawler

data/
├── raw/                 # Scraped data (JSON files)
├── processed/           # Cleaned and chunked data
├── vectorstore/         # FAISS index files
└── metadata/            # Crawling metadata and logs
```

## 🔧 Configuration

Edit `scrapers/config.json` to customize the crawler:

```json
{
  "scraping_config": {
    "start_url": "https://www.srmist.edu.in",
    "max_pages": 100,           // Maximum pages to crawl
    "max_depth": 3,             // How deep to crawl (0 = start page only)
    "delay_between_requests": 1.0,  // Seconds to wait between requests
    "timeout": 10,              // Request timeout in seconds
    "output_file": "../data/raw/scraped_data.json"
  }
}
```

## 📚 Module Documentation

### UniversityScraper Class

The `UniversityScraper` class handles individual page scraping.

**Key Methods:**

- `fetch_page(url)` - Downloads a webpage with error handling
- `extract_text_content(soup)` - Extracts clean text from HTML
- `extract_page_title(soup)` - Gets the page title
- `scrape_page(url)` - Main method that scrapes a single page
- `is_valid_url(url)` - Validates URLs before crawling
- `extract_links(soup, current_url)` - Finds all internal links

**Example Usage:**

```python
from scrapers.scraper import UniversityScraper

# Create scraper instance
scraper = UniversityScraper("https://www.srmist.edu.in")

# Scrape a single page
result = scraper.scrape_page("https://www.srmist.edu.in/admissions")

if result:
    print(f"Title: {result['page_title']}")
    print(f"Content: {result['content'][:200]}...")
```

### UniversityCrawler Class

The `UniversityCrawler` class orchestrates the crawling of multiple pages.

**Key Methods:**

- `crawl()` - Starts the crawling process
- `save_to_json(output_file)` - Saves scraped data to JSON
- `get_statistics()` - Returns crawling statistics

**Example Usage:**

```python
from scrapers.crawler import UniversityCrawler

# Create crawler instance
crawler = UniversityCrawler(
    start_url="https://www.srmist.edu.in",
    max_pages=50,
    max_depth=2,
    delay=1.0
)

# Start crawling
data = crawler.crawl()

# Save results
crawler.save_to_json("data/raw/scraped_data.json")

# Get statistics
stats = crawler.get_statistics()
print(stats)
```

## 🎯 Features

### ✅ What It Does

- **Crawls Internal Links Only** - Stays within the university domain
- **Avoids Non-Text Files** - Skips PDFs, images, videos, etc.
- **Extracts Clean Text** - Removes navigation, footers, scripts, styles
- **Polite Crawling** - Configurable delays between requests
- **Progress Tracking** - Real-time console output
- **Error Handling** - Gracefully handles timeouts and errors
- **Metadata Tracking** - Saves crawl statistics and timestamps

### ⚠️ What It Avoids

- External links (different domains)
- PDF, image, and media files
- Login/logout pages
- Download links
- Duplicate pages
- Pages with insufficient content

## 📊 Output Format

The scraper produces a JSON file with this structure:

```json
[
  {
    "url": "https://www.srmist.edu.in/admissions",
    "page_title": "Admissions - SRM Institute of Science and Technology",
    "content": "Clean text content extracted from the page..."
  },
  {
    "url": "https://www.srmist.edu.in/academics",
    "page_title": "Academics - SRM Institute of Science and Technology",
    "content": "Clean text content extracted from the page..."
  }
]
```

## 🛠️ Advanced Usage

### Crawl Specific Sections

```python
from scrapers.crawler import UniversityCrawler

# Create crawler for specific section
crawler = UniversityCrawler(
    start_url="https://www.srmist.edu.in/admissions",
    max_pages=20,
    max_depth=1  # Only crawl direct children
)

data = crawler.crawl()
```

### Test Single Page Scraping

```python
from scrapers.scraper import UniversityScraper

scraper = UniversityScraper("https://www.srmist.edu.in")

# Test on a single page
page_data = scraper.scrape_page("https://www.srmist.edu.in/about")

if page_data:
    print("✅ Success!")
    print(f"Title: {page_data['page_title']}")
    print(f"Content length: {len(page_data['content'])} chars")
```

## 🐛 Troubleshooting

### Issue: "Connection timeout"

**Solution:** Increase the timeout in config.json:

```json
"timeout": 20
```

### Issue: "Too many requests" or getting blocked

**Solution:** Increase the delay between requests:

```json
"delay_between_requests": 2.0
```

### Issue: "No content extracted"

**Possible causes:**
- Page might be dynamically loaded (JavaScript)
- Content might be behind a login
- Page structure might be unusual

**Solution:** Check the page manually and adjust the content extraction logic if needed.

### Issue: "Module not found" error

**Solution:** Make sure you're running from the project root:

```bash
cd /path/to/srm-chatbot
python scripts/scrape_website.py
```

## 📝 Next Steps

After scraping the data:

1. **Process the text** - Clean and chunk the content (use `preprocessing/` module)
2. **Generate embeddings** - Create vector representations (use `preprocessing/embeddings_generator.py`)
3. **Build vector store** - Create FAISS index (use `scripts/build_vectorstore.py`)
4. **Test RAG pipeline** - Query the knowledge base (use `scripts/test_query.py`)

## ⚡ Performance Tips

- Start with a small `max_pages` (e.g., 10-20) for testing
- Use `max_depth=1` or `2` to avoid crawling too deep
- Set appropriate delays to be respectful to the server
- Run during off-peak hours for large crawls
- Monitor the output to ensure quality

## 🤝 Contributing

When adding new features:

1. Keep the code modular and well-commented
2. Add error handling for edge cases
3. Update the config.json if adding new parameters
4. Test with small datasets first

## 📄 License

This project is for educational purposes as part of a Minor Project at SRM University.

---

**Happy Crawling! 🕷️**