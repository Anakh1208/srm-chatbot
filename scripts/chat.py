#!/usr/bin/env python3
"""
Interactive RAG Chatbot
----------------------
Command-line chatbot powered by RAG (Retrieval-Augmented Generation).

This demonstrates the complete RAG pipeline:
1. User asks question
2. Retrieve relevant context from vector store
3. Generate grounded answer using LLM
4. Display answer with sources

Usage:
    python scripts/chat.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.rag_engine import RAGEngine


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 70)
    print("🎓 SRM UNIVERSITY CHATBOT")
    print("   Powered by RAG (Retrieval-Augmented Generation)")
    print("=" * 70)
    print("\n💡 Ask me anything about SRM University!")
    print("   Examples:")
    print("   - What programs does SRM offer?")
    print("   - How do I apply for admission?")
    print("   - What are the campus facilities?")
    print("   - Tell me about placements")
    print("\n🎯 Features:")
    print("   ✅ Answers grounded in actual SRM website data")
    print("   ✅ Cites sources for transparency")
    print("   ✅ Says 'I don't know' instead of making things up")
    print("\n⌨️  Commands:")
    print("   - Type any question to get an answer")
    print("   - 'examples' - Show example questions")
    print("   - 'stats' - Show system statistics")
    print("   - 'help' - Show this message")
    print("   - 'quit' or 'exit' - Exit the chatbot")
    print("=" * 70)


def show_examples():
    """Show example queries."""
    examples = {
        "Admissions": [
            "What is the admission process?",
            "What entrance exams are required?",
            "How do I apply for B.Tech?",
            "What are the eligibility criteria?"
        ],
        "Academics": [
            "What engineering programs are offered?",
            "Tell me about the Computer Science department",
            "What is the curriculum for AI/ML?",
            "Are there research opportunities?"
        ],
        "Campus Life": [
            "What facilities are available on campus?",
            "Tell me about student clubs",
            "What sports facilities does SRM have?",
            "Where is SRM located?"
        ],
        "Placements": [
            "What is the placement record?",
            "Which companies visit for recruitment?",
            "What is the average package?",
            "Tell me about internship opportunities"
        ]
    }
    
    print("\n" + "=" * 70)
    print("💡 EXAMPLE QUESTIONS")
    print("=" * 70)
    
    for category, questions in examples.items():
        print(f"\n📌 {category}:")
        for q in questions:
            print(f"   • {q}")
    
    print("=" * 70)


def show_stats(rag: RAGEngine):
    """Show system statistics."""
    stats = rag.vector_store.get_stats()
    
    print("\n" + "=" * 70)
    print("📊 SYSTEM STATISTICS")
    print("=" * 70)
    print(f"\n🗄️  Vector Store:")
    print(f"   Total chunks: {stats['total_vectors']}")
    print(f"   Embedding dimension: {stats['dimension']}")
    print(f"   Index type: {stats['index_type']}")
    print(f"   Memory usage: {stats['memory_usage_mb']:.2f} MB")
    
    print(f"\n🤖 Models:")
    print(f"   Embedding: {rag.embeddings_generator.model_name}")
    print(f"   LLM: {rag.llm_model_name}")
    
    print(f"\n⚙️  Configuration:")
    print(f"   Top-k retrieval: {rag.top_k}")
    print(f"   Relevance threshold: {rag.relevance_threshold}")
    
    print("=" * 70)


def interactive_chat(rag: RAGEngine):
    """
    Run interactive chat session.
    
    Args:
        rag: RAG engine instance
    """
    conversation_history = []
    
    while True:
        try:
            # Get user input
            query = input("\n💭 You: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            query_lower = query.lower()
            
            if query_lower in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for chatting! Goodbye!")
                break
            
            elif query_lower == 'help':
                print_welcome()
                continue
            
            elif query_lower == 'examples':
                show_examples()
                continue
            
            elif query_lower == 'stats':
                show_stats(rag)
                continue
            
            elif query_lower == 'history':
                if conversation_history:
                    print("\n" + "=" * 70)
                    print("📜 CONVERSATION HISTORY")
                    print("=" * 70)
                    for i, item in enumerate(conversation_history, 1):
                        print(f"\n{i}. You: {item['query']}")
                        print(f"   Bot: {item['answer'][:100]}...")
                    print("=" * 70)
                else:
                    print("\n📜 No conversation history yet")
                continue
            
            elif query_lower == 'clear':
                conversation_history = []
                print("\n✅ Conversation history cleared")
                continue
            
            # Process the question
            print("\n🤔 Thinking...")
            result = rag.answer_question(query)
            
            # Display formatted response
            print(rag.format_response(result))
            
            # Add to history
            conversation_history.append({
                'query': query,
                'answer': result['answer'],
                'has_context': result['has_context']
            })
            
            # Show tip for first question
            if len(conversation_history) == 1:
                print("\n💡 Tip: Type 'examples' to see more questions you can ask!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("   Please try rephrasing your question.")


def single_question_mode(rag: RAGEngine, question: str):
    """
    Answer a single question and exit.
    
    Args:
        rag: RAG engine instance
        question: The question to answer
    """
    print(f"\n❓ Question: {question}\n")
    
    result = rag.answer_question(question)
    print(rag.format_response(result))


def main():
    """
    Main function.
    """
    # Configuration
    vectorstore_dir = "data/vectorstore"
    
    # Check if vector store exists
    if not os.path.exists(os.path.join(vectorstore_dir, 'faiss.index')):
        print("\n" + "=" * 70)
        print("❌ ERROR: Vector store not found!")
        print("=" * 70)
        print(f"\nThe vector store is missing from: {vectorstore_dir}/")
        print("\n📝 To fix this, run:")
        print("   1. python scripts/scrape_website.py  (if not done)")
        print("   2. python scripts/process_data.py    (if not done)")
        print("   3. python scripts/build_vectorstore.py")
        print("\nThen try again!")
        print("=" * 70)
        sys.exit(1)
    
    # Initialize RAG engine
    print("\n🚀 Starting SRM Chatbot...")
    print("   (This may take a minute on first run...)\n")
    
    try:
        rag = RAGEngine(
            vectorstore_dir=vectorstore_dir,
            top_k=3,
            relevance_threshold=1.5
        )
        
        # Check if question provided as command line argument
        if len(sys.argv) > 1:
            # Single question mode
            question = ' '.join(sys.argv[1:])
            single_question_mode(rag, question)
        else:
            # Interactive mode
            print_welcome()
            interactive_chat(rag)
    
    except ImportError as e:
        print("\n❌ Missing required library!")
        if "transformers" in str(e):
            print("\n📦 Install transformers:")
            print("   pip install transformers torch")
        else:
            print(f"\n{str(e)}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error starting chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0),
        