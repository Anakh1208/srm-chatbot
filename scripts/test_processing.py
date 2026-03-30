#!/usr/bin/env python3
"""
Test Text Processing Pipeline
-----------------------------
Test the cleaning and chunking modules with sample data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.text_cleaner import TextCleaner
from preprocessing.chunker import TextChunker


def test_text_cleaner():
    """Test the text cleaning functionality."""
    
    print("\n" + "="*70)
    print("🧪 TEST 1: Text Cleaning")
    print("="*70)
    
    cleaner = TextCleaner()
    
    # Sample noisy text (simulating scraped content)
    noisy_text = """
    Home > About > University
    
    Welcome to SRM Institute of Science and Technology
    
    SRM is one of India's    top universities.     We offer programs in engineering,
    medicine, and management.
    
    Visit us at https://www.srmist.edu.in or contact us at info@srmist.edu.in
    
    Follow us on Facebook  Twitter  Instagram
    
    Click here to apply now!
    
    Copyright © 2024 SRM University.  All rights reserved.
    Privacy Policy | Terms of Service
    """
    
    print("\n📄 Original Text:")
    print("-" * 70)
    print(noisy_text)
    
    cleaned = cleaner.clean_text(noisy_text)
    
    print("\n✨ Cleaned Text:")
    print("-" * 70)
    print(cleaned)
    
    print("\n📊 Cleaning Results:")
    print(f"   Original length: {len(noisy_text)} chars")
    print(f"   Cleaned length: {len(cleaned)} chars")
    print(f"   Reduction: {100 * (1 - len(cleaned)/len(noisy_text)):.1f}%")
    
    # Verify cleaning worked
    assert "http" not in cleaned, "URLs should be removed"
    assert "@" not in cleaned, "Emails should be removed"
    assert "Copyright" not in cleaned, "Footer text should be removed"
    assert "  " not in cleaned, "Multiple spaces should be normalized"
    
    print("\n✅ Text cleaning tests passed!")


def test_text_chunker():
    """Test the text chunking functionality."""
    
    print("\n" + "="*70)
    print("🧪 TEST 2: Text Chunking")
    print("="*70)
    
    chunker = TextChunker(
        min_chunk_size=50,   # Small for testing
        max_chunk_size=100,  # Small for testing
        overlap_size=20
    )
    
    # Sample long text
    long_text = """
    SRM Institute of Science and Technology is one of the top ranking universities in India.
    The university has over 60000 full time students and more than 4460 faculty members.
    The campuses are located in Kattankulathur, Ramapuram, Vadapalani, and other locations
    across India. SRM offers a wide range of undergraduate and postgraduate programs.
    These programs span engineering, medicine, management, science, and humanities.
    The university is known for its excellent placement record. Companies from all over
    the world visit the campus for recruitment. SRM has state-of-the-art facilities and
    infrastructure. The research output is impressive with thousands of publications each year.
    Students get hands-on experience through well-equipped laboratories and live projects.
    The university encourages innovation and entrepreneurship among students.
    SRM has collaborations with leading universities worldwide. Students can participate
    in exchange programs and international internships. The campus life is vibrant with
    numerous clubs and cultural activities. Sports facilities are world-class with multiple
    playing fields and indoor stadiums.
    """ * 2  # Double it to make it longer
    
    print(f"\n📄 Original Text: {len(long_text.split())} words")
    
    chunks = chunker.chunk_text(long_text)
    
    print(f"\n✂️  Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        word_count = chunker.count_words(chunk)
        print(f"\n   Chunk {i+1}:")
        print(f"   - Words: {word_count}")
        print(f"   - Preview: {chunk[:100]}...")
        
        # Verify chunk size
        assert word_count >= chunker.min_chunk_size or i == len(chunks) - 1, \
            f"Chunk {i+1} is too small ({word_count} words)"
        assert word_count <= chunker.max_chunk_size, \
            f"Chunk {i+1} is too large ({word_count} words)"
    
    print("\n✅ Text chunking tests passed!")


def test_document_processing():
    """Test processing a complete document."""
    
    print("\n" + "="*70)
    print("🧪 TEST 3: Complete Document Processing")
    print("="*70)
    
    # Sample document (like from scraper)
    sample_doc = {
        'url': 'https://www.srmist.edu.in/about',
        'page_title': 'About SRM - Best University in India',
        'content': """
        Home > About
        
        SRM Institute of Science and Technology - Leading Educational Institution
        
        SRM Institute of Science and Technology is one of the top ranking universities in India.
        Established in 1985, SRM has grown into a world-class institution. The university has
        over 60000 full time students from across India and 95+ countries. With more than 4460
        faculty members, SRM maintains an excellent student-faculty ratio.
        
        Our campuses are located in multiple cities. The main campus is in Kattankulathur,
        near Chennai. We also have campuses in Ramapuram, Vadapalani, NCR Delhi, and other
        locations. Each campus is equipped with modern facilities and infrastructure.
        
        Visit https://www.srmist.edu.in for more information.
        Contact us at admissions@srmist.edu.in
        
        Follow us on social media!
        Copyright © 2024 SRM. All rights reserved.
        """
    }
    
    print(f"\n📄 Processing document: {sample_doc['page_title']}")
    print(f"   URL: {sample_doc['url']}")
    print(f"   Original content: {len(sample_doc['content'])} chars")
    
    # Step 1: Clean
    cleaner = TextCleaner()
    cleaned_doc = cleaner.clean_document(sample_doc)
    
    print(f"\n🧹 After cleaning: {len(cleaned_doc['content'])} chars")
    print(f"   Removed: {len(sample_doc['content']) - len(cleaned_doc['content'])} chars")
    
    # Step 2: Chunk
    chunker = TextChunker(min_chunk_size=50, max_chunk_size=100)
    chunks = chunker.chunk_document(cleaned_doc)
    
    print(f"\n✂️  Created {len(chunks)} chunks:")
    
    for chunk in chunks:
        print(f"\n   {chunk['chunk_id']}:")
        print(f"   - Position: {chunk['metadata']['chunk_position']}")
        print(f"   - Words: {chunk['word_count']}")
        print(f"   - Text: {chunk['text'][:80]}...")
    
    # Verify metadata
    for chunk in chunks:
        assert 'chunk_id' in chunk
        assert 'text' in chunk
        assert 'word_count' in chunk
        assert 'metadata' in chunk
        assert 'source_url' in chunk['metadata']
        assert chunk['metadata']['source_url'] == sample_doc['url']
    
    print("\n✅ Document processing tests passed!")


def test_statistics():
    """Test statistics generation."""
    
    print("\n" + "="*70)
    print("🧪 TEST 4: Statistics Generation")
    print("="*70)
    
    # Create sample chunks
    sample_chunks = [
        {'chunk_id': 'c1', 'word_count': 100, 'metadata': {'source_url': 'url1'}},
        {'chunk_id': 'c2', 'word_count': 150, 'metadata': {'source_url': 'url1'}},
        {'chunk_id': 'c3', 'word_count': 120, 'metadata': {'source_url': 'url2'}},
    ]
    
    chunker = TextChunker()
    stats = chunker.get_statistics(sample_chunks)
    
    print("\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Verify calculations
    assert stats['total_chunks'] == 3
    assert stats['total_words'] == 370
    assert stats['average_words_per_chunk'] == 370/3
    assert stats['min_words'] == 100
    assert stats['max_words'] == 150
    assert stats['unique_sources'] == 2
    
    print("\n✅ Statistics tests passed!")


def main():
    """Run all tests."""
    
    print("\n" + "="*70)
    print("🧪 TESTING TEXT PROCESSING PIPELINE")
    print("="*70)
    
    try:
        test_text_cleaner()
        test_text_chunker()
        test_document_processing()
        test_statistics()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n💡 Your text processing pipeline is working correctly!")
        print("\n🎯 Next steps:")
        print("   1. Run the scraper: python scripts/scrape_website.py")
        print("   2. Process the data: python scripts/process_data.py")
        print("   3. Check output: data/processed/chunks.json")
        print("\n" + "="*70)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()