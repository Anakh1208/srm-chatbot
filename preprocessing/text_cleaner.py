"""
Text Cleaner Module
------------------
Cleans and preprocesses raw text from scraped web pages.
Removes noise, normalizes whitespace, and prepares text for chunking.
"""

import re
import unicodedata
from typing import Dict, List


class TextCleaner:
    """
    Cleans raw text from web scraping to prepare for RAG processing.
    """
    
    def __init__(self):
        """Initialize the text cleaner with cleaning patterns."""
        
        # Common navigation/footer patterns to remove
        self.noise_patterns = [
            # Navigation breadcrumbs
            r'Home\s*>\s*\w+\s*>\s*\w+',
            r'Home\s*/\s*\w+\s*/\s*\w+',
            
            # Social media prompts
            r'Follow us on\s+(Facebook|Twitter|Instagram|LinkedIn|YouTube)',
            r'Share on\s+(Facebook|Twitter|LinkedIn)',
            
            # Common footer text
            r'Copyright\s+©\s+\d{4}',
            r'All rights reserved',
            r'Privacy Policy',
            r'Terms (of Service|and Conditions)',
            
            # Common navigation
            r'Click here to\s+\w+',
            r'Learn more',
            r'Read more',
            
            # Cookie notices
            r'This website uses cookies',
            r'We use cookies to',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                  for pattern in self.noise_patterns]
    
    def remove_urls(self, text: str) -> str:
        """
        Remove URLs from text.
        
        Args:
            text: Input text
            
        Returns:
            Text with URLs removed
        """
        # Remove http/https URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove www URLs
        text = re.sub(r'www\.\S+', '', text)
        
        return text
    
    def remove_emails(self, text: str) -> str:
        """
        Remove email addresses from text.
        
        Args:
            text: Input text
            
        Returns:
            Text with emails removed
        """
        return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        - Replace multiple spaces with single space
        - Replace multiple newlines with single newline
        - Remove leading/trailing whitespace
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_special_characters(self, text: str) -> str:
        """
        Remove or normalize special characters.
        Keeps basic punctuation but removes unusual Unicode characters.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized characters
        """
        # Normalize Unicode (convert é to e, etc.)
        text = unicodedata.normalize('NFKD', text)
        
        # Remove non-ASCII characters but keep basic punctuation
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text
    
    def remove_noise_patterns(self, text: str) -> str:
        """
        Remove common noise patterns like navigation, footers, etc.
        
        Args:
            text: Input text
            
        Returns:
            Text with noise patterns removed
        """
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        
        return text
    
    def remove_short_lines(self, text: str, min_length: int = 10) -> str:
        """
        Remove very short lines (likely navigation items or noise).
        
        Args:
            text: Input text
            min_length: Minimum line length to keep
            
        Returns:
            Text with short lines removed
        """
        lines = text.split('\n')
        filtered_lines = [line for line in lines if len(line.strip()) >= min_length]
        return '\n'.join(filtered_lines)
    
    def fix_encoding_issues(self, text: str) -> str:
        """
        Fix common encoding issues.
        
        Args:
            text: Input text
            
        Returns:
            Text with encoding issues fixed
        """
        # Common encoding fixes
        replacements = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '—',
            'â€"': '–',
            'Â': '',
            '\x92': "'",
            '\x93': '"',
            '\x94': '"',
            '\x97': '—',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def clean_text(self, text: str, 
                   remove_urls: bool = True,
                   remove_emails: bool = True,
                   remove_special_chars: bool = False) -> str:
        """
        Main cleaning pipeline that applies all cleaning steps.
        
        Args:
            text: Raw text from web scraping
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove email addresses
            remove_special_chars: Whether to remove special characters
            
        Returns:
            Cleaned text ready for chunking
        """
        if not text:
            return ""
        
        # Step 1: Fix encoding issues
        text = self.fix_encoding_issues(text)
        
        # Step 2: Remove URLs if requested
        if remove_urls:
            text = self.remove_urls(text)
        
        # Step 3: Remove emails if requested
        if remove_emails:
            text = self.remove_emails(text)
        
        # Step 4: Remove noise patterns
        text = self.remove_noise_patterns(text)
        
        # Step 5: Remove special characters if requested
        if remove_special_chars:
            text = self.remove_special_characters(text)
        
        # Step 6: Remove very short lines
        text = self.remove_short_lines(text)
        
        # Step 7: Normalize whitespace (always last)
        text = self.normalize_whitespace(text)
        
        return text
    
    def clean_document(self, document: Dict) -> Dict:
        """
        Clean a single document from the scraped data.
        
        Args:
            document: Dictionary with 'url', 'page_title', 'content'
            
        Returns:
            Dictionary with cleaned content
        """
        cleaned_doc = document.copy()
        
        # Clean the main content
        cleaned_doc['content'] = self.clean_text(document['content'])
        
        # Also clean the title
        cleaned_doc['page_title'] = self.clean_text(
            document['page_title'],
            remove_urls=False,
            remove_emails=False
        )
        
        return cleaned_doc
    
    def clean_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Clean multiple documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of cleaned documents
        """
        cleaned = []
        
        for doc in documents:
            cleaned_doc = self.clean_document(doc)
            
            # Only keep documents with sufficient content after cleaning
            if len(cleaned_doc['content']) > 100:
                cleaned.append(cleaned_doc)
            else:
                print(f"⚠️  Skipping document with insufficient content after cleaning: {doc['url']}")
        
        return cleaned


if __name__ == "__main__":
    # Test the cleaner
    print("Testing Text Cleaner...\n")
    
    cleaner = TextCleaner()
    
    # Test text with various noise
    test_text = """
    Home > About > Contact Us
    
    Welcome to SRM University
    
    SRM University is one of India's top universities.    We offer programs in engineering.
    
    Click here to apply
    Follow us on Facebook, Twitter, and Instagram
    
    Contact us at info@srmist.edu.in or visit https://www.srmist.edu.in
    
    Copyright © 2024 SRM University. All rights reserved.
    Privacy Policy | Terms of Service
    """
    
    cleaned = cleaner.clean_text(test_text)
    
    print("Original text:")
    print("-" * 50)
    print(test_text)
    print("\nCleaned text:")
    print("-" * 50)
    print(cleaned)
    print("\nCleaning successful! ✅")