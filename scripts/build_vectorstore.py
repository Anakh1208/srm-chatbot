"""
Build FAISS vector store from MANUAL curated data only
NO web scraping, NO crawled data
"""
import sys
import os
import json
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.vector_store import FAISSVectorStore
from backend.core.embeddings import EmbeddingsGenerator


def load_manual_data() -> list:
    """
    Load ONLY manual curated JSON files
    NO scraped/crawled data
    """
    print("\n📂 Loading manual curated data...")
    
    # Paths to manual JSON files
    manual_files = [
        project_root / "data" / "srm_knowledge_base.json",
        project_root / "data" / "srmist_chatbot_dataset.json"
    ]
    
    all_chunks = []
    
    for file_path in manual_files:
        if not file_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
        
        print(f"   Loading: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract text from each entry
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    text = item['text'].strip()
                    if text:
                        all_chunks.append(text)
        
        print(f"   ✅ Loaded {len([d for d in data if isinstance(d, dict) and 'text' in d])} chunks")
    
    print(f"\n✅ Total chunks from manual data: {len(all_chunks)}")
    return all_chunks


def main():
    print("\n" + "="*70)
    print("🚀 BUILDING FAISS VECTOR STORE - MANUAL DATA ONLY")
    print("="*70)
    
    # Paths
    vectorstore_dir = str(project_root / "data" / "vectorstore")
    
    try:
        # Step 1: Load ONLY manual curated data
        texts = load_manual_data()
        
        if not texts:
            print("❌ No data loaded! Check JSON files.")
            sys.exit(1)
        
        print(f"\n📊 Processing {len(texts)} chunks")
        
        # Step 2: Initialize embeddings generator
        print("\n🔧 Initializing embeddings generator...")
        embeddings_generator = EmbeddingsGenerator()
        
        # Step 3: Generate embeddings
        print(f"\n🔢 Generating embeddings...")
        all_embeddings = []
        batch_size = 32
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embs = embeddings_generator.embed(batch)
            all_embeddings.extend(batch_embs)
            print(f"   Progress: {min(i + batch_size, len(texts))}/{len(texts)}")
        
        embeddings = np.array(all_embeddings, dtype=np.float32)
        print(f"✅ Generated embeddings: {embeddings.shape}")
        
        # Step 4: Build FAISS index
        print(f"\n🏗️ Building FAISS index...")
        vector_store = FAISSVectorStore()
        vector_store.add_embeddings(texts, embeddings)
        
        # Step 5: Save
        print(f"\n💾 Saving to {vectorstore_dir}...")
        os.makedirs(vectorstore_dir, exist_ok=True)
        vector_store.save_index(vectorstore_dir)
        
        # Step 6: Test
        print(f"\n🧪 Testing search...")
        test_query = "What programs does SRM offer?"
        test_emb = embeddings_generator.embed([test_query])[0]
        results = vector_store.search(test_emb, k=3)
        
        print(f"✅ Retrieved {len(results)} results")
        if results:
            print(f"\n📄 Top result:")
            print(f"   {results[0].get('chunk', '')[:150]}...")
        
        print("\n" + "="*70)
        print("✅ BUILD COMPLETE - MANUAL DATA ONLY")
        print("="*70)
        print(f"📍 Location: {vectorstore_dir}")
        print(f"📊 Total vectors: {len(embeddings)}")
        print(f"🎯 Source: manual_data1.json + manual_data2.json")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()