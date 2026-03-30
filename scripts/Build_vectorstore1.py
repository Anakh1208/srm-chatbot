"""
Rebuild vector store from chunks
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.vector_store import FAISSVectorStore
from backend.core.embeddings import EmbeddingsGenerator

def build_vector_store():
    """Build FAISS vector store from chunks"""

   

    print("="*70)
    print("BUILDING VECTOR STORE FROM SCRAPED DATA")
    print("="*70)
    
    # 1. Load chunks
    chunk_files = [
        'data/processed/improved_chunks.json',
        'data/processed/chunks.json'
    ]
    
    chunks_data = None
    for chunk_file in chunk_files:
        if os.path.exists(chunk_file):
            print(f"\n✅ Found chunks: {chunk_file}")
            with open(chunk_file, 'r') as f:
                chunks_data = json.load(f)
            break
    
    if not chunks_data:
        print("❌ No chunks found! Run chunking first:")
        print("   python scripts/improved_chunking.py")
        return
    
    # Extract text from chunks
    if isinstance(chunks_data[0], dict):
        if 'text' in chunks_data[0]:
            chunks = [chunk['text'] for chunk in chunks_data]
        elif 'content' in chunks_data[0]:
            chunks = [chunk['content'] for chunk in chunks_data]
        else:
            chunks = [str(chunk) for chunk in chunks_data]
    else:
        chunks = chunks_data
    
    print(f"\n📊 Loaded {len(chunks)} chunks")
    print(f"   Sample: {chunks[0][:100]}...")
    
    # 2. Generate embeddings
    print("\n🔄 Generating embeddings...")
    embeddings_gen = EmbeddingsGenerator()
    embeddings = embeddings_gen.embed(chunks)
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # 3. Build FAISS index
    print("\n🔄 Building FAISS index...")
    vector_store = FAISSVectorStore()
    vector_store.add_embeddings(embeddings, [{"text": c} for c in chunks])
    
    # 4. Save index
    output_dir = 'data/vectorstore'
    os.makedirs(output_dir, exist_ok=True)
    
    vector_store.save_index(output_dir)
    print(f"\n✅ Vector store saved to {output_dir}")
    
    # 5. Test search
    print("\n🧪 Testing search...")
    test_query = "What programs does SRM offer?"
    test_embedding = embeddings_gen.embed([test_query])[0]
    results = vector_store.search(test_embedding, top_k=3)
    
    print(f"\nTest query: '{test_query}'")
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results[:3], 1):
        chunk_text = result.get('chunk', '')[:150]
        score = result.get('score', 0)
        print(f"\n{i}. Score: {score:.3f}")
        print(f"   Text: {chunk_text}...")
    
    print("\n" + "="*70)
    print("✅ VECTOR STORE BUILT SUCCESSFULLY!")
    print("="*70)
    print("\nRestart your server to use the new data:")
    print("  python -m uvicorn backend.main:app --reload --port 8001")
    

if __name__ == "__main__":
    build_vector_store()