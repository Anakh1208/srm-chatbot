#!/usr/bin/env python3
"""
Lightweight RAG Chatbot (Mac-Optimized)
---------------------------------------
Uses smaller model to avoid memory issues on Mac.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.rag_engine import RAGEngine


def main():
    vectorstore_dir = "data/vectorstore"
    
    if not os.path.exists(os.path.join(vectorstore_dir, 'faiss.index')):
        print("❌ Vector store not found!")
        print("Build it first: python scripts/build_vectorstore.py")
        sys.exit(1)
    
    print("\n🚀 Starting Lightweight SRM Chatbot (Mac-Optimized)...")
    print("   Using smaller model to avoid crashes...\n")
    
    try:
        # Use smaller, faster model for Mac
        rag = RAGEngine(
            vectorstore_dir=vectorstore_dir,
            llm_model="google/flan-t5-small",  # ← Smaller model!
            top_k=3,
            relevance_threshold=1.5
        )
        
        print("\n" + "="*70)
        print("🎓 SRM UNIVERSITY CHATBOT (Lightweight)")
        print("="*70)
        print("\n💭 Ask your question (or 'quit' to exit)")
        
        while True:
            query = input("\n💭 You: ").strip()
            
            if not query or query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🤔 Thinking...")
            result = rag.answer_question(query)
            print(rag.format_response(result))
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)