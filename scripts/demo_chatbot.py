#!/usr/bin/env python3
"""
Demo Chatbot - Working Version for Presentation
-----------------------------------------------
Uses retrieved context directly without LLM to avoid crashes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing.embeddings_generator import EmbeddingsGenerator
from backend.core.vector_store import FAISSVectorStore


class DemoChatbot:
    """Simple chatbot that shows retrieved context as answers."""
    
    def __init__(self, vectorstore_dir: str):
        print("\n🚀 Initializing Demo Chatbot...")
        
        # Load embeddings generator
        print("📥 Loading embedding model...")
        self.embeddings_generator = EmbeddingsGenerator('all-MiniLM-L6-v2')
        
        # Load vector store
        print("📂 Loading vector store...")
        self.vector_store = FAISSVectorStore(
            dimension=self.embeddings_generator.embedding_dimension
        )
        self.vector_store.load_index(vectorstore_dir)
        
        print("✅ Demo Chatbot ready!\n")
    
    def answer_question(self, query: str):
        """Answer a question using retrieved context."""
        
        print(f"\n{'='*70}")
        print(f"❓ Question: {query}")
        print('='*70)
        
        # Generate query embedding
        query_embedding = self.embeddings_generator.generate_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=3)
        
        print(f"\n🔍 Retrieved {len(results)} relevant chunks:")
        
        if not results:
            print("\n💬 Answer:")
            print("-" * 70)
            print("I couldn't find specific information about this on the SRM website.")
            print("-" * 70)
            return
        
        # Show retrieval results
        for i, result in enumerate(results, 1):
            chunk = result['chunk']
            score = result['score']
            print(f"\n📄 Chunk {i} (Similarity: {score:.4f})")
            print(f"   Source: {chunk['metadata']['page_title']}")
            print(f"   Preview: {chunk['text'][:100]}...")
        
        # Create answer from retrieved context
        print("\n💬 Answer:")
        print("-" * 70)
        
        # Use the most relevant chunk
        best_chunk = results[0]['chunk']
        context = best_chunk['text']
        
        # Extract relevant sentences (simple approach)
        sentences = context.split('.')
        relevant_sentences = []
        
        query_words = set(query.lower().split())
        for sentence in sentences[:5]:  # First 5 sentences
            sentence_words = set(sentence.lower().split())
            if len(query_words & sentence_words) > 0:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer = '. '.join(relevant_sentences[:3]) + '.'
        else:
            # Just use first part of best chunk
            answer = '. '.join(sentences[:3]) + '.'
        
        print(answer)
        print("-" * 70)
        
        # Show sources
        print(f"\n📚 Sources:")
        for i, result in enumerate(results, 1):
            chunk = result['chunk']
            print(f"\n{i}. {chunk['metadata']['page_title']}")
            print(f"   🔗 {chunk['metadata']['source_url']}")
            print(f"   📊 Relevance Score: {result['score']:.4f}")
        
        print("\n" + "="*70)


def main():
    """Run the demo chatbot."""
    
    vectorstore_dir = "data/vectorstore"
    
    if not os.path.exists(os.path.join(vectorstore_dir, 'faiss.index')):
        print("❌ Vector store not found!")
        print("Build it first: python scripts/build_vectorstore.py")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🎓 SRM UNIVERSITY DEMO CHATBOT")
    print("="*70)
    print("\n💡 This demo shows the RAG retrieval system working!")
    print("   Answers are extracted directly from retrieved context.")
    print("\n⌨️  Commands:")
    print("   - Type any question about SRM")
    print("   - 'quit' or 'exit' to stop")
    print("="*70)
    
    try:
        chatbot = DemoChatbot(vectorstore_dir)
        
        # Demo mode - show some example questions
        example_questions = [
            "What programs does SRM offer?",
            "Tell me about SRM admissions",
            "What are the campus facilities?",
        ]
        
        print("\n📝 Example Questions:")
        for i, q in enumerate(example_questions, 1):
            print(f"   {i}. {q}")
        
        while True:
            query = input("\n💭 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for the demo!")
                break
            
            chatbot.answer_question(query)
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo ended!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()