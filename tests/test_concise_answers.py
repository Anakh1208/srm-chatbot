"""
Test script for concise chatbot responses.
"""

import os
import sys

# Ensure project root is importable no matter where this script runs from.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.rag_engine import RAGEngine


def test_chatbot():
    """Test the improved concise chatbot."""
    rag = RAGEngine(vectorstore_dir="data/vectorstore")

    test_queries = [
        "What is the fee for B.Tech CSE?",
        "How to apply for admission?",
        "Tell me about placements",
        "Where is the library?",
        "Hostel facilities for girls",
    ]

    print("=" * 70)
    print("TESTING CONCISE RESPONSES")
    print("=" * 70)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)

        result = rag.answer_question(query)

        print(f"Answer:\n{result['answer']}\n")
        print(f"Confidence: {result['confidence']}")
        print(f"Word count: {len(result['answer'].split())} words")
        print("=" * 70)


if __name__ == "__main__":
    test_chatbot()
