import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.vector_store import FAISSVectorStore
from backend.core.embeddings import EmbeddingsGenerator

def debug_vectorstore():
    print("="*70)
    print("DEBUGGING VECTOR STORE - FIXED VERSION")
    print("="*70)
    
    embeddings_gen = EmbeddingsGenerator()
    vector_store = FAISSVectorStore()
    
    # Check if files exist first
    vs_path = 'data/vectorstore'
    files = ['index.faiss', 'texts.pkl', 'config.json']
    print("Checking files:")
    for f in files:
        path = os.path.join(vs_path, f)
        status = "✅" if os.path.exists(path) else "❌"
        print(f"  {status} {path}")
    
    # Try load
    try:
        vector_store.load(vs_path)
        print(f"\n📊 SUCCESS: {vector_store.index.ntotal} vectors loaded!")
        
        # Test search
        test_queries = ["Admission process", "B.Tech programs"]
        for query in test_queries:
            print(f"\n--- Testing: '{query}' ---")
            q_emb = embeddings_gen.embed([query])[0]
            results = vector_store.search(q_emb, top_k=3)
            print(f"Found {len(results)} results")
            for r in results:
                print(f"  Score: {r['score']:.3f} | {r['chunk'][:100]}...")
                
    except Exception as e:
        print(f"\n❌ Load failed: {e}")
        print("🔄 Run rebuild script next!")

if __name__ == "__main__":
    debug_vectorstore()