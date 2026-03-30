"""
Text Chunker Module
------------------
Splits cleaned text into optimal chunks for RAG (Retrieval-Augmented Generation).

WHY CHUNKING IS IMPORTANT FOR RAG:
==================================

1. **Context Window Limitations**
   - Embedding models have max input length (e.g., 512 tokens)
   - LLMs have context window limits
   - Need to fit retrieved content + query + response in one context

2. **Retrieval Precision**
   - Smaller chunks = more precise retrieval
   - Match specific information, not entire documents
   - Example: "admission deadlines" should retrieve just that section, not full page

3. **Embedding Quality**
   - Embeddings of large texts become "averaged" and less meaningful
   - Smaller, focused chunks have more semantic clarity
   - Better similarity matching in vector space

4. **Response Relevance**
   - RAG retrieves top-k chunks to answer query
   - If chunks are too large, you get irrelevant information mixed in
   - If chunks are too small, you lose context

5. **Memory Efficiency**
   - Processing many small chunks is faster than few large ones
   - Better parallelization
   - More efficient vector search

OPTIMAL CHUNK SIZE:
==================
- **300-500 words** (our choice) = ~400-650 tokens
- Balances context preservation with precision
- Fits comfortably in embedding models (512 token limit)
- Leaves room for overlap between chunks
"""

import re
from typing import Dict, List, Tuple
import json


class TextChunker:
    """
    Splits text into chunks optimized for RAG systems.
    """
    
    def __init__(self, 
                 min_chunk_size: int = 300,
                 max_chunk_size: int = 500,
                 overlap_size: int = 50):
        """
        Initialize the chunker.
        
        Args:
            min_chunk_size: Minimum words per chunk (default: 300)
            max_chunk_size: Maximum words per chunk (default: 500)
            overlap_size: Words to overlap between chunks (default: 50)
            
        Why overlap?
        - Prevents losing context at chunk boundaries
        - Ensures complete sentences/ideas aren't split awkwardly
        - Improves retrieval when answer spans chunk boundary
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def count_words(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        return len(text.split())
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences intelligently.
        Handles common abbreviations like Dr., Mr., etc.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Replace common abbreviations to avoid false splits
        text = re.sub(r'Dr\.', 'Dr<DOT>', text)
        text = re.sub(r'Mr\.', 'Mr<DOT>', text)
        text = re.sub(r'Mrs\.', 'Mrs<DOT>', text)
        text = re.sub(r'Ms\.', 'Ms<DOT>', text)
        text = re.sub(r'Prof\.', 'Prof<DOT>', text)
        text = re.sub(r'Sr\.', 'Sr<DOT>', text)
        text = re.sub(r'Jr\.', 'Jr<DOT>', text)
        text = re.sub(r'Ph\.D\.', 'PhD<DOT>', text)
        text = re.sub(r'B\.Tech\.', 'BTech<DOT>', text)
        text = re.sub(r'M\.Tech\.', 'MTech<DOT>', text)
        
        # Split on sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Restore abbreviations
        sentences = [s.replace('<DOT>', '.') for s in sentences]
        
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks_from_sentences(self, sentences: List[str]) -> List[str]:
        """
        Create chunks from sentences, respecting size limits.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_word_count = self.count_words(sentence)
            
            # If adding this sentence exceeds max size, save current chunk
            if current_word_count + sentence_word_count > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap from previous chunk
                overlap_text = ' '.join(current_chunk[-3:])  # Last 3 sentences for overlap
                overlap_words = self.count_words(overlap_text)
                
                if overlap_words > self.overlap_size:
                    current_chunk = current_chunk[-2:]  # Use last 2 sentences
                else:
                    current_chunk = current_chunk[-3:]  # Use last 3 sentences
                
                current_word_count = self.count_words(' '.join(current_chunk))
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
        
        # Add remaining chunk if it meets minimum size
        if current_chunk and current_word_count >= self.min_chunk_size:
            chunks.append(' '.join(current_chunk))
        elif current_chunk and chunks:
            # If too small, append to last chunk
            chunks[-1] = chunks[-1] + ' ' + ' '.join(current_chunk)
        elif current_chunk:
            # First chunk and too small - still include it
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Main chunking method - splits text into optimal chunks.
        
        Args:
            text: Cleaned text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Check if text is already small enough
        word_count = self.count_words(text)
        if word_count <= self.max_chunk_size:
            return [text]
        
        # Split into sentences first
        sentences = self.split_into_sentences(text)
        
        # Create chunks from sentences
        chunks = self.create_chunks_from_sentences(sentences)
        
        return chunks
    
    def chunk_document(self, document: Dict, chunk_id_prefix: str = None) -> List[Dict]:
        """
        Chunk a single document and add metadata.
        
        Args:
            document: Dictionary with 'url', 'page_title', 'content'
            chunk_id_prefix: Optional prefix for chunk IDs
            
        Returns:
            List of chunk dictionaries with metadata
        """
        text = document.get('content', '')
        
        if not text:
            return []
        
        # Create chunks
        text_chunks = self.chunk_text(text)
        
        # Add metadata to each chunk
        chunked_documents = []
        
        for idx, chunk_text in enumerate(text_chunks):
            # Create unique chunk ID
            if chunk_id_prefix:
                chunk_id = f"{chunk_id_prefix}_chunk_{idx}"
            else:
                # Use URL-based ID
                url_slug = document['url'].split('/')[-1] or 'home'
                chunk_id = f"{url_slug}_chunk_{idx}"
            
            chunk_doc = {
                'chunk_id': chunk_id,
                'chunk_index': idx,
                'total_chunks': len(text_chunks),
                'text': chunk_text,
                'word_count': self.count_words(chunk_text),
                'metadata': {
                    'source_url': document['url'],
                    'page_title': document['page_title'],
                    'chunk_position': f"{idx + 1}/{len(text_chunks)}"
                }
            }
            
            chunked_documents.append(chunk_doc)
        
        return chunked_documents
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of all chunks with metadata
        """
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            print(f"📄 Chunking document {doc_idx + 1}/{len(documents)}: {doc['page_title']}")
            
            # Create chunks for this document
            chunks = self.chunk_document(doc, chunk_id_prefix=f"doc{doc_idx}")
            
            print(f"   ✂️  Created {len(chunks)} chunks")
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def get_statistics(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'average_words_per_chunk': 0,
                'min_words': 0,
                'max_words': 0,
                'total_words': 0
            }
        
        word_counts = [chunk['word_count'] for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'average_words_per_chunk': sum(word_counts) / len(word_counts),
            'min_words': min(word_counts),
            'max_words': max(word_counts),
            'total_words': sum(word_counts),
            'unique_sources': len(set(chunk['metadata']['source_url'] for chunk in chunks))
        }


if __name__ == "__main__":
    # Test the chunker
    print("Testing Text Chunker...\n")
    
    chunker = TextChunker(min_chunk_size=50, max_chunk_size=100, overlap_size=20)
    
    # Test document
    test_doc = {
        'url': 'https://www.srmist.edu.in/about',
        'page_title': 'About SRM University',
        'content': """
        SRM Institute of Science and Technology is one of the top ranking universities in India. 
        The university has over 60000 full time students. It has more than 4460 faculty members.
        The campuses are located in Kattankulathur, Ramapuram, Vadapalani, and other locations.
        SRM offers a wide range of undergraduate and postgraduate programs. These programs span
        engineering, medicine, management, and other fields. The university is known for its
        excellent placement record. Companies from all over the world visit for campus recruitment.
        SRM has state-of-the-art facilities and infrastructure. The research output is impressive
        with thousands of publications each year. Students get hands-on experience through labs
        and projects. The university encourages innovation and entrepreneurship among students.
        """
    }
    
    chunks = chunker.chunk_document(test_doc)
    
    print(f"Created {len(chunks)} chunks\n")
    
    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index'] + 1}:")
        print(f"  Words: {chunk['word_count']}")
        print(f"  Text: {chunk['text'][:100]}...")
        print()
    
    print("Chunking successful! ✅")