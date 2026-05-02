"""
RAG Engine - Retrieval-Augmented Generation
-------------------------------------------
Complete RAG system that retrieves relevant context and generates grounded answers.

WHAT IS RAG?
============
RAG = Retrieval-Augmented Generation

Traditional LLM (without RAG):
User: "What programs does SRM offer?"
LLM: [Guesses from training data, may hallucinate]
Problem: ❌ Might be outdated or wrong

RAG-Enhanced LLM:
User: "What programs does SRM offer?"
  ↓
1. Retrieve relevant chunks from vector store
2. Feed chunks + question to LLM
3. LLM answers based on provided context
Result: ✅ Accurate, grounded in actual data

HOW THIS REDUCES HALLUCINATION:
===============================

Hallucination = When AI makes up information that sounds plausible but is false

Without RAG:
- LLM relies only on training data (may be outdated)
- No way to verify accuracy
- Fills gaps with "reasonable guesses"
- Confidently states wrong information

With RAG:
- LLM sees actual, current information from your website
- Instructed to ONLY use provided context
- If context doesn't contain answer → Say "I don't know"
- Cannot make up facts (they must be in context)

Example of Hallucination Prevention:
------------------------------------
Query: "What is the tuition fee for B.Tech AI/ML?"

Without RAG:
LLM: "The tuition is approximately ₹2.5 lakhs per year"
Reality: Completely made up! ❌

With RAG (no relevant context found):
LLM: "I couldn't find information about B.Tech AI/ML tuition fees 
      on the SRM website. Please contact admissions."
Reality: Honest, helpful response ✅

With RAG (relevant context found):
Retrieved: "B.Tech programs cost ₹2.8 lakhs per year"
LLM: "According to SRM's website, B.Tech programs cost ₹2.8 lakhs 
      per year."
Reality: Accurate, sourced response ✅
"""

import sys
import os
from typing import List, Dict, Tuple, Optional
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from preprocessing.embeddings_generator import EmbeddingsGenerator
from backend.core.vector_store import FAISSVectorStore


class RAGEngine:
    """
    Complete RAG system with retrieval and generation.
    """
    
    load_dotenv()

# Initialize Supabase client (module-level)
try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected")
    else:
        supabase = None
        print("⚠️ Supabase credentials not found - using local storage")
except Exception as e:
    supabase = None
    print(f"⚠️ Supabase connection failed: {str(e)}")
    
    def __init__(self, 
                 vectorstore_dir: str,
                 model_name: str = 'all-MiniLM-L6-v2',
                 llm_model: str = 'google/flan-t5-base',
                 top_k: int = 3,
                 relevance_threshold: float = 1.5):
        """
        Initialize the RAG engine.
        
        Args:
            vectorstore_dir: Directory containing FAISS index
            model_name: Embedding model (for query encoding)
            llm_model: LLM for generation (default: FLAN-T5)
            top_k: Number of chunks to retrieve
            relevance_threshold: Max distance for relevant results
            
        LLM Choice: google/flan-t5-base
        ----------------------------------
        ✅ Fast: Runs on CPU (no GPU needed)
        ✅ Small: ~250MB download
        ✅ Good: Fine-tuned for instructions
        ✅ Free: Open-source, no API costs
        
        Alternatives:
        - flan-t5-small: Faster, less accurate
        - flan-t5-large: Slower, more accurate (needs GPU)
        - For production: Use GPT-4 or Claude API
        """
        print("🚀 Initializing RAG Engine...")
        
        # Load embeddings generator
        print(f"📥 Loading embedding model: {model_name}")
        self.embeddings_generator = EmbeddingsGenerator(model_name)
        
        # Load vector store
        print(f"📂 Loading vector store from: {vectorstore_dir}")
        self.vector_store = FAISSVectorStore(
            dimension=self.embeddings_generator.embedding_dimension
        )
        self.vector_store.load_index(vectorstore_dir)
        
        # Configuration
        self.top_k = top_k
        self.relevance_threshold = relevance_threshold
        
        # Load LLM
        print(f"🤖 Loading language model: {llm_model}")
        self.llm_model_name = llm_model
        self._load_llm()
        
        print("✅ RAG Engine ready!\n")
    
    def _load_llm(self):
        """
        Load the language model for generation.
        
        Using FLAN-T5:
        -------------
        FLAN-T5 is an instruction-tuned model (Google)
        - Trained to follow instructions
        - Good at Q&A tasks
        - Works on CPU
        - Free and open-source
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            print("   Downloading model (first time only, ~250MB)...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            self.llm = AutoModelForSeq2SeqLM.from_pretrained(self.llm_model_name)
            
            print("   ✅ LLM loaded successfully!")
            
        except ImportError:
            print("❌ Error: transformers library not installed")
            print("   Install with: pip install transformers")
            sys.exit(1)
    
    def retrieve_context(self, query: str) -> Tuple[List[Dict], List[float]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (relevant_chunks, scores)
            
        Process:
        -------
        1. Convert query to embedding
        2. Search FAISS index
        3. Filter by relevance threshold
        4. Return relevant chunks
        """
        print(f"🔍 Retrieving context for: \"{query}\"")
        
        # Step 1: Generate query embedding
        query_embedding = self.embeddings_generator.generate_embedding(query)
        
        # Step 2: Search vector store
        results = self.vector_store.search(query_embedding, top_k=self.top_k)
        
        # Step 3: Filter by relevance
        relevant_chunks = []
        scores = []
        
        for result in results:
            score = result['score']
            
            # Only include if below threshold (lower score = more similar)
            if score <= self.relevance_threshold:
                relevant_chunks.append(result['chunk'])
                scores.append(score)
                print(f"   ✅ Found relevant chunk (score: {score:.4f})")
            else:
                print(f"   ⚠️  Chunk not relevant enough (score: {score:.4f})")
        
        if not relevant_chunks:
            print("   ❌ No relevant chunks found!")
        else:
            print(f"   📊 Retrieved {len(relevant_chunks)} relevant chunks")
        
        return relevant_chunks, scores
    
    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        """
        Build the prompt for the LLM.
        
        This is CRITICAL for preventing hallucination!
        
        Key Components:
        --------------
        1. Clear instructions
        2. Retrieved context
        3. The question
        4. Explicit constraints
        
        Why This Works:
        --------------
        - LLM sees actual information (not guessing)
        - Told to ONLY use provided context
        - Instructed to say "I don't know" if unsure
        - Cannot make up facts
        """
        # Build context from retrieved chunks
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            # Include source for transparency
            source = chunk['metadata']['page_title']
            text = chunk['text']
            
            context_parts.append(f"[Source {i}: {source}]\n{text}")
        
        context = "\n\n".join(context_parts)
        
        # Build the complete prompt
        prompt = f"""You are a helpful assistant answering questions about SRM Institute of Science and Technology.

INSTRUCTIONS:
- Answer the question using ONLY the context provided below
- If the context doesn't contain the answer, say "I couldn't find this information on the SRM website"
- Be specific and cite the source when possible
- Do NOT make up or infer information not in the context
- Keep your answer concise and helpful

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        """
        Generate answer using the LLM.
        
        Args:
            prompt: Complete prompt with context + question
            
        Returns:
            Generated answer
            
        Generation Parameters:
        ---------------------
        - max_length: 200 tokens (concise answers)
        - temperature: 0.3 (low = more focused, less creative)
        - top_p: 0.9 (nucleus sampling)
        - do_sample: True (allows some variation)
        
        Why Low Temperature?
        -------------------
        Temperature controls randomness:
        - 0.0 = Always picks most likely word (deterministic)
        - 1.0 = More random, creative
        - 0.3 = Focused but not robotic
        
        For factual Q&A, we want LOW temperature (facts, not creativity!)
        """
        print("🤖 Generating answer...")
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        
        # Generate answer
        outputs = self.llm.generate(
            inputs.input_ids,
            max_length=200,      # Keep answers concise
            temperature=0.3,     # Low temperature = factual
            top_p=0.9,           # Nucleus sampling
            do_sample=True,      # Allow some variation
            num_beams=4,         # Beam search for quality
            early_stopping=True
        )
        
        # Decode answer
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print("✅ Answer generated!")
        
        return answer.strip()
    
    def answer_question(self, query: str) -> Dict:
        """
        Complete RAG pipeline: retrieve → generate → return.
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
            
        Pipeline:
        --------
        1. Retrieve relevant chunks
        2. Check if context is sufficient
        3. Build prompt with context
        4. Generate answer
        5. Return with sources
        """
        print("\n" + "=" * 70)
        print(f"❓ Question: {query}")
        print("=" * 70)
        
        # Step 1: Retrieve context
        chunks, scores = self.retrieve_context(query)
        
        # Step 2: Check if we have relevant context
        if not chunks:
            # NO RELEVANT CONTEXT FOUND
            # This is where we prevent hallucination!
            answer = "I couldn't find this information on the SRM website. Please try rephrasing your question or contact SRM directly for more information."
            
            return {
                'answer': answer,
                'sources': [],
                'scores': [],
                'has_context': False,
                'query': query
            }
        
        # Step 3: Build prompt
        prompt = self.build_prompt(query, chunks)
        
        # Step 4: Generate answer
        answer = self.generate_answer(prompt)
        
        # Step 5: Build sources list
        sources = []
        for chunk in chunks:
            sources.append({
                'title': chunk['metadata']['page_title'],
                'url': chunk['metadata']['source_url'],
                'preview': chunk['text'][:150] + "..."
            })
        
        # Step 6: Return complete response
        result = {
            'answer': answer,
            'sources': sources,
            'scores': scores,
            'has_context': True,
            'query': query
        }
        
        print("\n✅ RAG pipeline complete!")
        print("=" * 70)
        
        return result
    
    def format_response(self, result: Dict) -> str:
        """
        Format the response for display.
        
        Args:
            result: Result dictionary from answer_question()
            
        Returns:
            Formatted string for display
        """
        output = []
        
        # Answer
        output.append(f"\n💬 Answer:")
        output.append("-" * 70)
        output.append(result['answer'])
        output.append("-" * 70)
        
        # Sources (if any)
        if result['sources']:
            output.append(f"\n📚 Sources:")
            for i, source in enumerate(result['sources'], 1):
                output.append(f"\n{i}. {source['title']}")
                output.append(f"   🔗 {source['url']}")
                output.append(f"   📝 {source['preview']}")
        else:
            output.append("\n⚠️  No sources found in database")
        
        # Confidence indicator
        output.append(f"\n📊 Confidence:")
        if result['has_context']:
            avg_score = sum(result['scores']) / len(result['scores'])
            if avg_score < 0.5:
                confidence = "High ✅"
            elif avg_score < 1.0:
                confidence = "Medium ⚠️"
            else:
                confidence = "Low ⚠️"
            output.append(f"   {confidence} (avg score: {avg_score:.4f})")
        else:
            output.append("   No relevant context found")
        
        return "\n".join(output)


if __name__ == "__main__":
    # Test the RAG engine
    print("=" * 70)
    print("🧪 TESTING RAG ENGINE")
    print("=" * 70)
    
    # Initialize
    try:
        rag = RAGEngine(
            vectorstore_dir="../../data/vectorstore",
            top_k=3
        )
        
        # Test queries
        test_queries = [
            "What programs does SRM offer?",
            "How do I apply for admission?",
            "What is the quantum physics curriculum?"  # Should fail
        ]
        
        for query in test_queries:
            result = rag.answer_question(query)
            print(rag.format_response(result))
            print("\n" + "=" * 70 + "\n")
        
        print("✅ RAG Engine tests complete!")
        
    except FileNotFoundError:
        print("❌ Vector store not found!")
        print("   Build it first: python scripts/build_vectorstore.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()