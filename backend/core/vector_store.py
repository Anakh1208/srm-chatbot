import faiss
import numpy as np
import os
import pickle
import json
from typing import List, Dict, Any

class FAISSVectorStore:
    def __init__(self, embedding_dim: int = 384, index_type: str = "flat"):
        """Initialize FAISS index"""
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.texts = [] # This stores our actual sentences

        if index_type == "flat":
            self.index = faiss.IndexFlatL2(embedding_dim)
        else:
            raise ValueError(f"Unknown index_type: {index_type}")

        print(f"✅ FAISS index initialized (Dim: {embedding_dim})")

    def add_texts(self, texts: List[str], embeddings: List[np.ndarray]):
        """Add texts and embeddings to index"""
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.texts.extend(texts)
        print(f"✅ Added {len(texts)} texts. Total in index: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        # Ensure query is 2D array for FAISS
        query_emb = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_emb, top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if 0 <= idx < len(self.texts):
                results.append({
                    "score": float(distances[0][i]),
                    "chunk": self.texts[idx],
                    "rank": int(idx),
                })
        return results

    def save(self, save_path: str):
        """Save index + metadata"""
        os.makedirs(save_path, exist_ok=True)
        # Use consistent filenames
        faiss.write_index(self.index, os.path.join(save_path, "faiss.index"))
        
        with open(os.path.join(save_path, "chunks.json"), 'w') as f:
            json.dump(self.texts, f)
        
        print(f"✅ Saved vector store to {save_path}")

    def load(self, directory: str):
        """Load FAISS index and chunks from directory"""
        index_path = os.path.join(directory, 'faiss.index')
        chunks_path = os.path.join(directory, 'chunks.json')
        
        if not os.path.exists(index_path):
            print(f"⚠️ Index file not found: {index_path}")
            return
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load chunks
        if os.path.exists(chunks_path):
            with open(chunks_path, 'r') as f:
                self.texts = json.load(f)
            print(f"✅ Loaded index and {len(self.texts)} chunks")
        else:
            print(f"⚠️ Chunks file not found: {chunks_path}")

    # ALIAS: This ensures that if rag_engine calls load_index(), it still works!
    def load_index(self, directory: str):
        return self.load(directory)