# improved_retrieval.py - Update your RAG engine

def retrieve_relevant_context(self, query: str) -> dict:
    """
    Retrieve ONLY the most relevant chunks
    
    Changes from your current code:
    - top_k = 3 (was probably 5-10)
    - Higher threshold (0.5 instead of 1.5)
    - Score-based filtering
    """
    
    # Generate query embedding
    query_embedding = self.embeddings_generator.generate_embeddings([query])[0]
    
    # Search vector store - ONLY top 3
    results = self.vector_store.search(
        query_embedding=query_embedding,
        top_k=3  # ⭐ REDUCED from 5+
    )
    
    # Filter by score
    good_results = []
    for chunk_id, score in zip(results['indices'], results['scores']):
        # ⭐ STRICTER threshold
        if score < 0.8:  # Lower distance = better match
            chunk_text = self.vector_store.get_chunk_text(chunk_id)
            good_results.append({
                'text': chunk_text,
                'score': float(score),
                'chunk_id': int(chunk_id)
            })
    
    # If no good results, return empty
    if not good_results:
        return {
            'has_context': False,
            'chunks': [],
            'answer': create_no_context_response(query)
        }
    
    return {
        'has_context': True,
        'chunks': good_results,
        'answer': None  # Will generate with LLM
    }