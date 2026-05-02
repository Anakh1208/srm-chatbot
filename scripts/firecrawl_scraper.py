from firecrawl import Firecrawl
import json
import os

# 🔑 Replace with your API key
app = Firecrawl(api_key="fc-1fe2dcccd9b0426d9bbcc268ae644730")

def scrape_srm():
    print("🔥 Starting Firecrawl scraping...")

    # Crawl SRM website
    docs = app.crawl(
        "https://www.srmist.edu.in",
        limit=30  # keep small for now
    )

    results = []

    for doc in docs.data:
        results.append({
            "url": getattr(doc.metadata, "sourceURL", None),
            "content": doc.markdown
        })

    os.makedirs("data/raw", exist_ok=True)

    with open("data/raw/scraped_data.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Scraped {len(results)} pages successfully!")

if __name__ == "__main__":
    scrape_srm()