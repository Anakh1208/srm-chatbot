"""
Improved Chunking Strategy - Fixed for SRM Data
"""
import json
import os
import re
from typing import List, Dict

class ImprovedChunker:
    def __init__(self, chunk_size=400, chunk_overlap=100, min_chunk_size=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_by_semantic_units(self, text: str, metadata: dict) -> List[Dict]:
        """Smart chunking that respects semantic boundaries"""
        chunks = []
        sections = self._split_by_headers(text)
        
        for section_title, section_text in sections:
            if len(section_text) > self.chunk_size:
                sub_chunks = self._split_with_overlap(section_text)
                for i, chunk_text in enumerate(sub_chunks):
                    chunks.append({
                        'text': chunk_text,
                        'metadata': {**metadata, 'section': section_title, 'sub_chunk': i}
                    })
            else:
                chunks.append({
                    'text': section_text,
                    'metadata': {**metadata, 'section': section_title}
                })
        
        return chunks
    
    def _split_by_headers(self, text: str) -> List[tuple]:
        """Split text by headers"""
        lines = text.split('\n')
        sections = []
        current_section = []
        current_title = "Introduction"
        
        for line in lines:
            if len(line) < 100 and line.strip() and (line.isupper() or line.strip().endswith(':')):
                if current_section:
                    sections.append((current_title, '\n'.join(current_section)))
                current_title = line.strip()
                current_section = []
            else:
                current_section.append(line)
        
        if current_section:
            sections.append((current_title, '\n'.join(current_section)))
        
        return sections if sections else [("Content", text)]
    
    def _split_with_overlap(self, text: str) -> List[str]:
        """Split text with overlap"""
        words = text.split()
        chunks = []
        i = 0
        
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
            i += self.chunk_size - self.chunk_overlap
        
        return chunks if chunks else [text]

def reprocess_data():
    """Reprocess scraped data with improved chunking"""
    print("🔄 Reprocessing data with improved chunking...")
    
    # ✅ FIX: Use absolute paths (works from anywhere)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    input_path = os.path.join(BASE_DIR, "data/raw/scraped_data.json")
    output_path = os.path.join(BASE_DIR, "data/processed/improved_chunks.json")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"❌ Input file not found: {input_path}")
    
    with open(input_path, 'r') as f:
        scraped_data = json.load(f)
    
    print(f"📊 Found {len(scraped_data)} pages")
    
    chunker = ImprovedChunker()
    all_chunks = []
    
    for page in scraped_data:
        semantic_chunks = chunker.chunk_by_semantic_units(
            text=page['content'],
            metadata={
                'title': page.get('url', 'No Title'),
                'url': page.get('url', '')
            }
        )
        all_chunks.extend(semantic_chunks)
    
    # ✅ Ensure folder exists (using BASE_DIR)
    processed_dir = os.path.join(BASE_DIR, "data/processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Created: {len(all_chunks)} chunks")
    print(f"   Saved to: {output_path}")
    
    return all_chunks

if __name__ == "__main__":
    reprocess_data()