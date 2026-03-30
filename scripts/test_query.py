#!/usr/bin/env python3
"""
Test Query Tool
--------------
Interactive CLI tool to test queries against your vector database.

This helps you verify that:
1. Vector store loads correctly
2. Search returns relevant results
3. Chunks contain useful information

Usage:
    python scripts/test_query.py
    
    Or with a specific query:
    python scripts/test_query.py "What programs does SRM offer?"
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.embeddings_generator import EmbeddingsGenerator
from backend.core.vector_store import FAISSVectorStore


def display_results(query: str, results: list, show_full_text: bool = False):
    """
    Display search results in a nice format.
    
    Args:
        query: The search query
        results: List of search results
        show_full_text: Whether to show full chunk text
    """
    print("\n" + "=" * 70)
    print(f"🔍 Query: \"{query}\"")
    print("=" * 70)
    
    if not results:
        print("\n❌ No results found!")
        return
    
    for result in results:
        chunk = result['chunk']
        score = result['score']
        rank = result['rank']
        
        print(f"\n📄 Result #{rank} (Similarity Score: {score:.4f})")
        print("-" * 70)
        print(f"📌 Source: {chunk['metadata']['page_title']}")
        print(f"🔗 URL: {chunk['metadata']['source_url']}")
        print(f"📊 Position: {chunk['metadata']['chunk_position']}")
        print(f"📏 Words: {chunk['word_count']}")
        
        print(f"\n💬 Content:")
        print("-" * 70)
        if show_full_text:
            print(chunk['text'])
        else:
            # Show first 300 characters
            preview = chunk['text'][:300]
            print(preview + "..." if len(chunk['text']) > 300 else preview)
        
        print("-" * 70)


def interactive_mode(vector_store: FAISSVectorStore, generator: EmbeddingsGenerator):
    """
    Run interactive query mode.
    
    Args:
        vector_store: Loaded FAISS vector store
        generator: Embeddings generator
    """
    print("\n" + "=" * 70)
    print("🎓 SRM CHATBOT - INTERACTIVE QUERY MODE")
    print("=" * 70)
    print("\nType your questions and see what the vector store retrieves!")
    print("Commands:")
    print("  - Type any question to search")
    print("  - 'full' - Toggle full text display")
    print("  - 'top N' - Change number of results (e.g., 'top 5')")
    print("  - 'stats' - Show vector store statistics")
    print("  - 'examples' - Show example queries")
    print("  - 'quit' or 'exit' - Exit the program")
    print("=" * 70)
    
    top_k = 3
    show_full_text = False
    
    while True:
        try:
            # Get user input
            query = input("\n💭 Your question: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif query.lower() == 'full':
                show_full_text = not show_full_text
                print(f"✅ Full text display: {'ON' if show_full_text else 'OFF'}")
                continue
            
            elif query.lower().startswith('top '):
                try:
                    top_k = int(query.split()[1])
                    print(f"✅ Now showing top {top_k} results")
                    continue
                except:
                    print("❌ Invalid format. Use: top 5")
                    continue
            
            elif query.lower() == 'stats':
                stats = vector_store.get_stats()
                print("\n📊 Vector Store Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            
            elif query.lower() == 'examples':
                print("\n💡 Example Queries:")
                examples = [
                    "What programs does SRM offer?",
                    "How to apply for admission?",
                    "What is the admission fee?",
                    "What are the campus facilities?",
                    "Tell me about placements",
                    "What entrance exams are required?",
                    "Where is SRM located?",
                    "What research opportunities are available?"
                ]
                for ex in examples:
                    print(f"   - {ex}")
                continue
            
            # Process query
            print(f"\n⏳ Searching...")
            
            # Generate query embedding
            query_embedding = generator.generate_embedding(query)
            
            # Search vector store
            results = vector_store.search(query_embedding, top_k=top_k)
            
            # Display results
            display_results(query, results, show_full_text)
            
            # Show relevance interpretation
            if results:
                best_score = results[0]['score']
                if best_score < 0.5:
                    print("\n✅ Excellent match! Very relevant results.")
                elif best_score < 1.0:
                    print("\n👍 Good match! Results are relevant.")
                elif best_score < 2.0:
                    print("\n⚠️  Fair match. Results may be somewhat relevant.")
                else:
                    print("\n⚠️  Weak match. You might want to rephrase your question.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def single_query_mode(query: str, vector_store: FAISSVectorStore, 
                     generator: EmbeddingsGenerator, top_k: int = 3):
    """
    Process a single query and display results.
    
    Args:
        query: The search query
        vector_store: Loaded FAISS vector store
        generator: Embeddings generator
        top_k: Number of results to return
    """
    print(f"\n⏳ Processing query...")
    
    # Generate query embedding
    query_embedding = generator.generate_embedding(query)
    
    # Search
    results = vector_store.search(query_embedding, top_k=top_k)
    
    # Display
    display_results(query, results, show_full_text=True)


def main():
    """
    Main function.
    """
    print("\n" + "=" * 70)
    print("🎓 SRM CHATBOT - QUERY TESTING TOOL")
    print("=" * 70)
    
    # Configuration
    vectorstore_dir = "data/vectorstore"
    model_name = "all-MiniLM-L6-v2"
    
    # Check if vector store exists
    if not os.path.exists(os.path.join(vectorstore_dir, 'faiss.index')):
        print(f"\n❌ Error: Vector store not found in {vectorstore_dir}/")
        print(f"💡 Build it first:")
        print(f"   python scripts/build_vectorstore.py")
        sys.exit(1)
    
    # Load embeddings generator
    print("\n📥 Loading embeddings model...")
    generator = EmbeddingsGenerator(model_name=model_name)
    
    # Load vector store
    print("📂 Loading vector store...")
    vector_store = FAISSVectorStore(dimension=generator.embedding_dimension)
    vector_store.load_index(vectorstore_dir)
    
    # Display stats
    stats = vector_store.get_stats()
    print(f"\n✅ Vector store loaded!")
    print(f"   Vectors: {stats['total_vectors']}")
    print(f"   Memory: {stats['memory_usage_mb']:.2f} MB")
    
    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        # Single query mode
        query = ' '.join(sys.argv[1:])
        single_query_mode(query, vector_store, generator)
    else:
        # Interactive mode
        interactive_mode(vector_store, generator)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)