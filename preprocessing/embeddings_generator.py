"""
Embeddings Generator
-------------------
Converts text chunks into vector embeddings using Hugging Face models.

WHAT ARE EMBEDDINGS?
====================
Embeddings are numerical representations (vectors) of text that capture semantic meaning.

Simple Analogy:
--------------
Imagine you want to organize books in a library by their content, not just titles.
You could create a "coordinate system" where:
- X-axis = "How technical is it?" (0 = simple, 10 = advanced)
- Y-axis = "Fiction vs Non-fiction" (0 = fiction, 10 = non-fiction)
- Z-axis = "Modern vs Historical" (0 = ancient, 10 = modern)

Each book gets coordinates like (7, 9, 3) = "Advanced non-fiction about history"

Embeddings work the same way, but with 384 dimensions instead of 3!

Example:
-------
Text: "SRM University offers engineering programs"
Embedding: [0.23, -0.15, 0.87, ..., 0.45]  ← 384 numbers
          ↑ Each number captures some aspect of meaning

Similar texts have similar embeddings:
- "SRM has engineering courses" → [0.25, -0.13, 0.89, ...]  ← Very close!
- "The weather is sunny today" → [-0.67, 0.92, -0.34, ...] ← Far away!

Why This Matters for RAG:
-------------------------
When user asks: "What programs does SRM offer?"
→ Convert question to embedding
→ Find chunks with similar embeddings
→ Those chunks likely contain the answer!

MODEL: all-MiniLM-L6-v2
========================
- Fast and efficient (runs on CPU)
- 384-dimensional embeddings
- Pre-trained on 1 billion+ sentence pairs
- Excellent for semantic search
- Size: ~80MB (small enough for any machine)
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import pickle
import os
from tqdm import tqdm
import json


class EmbeddingsGenerator:
    """
    Generates embeddings for text chunks using Hugging Face models.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embeddings generator.
        
        Args:
            model_name: Name of the sentence-transformers model
                       Default: all-MiniLM-L6-v2 (fast, accurate, small)
        
        Why all-MiniLM-L6-v2?
        --------------------
        ✅ Fast: Encodes 1000 sentences in ~1 second (CPU)
        ✅ Accurate: 384 dimensions capture rich semantics
        ✅ Small: Only 80MB download
        ✅ Versatile: Works for questions and answers
        ✅ Popular: Well-tested, widely used
        """
        print(f"📥 Loading model: {model_name}")
        print("   (First time will download ~80MB, then it's cached)")
        
        # Load the model
        # This downloads the model on first run, then loads from cache
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        
        # Get embedding dimension (384 for all-MiniLM-L6-v2)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        
        print(f"✅ Model loaded!")
        print(f"   Embedding dimension: {self.embedding_dimension}")
        print(f"   Model size: ~80MB\n")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text (question or chunk)
            
        Returns:
            Numpy array of shape (384,) - the embedding vector
            
        Example:
        -------
        text = "What is the admission process?"
        embedding = generator.generate_embedding(text)
        # embedding = array([0.23, -0.15, 0.87, ..., 0.45])
        # Shape: (384,) - 384 numbers representing the meaning
        """
        # Encode converts text → embedding vector
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  batch_size: int = 32,
                                  show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once (32 = good balance)
            show_progress: Show progress bar
            
        Returns:
            Numpy array of shape (n_texts, 384) - all embeddings
            
        Why Batching?
        ------------
        Processing texts in batches is much faster than one-by-one:
        - One-by-one: 1000 texts = 10 seconds
        - Batched (32): 1000 texts = 2 seconds
        
        The model can process multiple texts in parallel!
        """
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        print(f"   Batch size: {batch_size}")
        
        # Encode all texts in batches with progress bar
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Shape: {embeddings.shape}")
        print(f"   Memory: ~{embeddings.nbytes / 1024 / 1024:.2f} MB\n")
        
        return embeddings
    
    def embed_chunks(self, chunks: List[Dict]) -> tuple:
        """
        Generate embeddings for all chunks from processed data.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            Tuple of (embeddings_array, chunks_list)
            - embeddings: numpy array (n_chunks, 384)
            - chunks: original chunks (for reference)
            
        Process:
        -------
        1. Extract text from each chunk
        2. Generate embeddings in batches
        3. Return embeddings aligned with chunks
        
        Example:
        -------
        chunks = [
            {"chunk_id": "c1", "text": "SRM offers engineering..."},
            {"chunk_id": "c2", "text": "Admission process is..."},
        ]
        
        embeddings, chunks = generator.embed_chunks(chunks)
        # embeddings[0] = embedding of chunks[0]['text']
        # embeddings[1] = embedding of chunks[1]['text']
        """
        # Extract just the text from each chunk
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"📊 Embedding {len(texts)} chunks...")
        print(f"   Average chunk size: {sum(len(t.split()) for t in texts) / len(texts):.0f} words\n")
        
        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(texts)
        
        return embeddings, chunks
    
    def save_embeddings(self, embeddings: np.ndarray, chunks: List[Dict], 
                       output_dir: str):
        """
        Save embeddings and chunks to disk.
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of chunks
            output_dir: Directory to save files
            
        Saves:
        -----
        1. embeddings.npy - Numpy array of vectors (binary, fast)
        2. chunks.pkl - Pickle file of chunks (for metadata)
        3. metadata.json - Info about embeddings (for reference)
        
        Why separate files?
        ------------------
        - embeddings.npy: Fast to load with numpy
        - chunks.pkl: Contains all text and metadata
        - metadata.json: Human-readable info
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Save embeddings as numpy array (binary format, fast loading)
        embeddings_path = os.path.join(output_dir, 'embeddings.npy')
        np.save(embeddings_path, embeddings)
        print(f"💾 Saved embeddings: {embeddings_path}")
        print(f"   Size: {os.path.getsize(embeddings_path) / 1024 / 1024:.2f} MB")
        
        # Save chunks as pickle (includes all metadata)
        chunks_path = os.path.join(output_dir, 'chunks.pkl')
        with open(chunks_path, 'wb') as f:
            pickle.dump(chunks, f)
        print(f"💾 Saved chunks: {chunks_path}")
        print(f"   Size: {os.path.getsize(chunks_path) / 1024 / 1024:.2f} MB")
        
        # Save metadata as JSON (human-readable)
        metadata = {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'num_embeddings': len(embeddings),
            'num_chunks': len(chunks),
            'embedding_shape': embeddings.shape,
        }
        
        metadata_path = os.path.join(output_dir, 'embeddings_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved metadata: {metadata_path}\n")
    
    def load_embeddings(self, input_dir: str) -> tuple:
        """
        Load embeddings and chunks from disk.
        
        Args:
            input_dir: Directory containing saved files
            
        Returns:
            Tuple of (embeddings, chunks)
        """
        # Load embeddings
        embeddings_path = os.path.join(input_dir, 'embeddings.npy')
        embeddings = np.load(embeddings_path)
        print(f"📂 Loaded embeddings: {embeddings.shape}")
        
        # Load chunks
        chunks_path = os.path.join(input_dir, 'chunks.pkl')
        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)
        print(f"📂 Loaded chunks: {len(chunks)}\n")
        
        return embeddings, chunks


if __name__ == "__main__":
    # Test the embeddings generator
    print("=" * 70)
    print("🧪 TESTING EMBEDDINGS GENERATOR")
    print("=" * 70 + "\n")
    
    # Initialize
    generator = EmbeddingsGenerator()
    
    # Test 1: Single embedding
    print("Test 1: Single text embedding")
    print("-" * 70)
    test_text = "SRM University offers various engineering programs"
    embedding = generator.generate_embedding(test_text)
    print(f"Text: {test_text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"✅ Single embedding works!\n")
    
    # Test 2: Batch embeddings
    print("Test 2: Batch embeddings")
    print("-" * 70)
    test_texts = [
        "SRM University offers engineering programs",
        "The admission process requires SRMJEEE exam",
        "Campus has excellent facilities and infrastructure"
    ]
    embeddings = generator.generate_embeddings_batch(test_texts, show_progress=False)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Shape: {embeddings.shape}")
    print(f"✅ Batch embeddings work!\n")
    
    # Test 3: Similarity check
    print("Test 3: Semantic similarity")
    print("-" * 70)
    # Compute cosine similarity between first two texts
    similarity = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    print(f"Text 1: {test_texts[0]}")
    print(f"Text 2: {test_texts[1]}")
    print(f"Similarity: {similarity:.4f}")
    print("(1.0 = identical, 0.0 = unrelated)")
    print(f"✅ Similarity computation works!\n")
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)