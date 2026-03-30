"""
Context cleaning utilities
"""
import re

class ContextCleaner:
    """Clean retrieved chunks before sending to LLM"""
    
    def __init__(self):
        # Junk patterns to remove
        self.junk_patterns = [
            r'Home\s*\|\s*About\s*\|\s*Contact',
            r'Copyright.*?(?:\n|$)',
            r'All rights reserved',
            r'Follow us on.*?(?:\n|$)',
            r'Quick Links?:.*?(?:\n|$)',
            r'Last updated:.*?(?:\n|$)',
            r'\[.*?Edit.*?\]',
            r'Click here.*?(?:\n|$)',
        ]
    
    def clean_chunks(self, chunks: list, max_context_length: int = 600) -> str:
        """
        Clean and combine chunks into usable context
        
        Args:
            chunks: List of retrieved chunks (dicts or strings)
            max_context_length: Max words in final context
        
        Returns:
            Clean context string
        """
        
        if not chunks:
            return ""
        
        cleaned_texts = []
        total_words = 0
        
        for chunk in chunks:
            # Handle both dict and string chunks
            if isinstance(chunk, dict):
                text = chunk.get('text', str(chunk))
            else:
                text = str(chunk)
            
            # Remove junk patterns
            for pattern in self.junk_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove very short chunks (likely navigation)
            if len(text.split()) < 15:
                continue
            
            # Add to context if we have space
            words_in_chunk = len(text.split())
            if total_words + words_in_chunk <= max_context_length:
                cleaned_texts.append(text)
                total_words += words_in_chunk
            else:
                # Add partial chunk to fill remaining space
                remaining_words = max_context_length - total_words
                if remaining_words > 20:  # Only if meaningful amount left
                    words = text.split()[:remaining_words]
                    cleaned_texts.append(' '.join(words) + '...')
                break
        
        # Combine with separator
        return '\n\n'.join(cleaned_texts)
    
    def deduplicate(self, text: str) -> str:
        """Remove duplicate sentences"""
        sentences = text.split('. ')
        seen = set()
        unique = []
        
        for sentence in sentences:
            normalized = sentence.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(sentence)
        
        return '. '.join(unique)