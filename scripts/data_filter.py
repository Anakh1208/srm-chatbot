# data_filter.py - Run this on your scraped data

import json
import re

# URLs to KEEP (whitelist approach is better)
KEEP_PATTERNS = [
    r'/admissions/',
    r'/programs/',
    r'/placements/',
    r'/campus/',
    r'/about/',
    r'/departments/',
    r'/courses/',
    r'/facilities/',
    r'/hostels/',
    r'/fees/',
]

# URLs to REJECT (nuclear list)
REJECT_PATTERNS = [
    r'/ugc', r'/naac', r'/nirf', r'/aishe',
    r'/tender', r'/recruitment', r'/career',
    r'/rti', r'/mandatory', r'/compliance',
    r'/grievance', r'/anti-ragging',
    r'/committee', r'/policy',
    r'/sitemap', r'/privacy', r'/terms',
]

# Content to REJECT (even if URL is good)
BAD_CONTENT_MARKERS = [
    'All Rights Reserved',
    'Copyright ©',
    'Follow us on',
    'Quick Links:',
    'Home | About | Contact',
    'Last Updated:',
    'Designed and Developed by',
]

def should_keep_page(url, content):
    """Decide if page is useful"""
    
    # Check URL whitelist
    is_good_url = any(re.search(pattern, url, re.I) for pattern in KEEP_PATTERNS)
    
    # Check URL blacklist
    is_bad_url = any(re.search(pattern, url, re.I) for pattern in REJECT_PATTERNS)
    
    if is_bad_url:
        return False
    
    if not is_good_url:
        return False  # Only keep whitelisted
    
    # Check content quality
    content_lower = content.lower()
    
    # Too short = navigation/footer only
    if len(content) < 200:
        return False
    
    # Too many bad markers
    bad_count = sum(1 for marker in BAD_CONTENT_MARKERS if marker.lower() in content_lower)
    if bad_count > 2:
        return False
    
    # Must have actual content words
    content_words = re.findall(r'\b\w+\b', content)
    if len(set(content_words)) < 50:  # Less than 50 unique words
        return False
    
    return True

def clean_scraped_data(input_file, output_file):
    """Filter scraped data"""
    
    with open(input_file, 'r') as f:
        pages = json.load(f)
    
    print(f"📊 Original pages: {len(pages)}")
    
    # Filter pages
    good_pages = []
    for page in pages:
        if should_keep_page(page['url'], page['content']):
            # Also clean the content
            cleaned_content = clean_content(page['content'])
            page['content'] = cleaned_content
            good_pages.append(page)
    
    print(f"✅ Kept pages: {len(good_pages)}")
    print(f"❌ Removed: {len(pages) - len(good_pages)} ({100*(len(pages)-len(good_pages))/len(pages):.1f}%)")
    
    with open(output_file, 'w') as f:
        json.dump(good_pages, f, indent=2)
    
    return good_pages

def clean_content(text):
    """Remove navigation, footers, etc"""
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty
        if not line:
            continue
        
        # Skip navigation
        if line in ['Home', 'About', 'Contact', 'Login', 'Register']:
            continue
        
        # Skip social media
        if line in ['Facebook', 'Twitter', 'LinkedIn', 'Instagram']:
            continue
        
        # Skip if mostly symbols
        if sum(c.isalnum() for c in line) / max(len(line), 1) < 0.5:
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

# Run it
if __name__ == "__main__":
    clean_scraped_data(
        'data/raw/scraped_data.json',
        'data/raw/scraped_data_clean.json'
    )