"""
FAISS Vector Store
"""
import os
import json
import faiss
import numpy as np
import pickle


class FAISSVectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.index = None
        self.texts = []
    
    def add_embeddings(self, texts: list, embeddings: np.ndarray):
        """
        Add texts and embeddings to the store
        
        Args:
            texts: List of text chunks
            embeddings: NumPy array of embeddings
        """
        if embeddings.shape[0] != len(texts):
            raise ValueError(f"Mismatch: {len(texts)} texts but {embeddings.shape[0]} embeddings")
        
        # Store texts
        self.texts = texts
        
        # Create index if needed
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.embedding_dim = dimension
        
        # Add to index
        self.index.add(embeddings.astype('float32'))
        print(f"✅ Added {len(texts)} vectors to FAISS index")
    
    def save_index(self, directory: str):
        """
        Save FAISS index and texts
        
        Args:
            directory: Save directory path
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(directory, 'faiss.index')
        faiss.write_index(self.index, index_path)
        print(f"✅ Saved FAISS index to {index_path}")
        
        # Save texts
        texts_path = os.path.join(directory, 'chunks.json')
        with open(texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(self.texts)} chunks to {texts_path}")
    
    def load_index(self, directory: str):
        """
        Load FAISS index and texts
        
        Args:
            directory: Directory to load from
        """
        # Load FAISS index
        index_path = os.path.join(directory, 'faiss.index')
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        self.index = faiss.read_index(index_path)
        print(f"✅ Loaded FAISS index from {index_path}")
        
        # Load texts
        texts_path = os.path.join(directory, 'chunks.json')
        if os.path.exists(texts_path):
            with open(texts_path, 'r', encoding='utf-8') as f:
                self.texts = json.load(f)
            print(f"✅ Loaded {len(self.texts)} chunks")
        else:
            print(f"⚠️ No chunks file found at {texts_path}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> list:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            k: Number of results
        
        Returns:
            List of dicts with chunk, score, rank
        """
        if self.index is None:
            raise ValueError("Index not loaded")
        
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Format results
        results = []
        for rank, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.texts):
                results.append({
                    'chunk': self.texts[idx],
                    'score': float(distance),
                    'rank': rank + 1
                })
        
        return results