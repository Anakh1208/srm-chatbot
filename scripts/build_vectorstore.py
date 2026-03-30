#!/usr/bin/env python3
"""
Build Vector Store
-----------------
Complete pipeline to build FAISS vector database from processed chunks.

Pipeline:
1. Load processed chunks (data/processed/chunks.json)
2. Generate embeddings using all-MiniLM-L6-v2
3. Create FAISS index
4. Add embeddings to index
5. Save index and embeddings
6. Test search functionality

This creates the "knowledge base" that powers your RAG chatbot!

Usage:
    python scripts/build_vectorstore.py
"""


import sys
import os
import json
import faiss
import numpy as np
from datetime import datetime


# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from preprocessing.embeddings_generator import EmbeddingsGenerator
from backend.core.vector_store import FAISSVectorStore


def load_chunks(chunks_file: str) -> list:
    """
    Load processed chunks from JSON file.

    Args:
        chunks_file: Path to chunks.json

    Returns:
        List of chunk dictionaries
    """
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        print(f"✅ Loaded {len(chunks)} chunks from {chunks_file}")
        return chunks

    except FileNotFoundError:
        print(f"❌ Error: File not found: {chunks_file}")
        print(f"💡 Make sure you've processed the data first:")
        print(f"   python scripts/process_data.py")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {chunks_file}")
        print(f"   {str(e)}")
        sys.exit(1)


def test_search(vector_store, generator, test_queries):
    """
    Test the vector store with sample queries.

    Args:
        vector_store: Loaded FAISS vector store
        generator: Embeddings generator
        test_queries: List of test questions
    """
    print("\n" + "=" * 70)
    print("🔍 TESTING VECTOR SEARCH")
    print("=" * 70)

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest Query {i}: \"{query}\"")
        print("-" * 70)

        # Generate query embedding
        query_embedding = generator.generate_embedding(query)

        # Search
        results = vector_store.search(query_embedding, top_k=3)

        # Display results
        for result in results:
            text = result['chunk']   # ✅ FIXED INDENT
            print(f"\nRank {result['rank']} (score: {result['score']:.4f}):")
            print(f"  Text: {text[:150]}...")

        print("\n" + "-" * 70)

def main():
    """
    Main pipeline to build vector store.
    """
    print("\n" + "=" * 70)
    print("🎓 SRM CHATBOT - BUILD VECTOR STORE")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Configuration
    chunks_file = "data/processed/chunks.json"
    output_dir = "data/vectorstore"
    model_name = "all-MiniLM-L6-v2"

    # ========================================================================
    # STEP 1: Load Processed Chunks
    # ========================================================================
    print("=" * 70)
    print("📂 STEP 1: Loading Processed Chunks")
    print("=" * 70)
    chunks = load_chunks(chunks_file)

    print(f"\n📊 Chunk Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Sample chunk ID: {chunks[0]['chunk_id']}")
    print(f"   Sample source: {chunks[0]['metadata']['page_title']}")

    # ========================================================================
    # STEP 2: Initialize Embeddings Generator
    # ========================================================================
    print("\n" + "=" * 70)
    print("🤖 STEP 2: Initializing Embeddings Model")
    print("=" * 70)
    print(f"Model: {model_name}")
    print("This will download ~80MB on first run...\n")

    generator = EmbeddingsGenerator(model_name=model_name)

    # ========================================================================
    # STEP 3: Generate Embeddings
    # ========================================================================
    print("=" * 70)
    print("🔄 STEP 3: Generating Embeddings")
    print("=" * 70)
    print(f"Processing {len(chunks)} chunks...")
    print("This may take 1-5 minutes depending on your CPU...\n")

    embeddings, chunks = generator.embed_chunks(chunks)

    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Size: {embeddings.nbytes / 1024 / 1024:.2f} MB")

    # ========================================================================
    # STEP 4: Build FAISS Index
    # ========================================================================
    print("\n" + "=" * 70)
    print("🗄️  STEP 4: Building FAISS Index")
    print("=" * 70)

    d = generator.embedding_dimension
    vector_store = FAISSVectorStore(embedding_dim=d, index_type="flat")

    # Extract text list for your FAISSVectorStore.add_texts
    texts = [chunk["text"] for chunk in chunks]

    # Convert embeddings to list of arrays (FAISSVectorStore.add_texts expects list)
    embeddings_list = [emb.tolist() for emb in embeddings]

    vector_store.add_texts(texts=texts, embeddings=embeddings_list)

    # Also expose total_vectors for logging
    print(f"📊 Index Statistics:")
    print(f"   Total vectors: {vector_store.index.ntotal}")
    print(f"   Dimension: {vector_store.embedding_dim}")
    print(f"   Index type: {vector_store.index_type}")

    # ========================================================================
    # STEP 5: Save Everything
    # ========================================================================
    print("\n" + "=" * 70)
    print("💾 STEP 5: Saving Vector Store")
    print("=" * 70)

    # Save FAISS index + metadata via your FAISSVectorStore.save
    vector_store.save(output_dir)

    # Also save embeddings + chunks separately (for debugging/analysis)
    generator.save_embeddings(embeddings, chunks, output_dir)

    # ========================================================================
    # STEP 6: Test Search
    # ========================================================================
    print("=" * 70)
    print("🧪 STEP 6: Testing Search Functionality")
    print("=" * 70)

    test_queries = [
        "What programs does SRM offer?",
        "How to apply for admission?",
        "What are the campus facilities?",
    ]

    test_search(vector_store, generator, test_queries)

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("✨ VECTOR STORE BUILT SUCCESSFULLY!")
    print("=" * 70)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Output files in: {output_dir}/")
    print(f"   - index.faiss          (FAISS index)")
    print(f"   - texts.pkl            (Texts metadata)")
    print(f"   - embeddings.npy       (Raw embeddings)")
    print(f"   - config.json          (Index config)")
    print(f"   - chunks.pkl           (Chunk metadata, from embeddings_generator.save_embeddings)")

    print(f"\n📊 Final Statistics:")
    print(f"   Chunks indexed: {len(chunks)}")
    print(f"   Embedding dimension: {generator.embedding_dimension}")
    print(f"   Model: {model_name}")
    print(f"   Index type: {vector_store.index_type} (exact search)")

    print(f"\n🎯 Next Steps:")
    print(f"   1. Test queries: python scripts/test_query.py")
    print(f"   2. Build RAG engine: Create backend/core/rag_engine.py")
    print(f"   3. Start building the FastAPI backend")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Building interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during building: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)