"""
Hybrid Search: Semantic + Keyword for Better Accuracy
"""
from typing import List, Dict
import numpy as np
from rank_bm25 import BM25Okapi
import json

class HybridSearchEngine:
    """
    Combines semantic search (FAISS) with keyword search (BM25)
    This dramatically improves accuracy!
    """
    
    def __init__(self, chunks_data: List[Dict]):
        """Initialize both search methods"""
        self.chunks = chunks_data
        self.chunk_texts = [chunk['text'] for chunk in chunks_data]
        
        # Initialize BM25 for keyword search
        tokenized_chunks = [text.lower().split() for text in self.chunk_texts]
        self.bm25 = BM25Okapi(tokenized_chunks)
        
        print("✅ Hybrid search initialized (Semantic + Keyword)")
    
    def search(self, 
               query: str, 
               semantic_results: List[tuple],  # From FAISS
               top_k: int = 5,
               semantic_weight: float = 0.6,
               keyword_weight: float = 0.4) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword
        
        Args:
            query: User query
            semantic_results: Results from FAISS [(idx, score), ...]
            top_k: Number of results
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
        
        Returns:
            List of results with hybrid scores
        """
        
        # 1. Get keyword search scores
        query_tokens = query.lower().split()
        keyword_scores = self.bm25.get_scores(query_tokens)
        
        # 2. Normalize scores to 0-1 range
        semantic_scores_dict = {}
        for idx, score in semantic_results:
            # Lower distance = higher similarity
            # Convert to 0-1 score (1 = perfect match)
            normalized = 1 / (1 + score)
            semantic_scores_dict[idx] = normalized
        
        # Normalize keyword scores
        if keyword_scores.max() > 0:
            keyword_scores_norm = keyword_scores / keyword_scores.max()
        else:
            keyword_scores_norm = keyword_scores
        
        # 3. Combine scores
        hybrid_scores = {}
        
        # Add semantic scores
        for idx, score in semantic_scores_dict.items():
            hybrid_scores[idx] = semantic_weight * score
        
        # Add keyword scores
        for idx, score in enumerate(keyword_scores_norm):
            if idx in hybrid_scores:
                hybrid_scores[idx] += keyword_weight * score
            else:
                hybrid_scores[idx] = keyword_weight * score
        
        # 4. Sort by hybrid score
        sorted_indices = sorted(
            hybrid_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # 5. Build results
        results = []
        for idx, score in sorted_indices:
            results.append({
                'chunk': self.chunks[idx],
                'hybrid_score': score,
                'semantic_score': semantic_scores_dict.get(idx, 0),
                'keyword_score': keyword_scores_norm[idx] if idx < len(keyword_scores_norm) else 0
            })
        
        return results


def test_hybrid_search():
    """Test hybrid search vs pure semantic"""
    
    # Load chunks
    with open('data/processed/chunks.json', 'r') as f:
        chunks = json.load(f)
    
    # Initialize
    hybrid = HybridSearchEngine(chunks)
    
    # Test query
    test_query = "What is the fee structure for B.Tech?"
    
    print("\n" + "="*70)
    print("TESTING HYBRID SEARCH")
    print("="*70)
    print(f"Query: {test_query}")
    
    # Simulate semantic results (you'd get these from FAISS)
    # For demo, using mock data
    mock_semantic = [(0, 0.5), (1, 0.6), (2, 0.7)]
    
    results = hybrid.search(test_query, mock_semantic)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Hybrid Score: {result['hybrid_score']:.3f}")
        print(f"   Semantic: {result['semantic_score']:.3f}")
        print(f"   Keyword: {result['keyword_score']:.3f}")
        print(f"   Preview: {result['chunk']['text'][:100]}...")


if __name__ == "__main__":
    # First install BM25
    print("Installing BM25...")
    import subprocess
    subprocess.run(["pip", "install", "rank-bm25"], check=True)
    
    test_hybrid_search()