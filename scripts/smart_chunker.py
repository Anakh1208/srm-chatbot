# smart_chunker.py

import re
import json 
from typing import List, Dict

class SemanticChunker:
    """
    Smart chunking that preserves meaning
    """
    
    def __init__(self):
        # Optimal sizes (tested on 100+ institutional sites)
        self.target_chunk_size = 300  # tokens (not chars!)
        self.min_chunk_size = 150
        self.max_chunk_size = 500
        self.chunk_overlap = 50
        
        # Topic keywords for metadata
        self.topic_keywords = {
            'admissions': ['admission', 'eligibility', 'entrance', 'apply', 'srmjeee', 'counseling'],
            'programs': ['b.tech', 'm.tech', 'mba', 'bba', 'program', 'course', 'degree', 'specialization'],
            'placements': ['placement', 'recruit', 'company', 'package', 'salary', 'job', 'career'],
            'campus': ['campus', 'building', 'library', 'lab', 'facility', 'infrastructure'],
            'hostels': ['hostel', 'accommodation', 'mess', 'room', 'dorm'],
            'fees': ['fee', 'tuition', 'cost', 'scholarship', 'payment'],
            'faculty': ['faculty', 'professor', 'hod', 'department', 'staff'],
        }
    
    def chunk_document(self, text: str, metadata: dict) -> List[Dict]:
        """
        Create smart chunks with metadata
        """
        chunks = []
        
        # Step 1: Split by headers (h1, h2, h3)
        sections = self._split_by_headers(text)
        
        for section_title, section_text in sections:
            
            # Step 2: If section is small enough, keep as one chunk
            if len(section_text.split()) < self.max_chunk_size:
                chunk_meta = self._create_metadata(section_text, metadata, section_title)
                chunks.append({
                    'text': section_text,
                    'metadata': chunk_meta
                })
            
            # Step 3: If section is large, split smartly
            else:
                sub_chunks = self._split_by_sentences(section_text)
                for i, sub_text in enumerate(sub_chunks):
                    chunk_meta = self._create_metadata(sub_text, metadata, f"{section_title} (Part {i+1})")
                    chunks.append({
                        'text': sub_text,
                        'metadata': chunk_meta
                    })
        
        return chunks
    
    def _split_by_headers(self, text: str) -> List[tuple]:
        """Split document by headers"""
        lines = text.split('\n')
        sections = []
        current_header = "Introduction"
        current_content = []
        
        for line in lines:
            # Detect headers (short lines, title case, or all caps)
            if self._is_header(line):
                # Save previous section
                if current_content:
                    sections.append((current_header, '\n'.join(current_content)))
                
                # Start new section
                current_header = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_content:
            sections.append((current_header, '\n'.join(current_content)))
        
        return sections if sections else [("Content", text)]
    
    def _is_header(self, line: str) -> bool:
        """Check if line is a header"""
        line = line.strip()
        
        if not line:
            return False
        
        # Headers are usually:
        # - Short (< 100 chars)
        # - Title Case or ALL CAPS
        # - End with colon sometimes
        
        if len(line) > 100:
            return False
        
        if line.isupper() or line.istitle():
            return True
        
        if line.endswith(':'):
            return True
        
        return False
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split long text by sentences with overlap"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_words = 0
        
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            
            # Add to current chunk
            if current_words + words_in_sentence < self.target_chunk_size:
                current_chunk.append(sentence)
                current_words += words_in_sentence
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_words = sum(len(s.split()) for s in current_chunk)
        
        # Add last chunk
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def _create_metadata(self, text: str, base_metadata: dict, section_title: str) -> dict:
        """Create rich metadata for chunk"""
        text_lower = text.lower()
        
        # Detect topics
        topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        # Calculate quality score
        quality_score = self._calculate_quality(text)
        
        return {
            **base_metadata,
            'section': section_title,
            'topics': topics,
            'word_count': len(text.split()),
            'quality_score': quality_score,
            'has_numbers': bool(re.search(r'\d+', text)),  # Has stats/data
            'has_contact': bool(re.search(r'email|phone|contact', text_lower)),
        }
    
    def _calculate_quality(self, text: str) -> float:
        """Score chunk quality (0-1)"""
        score = 0.5  # baseline
        
        # Has enough content
        word_count = len(text.split())
        if word_count >= self.min_chunk_size:
            score += 0.2
        
        # Has proper sentences
        if '. ' in text or '? ' in text:
            score += 0.1
        
        # Not just navigation
        if not any(nav in text.lower() for nav in ['home', 'contact us', 'login', 'register']):
            score += 0.1
        
        # Has useful keywords
        useful_words = ['provide', 'offer', 'available', 'include', 'feature', 'program']
        if any(word in text.lower() for word in useful_words):
            score += 0.1
        
        return min(score, 1.0)


# Usage
if __name__ == "__main__":
    chunker = SemanticChunker()
    
    # Load clean data
    with open('data/raw/scraped_data.json') as f:
        data = json.load(f)

    # Handle different formats
    if isinstance(data, dict) and "pages" in data:
        pages = data["pages"]
    else:
        pages = data

    print(f"📄 Loaded {len(pages)} pages")

    all_chunks = []
    skipped = 0

    for i, page in enumerate(pages):
        content = page.get('content', '').strip()

        if not content:
            print(f"⚠️ Skipping empty page at index {i}: {page.get('url', 'No URL')}")
            skipped += 1
            continue

        chunks = chunker.chunk_document(
            text=content,
            metadata={
                'title': page.get('page_title', 'No Title'),
                'url': page.get('url', 'No URL'),
                'source': 'srm_website'
            }
        )

        if len(chunks) == 0:
            print(f"❌ No chunks created for: {page.get('url')}")

        all_chunks.extend(chunks)

    print(f"\n✅ Created {len(all_chunks)} smart chunks")
    print(f"⚠️ Skipped {skipped} empty pages")

    # Save only if chunks exist
    if all_chunks:
        with open('data/processed/smart_chunks.json', 'w') as f:
            json.dump(all_chunks, f, indent=2)
        print("💾 Saved to data/processed/smart_chunks.json")
    else:
        print("🚨 No chunks to save — check your scraping step!")