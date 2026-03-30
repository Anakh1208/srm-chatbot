#!/usr/bin/env python3
"""
Process Scraped Data
-------------------
Main script to process raw scraped data into chunks ready for embedding.

Pipeline:
1. Load raw scraped data (JSON)
2. Clean text (remove noise, normalize)
3. Chunk into 300-500 word pieces
4. Add metadata (URL, title, position)
5. Save as chunks.json

Usage:
    python scripts/process_data.py
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.text_cleaner import TextCleaner
from preprocessing.chunker import TextChunker


def load_scraped_data(input_file: str) -> list:
    """
    Load raw scraped data from JSON file.
    
    Args:
        input_file: Path to scraped_data.json
        
    Returns:
        List of document dictionaries
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} documents from {input_file}")
        return data
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {input_file}")
        print(f"💡 Make sure you've run the scraper first:")
        print(f"   python scripts/scrape_website.py")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {input_file}")
        print(f"   {str(e)}")
        sys.exit(1)


def save_chunks(chunks: list, output_file: str):
    """
    Save processed chunks to JSON file.
    
    Args:
        chunks: List of chunk dictionaries
        output_file: Path to output file
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Saved {len(chunks)} chunks to {output_file}")
        
        # Calculate file size
        file_size = os.path.getsize(output_file)
        size_mb = file_size / (1024 * 1024)
        print(f"📦 File size: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error saving chunks: {str(e)}")
        sys.exit(1)


def save_metadata(stats: dict, chunks_sample: list, output_file: str):
    """
    Save processing metadata and statistics.
    
    Args:
        stats: Statistics dictionary
        chunks_sample: Sample chunks for preview
        output_file: Path to metadata file
    """
    metadata = {
        'processing_date': datetime.now().isoformat(),
        'statistics': stats,
        'sample_chunks': chunks_sample[:3]  # First 3 chunks as examples
    }
    
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"📝 Saved metadata to {output_file}")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not save metadata: {str(e)}")


def display_statistics(stats: dict):
    """
    Display processing statistics in a nice format.
    
    Args:
        stats: Statistics dictionary
    """
    print("\n" + "=" * 70)
    print("📊 PROCESSING STATISTICS")
    print("=" * 70)
    print(f"Total chunks created:        {stats['total_chunks']}")
    print(f"Unique source documents:     {stats['unique_sources']}")
    print(f"Average words per chunk:     {stats['average_words_per_chunk']:.1f}")
    print(f"Min words in a chunk:        {stats['min_words']}")
    print(f"Max words in a chunk:        {stats['max_words']}")
    print(f"Total words across chunks:   {stats['total_words']:,}")
    print("=" * 70)


def display_sample_chunks(chunks: list, num_samples: int = 2):
    """
    Display sample chunks for verification.
    
    Args:
        chunks: List of chunk dictionaries
        num_samples: Number of samples to show
    """
    print("\n" + "=" * 70)
    print("📝 SAMPLE CHUNKS")
    print("=" * 70)
    
    for i, chunk in enumerate(chunks[:num_samples]):
        print(f"\nChunk {i + 1}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Source: {chunk['metadata']['page_title']}")
        print(f"  URL: {chunk['metadata']['source_url']}")
        print(f"  Position: {chunk['metadata']['chunk_position']}")
        print(f"  Words: {chunk['word_count']}")
        print(f"  Text preview:")
        print(f"  {'-' * 66}")
        print(f"  {chunk['text'][:200]}...")
        print(f"  {'-' * 66}")
    
    print("\n" + "=" * 70)


def main():
    """
    Main processing pipeline.
    """
    print("\n" + "=" * 70)
    print("🎓 SRM CHATBOT - TEXT PROCESSING PIPELINE")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Configuration
    input_file = "data/raw/scraped_data.json"
    output_file = "data/processed/chunks.json"
    metadata_file = "data/metadata/processing_metadata.json"
    
    # Step 1: Load scraped data
    print("=" * 70)
    print("📂 STEP 1: Loading scraped data")
    print("=" * 70)
    documents = load_scraped_data(input_file)
    
    # Step 2: Clean text
    print("\n" + "=" * 70)
    print("🧹 STEP 2: Cleaning text")
    print("=" * 70)
    cleaner = TextCleaner()
    cleaned_documents = cleaner.clean_documents(documents)
    print(f"✅ Cleaned {len(cleaned_documents)} documents")
    print(f"⚠️  Removed {len(documents) - len(cleaned_documents)} documents with insufficient content")
    
    # Step 3: Chunk text
    print("\n" + "=" * 70)
    print("✂️  STEP 3: Chunking text (300-500 words per chunk)")
    print("=" * 70)
    print("💡 Why chunking?")
    print("   - Fits embedding model limits (512 tokens)")
    print("   - Improves retrieval precision")
    print("   - Better semantic matching")
    print("   - Enables focused responses\n")
    
    chunker = TextChunker(
        min_chunk_size=300,
        max_chunk_size=500,
        overlap_size=50
    )
    
    chunks = chunker.chunk_documents(cleaned_documents)
    print(f"\n✅ Created {len(chunks)} total chunks")
    
    # Step 4: Get statistics
    print("\n" + "=" * 70)
    print("📊 STEP 4: Generating statistics")
    print("=" * 70)
    stats = chunker.get_statistics(chunks)
    display_statistics(stats)
    
    # Step 5: Display samples
    display_sample_chunks(chunks)
    
    # Step 6: Save outputs
    print("=" * 70)
    print("💾 STEP 5: Saving processed data")
    print("=" * 70)
    save_chunks(chunks, output_file)
    save_metadata(stats, chunks, metadata_file)
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Output files:")
    print(f"   - Chunks: {output_file}")
    print(f"   - Metadata: {metadata_file}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Generate embeddings: python scripts/generate_embeddings.py")
    print(f"   2. Build FAISS index: python scripts/build_vectorstore.py")
    print(f"   3. Test RAG queries: python scripts/test_query.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)