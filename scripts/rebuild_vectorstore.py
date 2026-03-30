"""
Rebuild vector store from chunks
"""
import json
import sys
import os
import faiss
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.embeddings import EmbeddingsGenerator

def rebuild():
    print("="*70)
    print("REBUILDING VECTOR STORE")
    print("="*70)
    
    # 1. Load chunks
    chunk_file = 'data/processed/chunks.json'
    if not os.path.exists(chunk_file):
        print(f"❌ No chunks found at {chunk_file}")
        print("Run: python scripts/improved_chunking.py first")
        return
    
    with open(chunk_file, 'r') as f:
        chunks_data = json.load(f)
    
    print(f"\n✅ Loaded {len(chunks_data)} chunks")
    
    # 2. Extract texts
    texts = []
    for chunk in chunks_data:
        if isinstance(chunk, dict):
            text = chunk.get('text', str(chunk))
        else:
            text = str(chunk)
        if len(text.strip()) > 20:
            texts.append(text.strip())
    
    print(f"✅ Extracted {len(texts)} valid texts")
    print(f"   Sample: {texts[0][:150]}...")
    
    # 3. Generate embeddings
    print(f"\n🔄 Generating embeddings...")
    embeddings_gen = EmbeddingsGenerator()
    embeddings = embeddings_gen.embed(texts)
    embeddings_array = np.array(embeddings).astype('float32')
    
    print(f"✅ Generated embeddings: {embeddings_array.shape}")
    
    # 4. Create FAISS index
    print(f"\n🔄 Building FAISS index...")
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    
    # 5. Save
    output_dir = 'data/vectorstore'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save index
    faiss.write_index(index, os.path.join(output_dir, 'faiss.index'))
    
    # Save chunks
    with open(os.path.join(output_dir, 'chunks.json'), 'w') as f:
        json.dump(texts, f, indent=2)
    
    print(f"\n✅utput_dir/")
    print(f"   - faiss.index ({index.ntotal} vectors)")
    print(f"   - chunks.json ({len(texts)} chunks)")
    
    print("\n" + "="*70)
    print("✅ REBUILD COMPLETE!")
    print("="*70)
    print("\n🔄 Restart server:")
    print("   python -m uvicorn backend.main:app --reload --port 8001")

if __name__ == "__main__":
    rebuild()
