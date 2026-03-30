"""
Enhanced RAG Engine with concise responses - FIXED VERSION
"""
import os
import numpy as np
from typing import List, Dict
from .vector_store import FAISSVectorStore
from .embeddings import EmbeddingsGenerator
from .prompts import create_answer_prompt, create_no_context_response, extract_topics_for_followups
from .context_cleaner import ContextCleaner
from .ollama_llm import OllamaLLM


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine with concise answers
    """

    def __init__(self, vectorstore_dir: str, top_k: int = 6):
        """
        Initialize RAG Engine
        
        Args:
            vectorstore_dir: Path to vector store directory
            top_k: Default number of results to retrieve
        """
        self.vectorstore_dir = vectorstore_dir
        self.vector_store = FAISSVectorStore()

        # Try to load existing vector store
        try:
            self.vector_store.load_index(vectorstore_dir)
            print(f"✅ Loaded vector store from {vectorstore_dir}")
        except Exception as e:
            print(f"⚠️ Could not load vector store: {str(e)}")

        self.top_k = top_k
        self.embeddings_generator = EmbeddingsGenerator()
        self.context_cleaner = ContextCleaner()
        self.llm = OllamaLLM()

        print("✅ RAG Engine initialized with concise response mode")

    def retrieve_relevant_context(self, query: str, top_k: int = None) -> dict:
        """
        Retrieve ONLY the most relevant chunks
        
        Args:
            query: User question
            top_k: Number of results (uses self.top_k if None)
        
        Returns:
            Dict with has_context, chunks, answer
        """
        if top_k is None:
            top_k = self.top_k

        try:
            # Generate query embedding
            query_embedding = self.embeddings_generator.embed([query])[0]
            
            # Search vector store
            results = self.vector_store.search(query_embedding, top_k)

            # Handle empty results
            if not results:
                return {
                    'has_context': False,
                    'chunks': [],
                    'answer': create_no_context_response(query)
                }

            # DEBUG: Print retrieved chunks
            print("\n===== DEBUG RETRIEVAL =====")
            for r in results:
                print(r.get('chunk', '')[:200])
            print("===== END =====\n")

            # Process results
            processed_results = []
            for result in results:
                chunk_text = result.get('chunk', '')
                score = result.get('score', 999.0)

                if chunk_text:
                    processed_results.append({
                        'text': chunk_text,
                        'score': float(score),
                        'chunk_id': result.get('rank', -1)
                    })

            return {
                'has_context': True,
                'chunks': processed_results,
                'answer': None
            }

        except Exception as e:
            print(f"❌ Error in retrieve_relevant_context: {str(e)}")
            return {
                'has_context': False,
                'chunks': [],
                'answer': create_no_context_response(query)
            }

    def answer_question(self, query: str) -> dict:
        """
        Main method - Generate concise answer with follow-ups
        
        Args:
            query: User question
        
        Returns:
            Dict with answer, sources, confidence
        """
        try:
            # Step 1: Retrieve (top 6)
            retrieval_result = self.retrieve_relevant_context(query, top_k=6)
            
            if not retrieval_result['has_context']:
                # No relevant context found
                return {
                    'answer': retrieval_result['answer'],
                    'sources': [],
                    'confidence': 'low',
                    'has_context': False
                }
            
            # Step 2: Clean context
            clean_context = self.context_cleaner.clean_chunks(
                chunks=retrieval_result['chunks'],
                max_context_length=600
            )
            
            # Remove duplicates
            clean_context = self.context_cleaner.deduplicate(clean_context)
            
            # Step 3: Generate answer (simple extraction)
            answer = self._extract_answer_from_context(clean_context, query)
            
            # Step 4: Build sources
            sources = []
            for chunk in retrieval_result['chunks'][:3]:
                sources.append({
                    'text': chunk['text'][:200] + '...',
                    'score': chunk['score']
                })
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': 'high',
                'has_context': True
            }
            
        except Exception as e:
            print(f"❌ Error in answer_question: {str(e)}")
            return {
                'answer': f"I'm having trouble processing your question. Please try rephrasing.\n\n{create_no_context_response(query)}",
                'sources': [],
                'confidence': 'error',
                'has_context': False
            }

    def _extract_answer_from_context(self, context: str, query: str) -> str:
        """Extract clean, short answer from context"""
        
        if not context or len(context.strip()) < 20:
            return create_no_context_response(query)
        
        # Split into sentences - remove markdown symbols
        sentences = context.replace('*', '').replace('-', '').split('. ')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Find most relevant sentences (contain query keywords)
        query_words = set(query.lower().split())
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words & sentence_words)
            if overlap > 0:
                scored_sentences.append((overlap, sentence))
        
        # Sort by relevance
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # Take top 2 sentences (max 60 words total)
        answer_sentences = []
        word_count = 0
        
        for _, sentence in scored_sentences[:5]:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= 60:
                answer_sentences.append(sentence)
                word_count += sentence_words
            else:
                break
            
            if len(answer_sentences) >= 2:
                break
        
        if not answer_sentences:
            # Fallback: first 2 sentences
            answer_sentences = sentences[:2]
        
        # Clean answer - remove all markdown
        answer = '. '.join(answer_sentences).strip()
        answer = answer.replace('**', '').replace('*', '').replace('_', '')
        answer = answer.replace('  ', ' ')
        
        if not answer.endswith('.'):
            answer += '.'
        
        # Keep answer under 60 words
        words = answer.split()
        if len(words) > 60:
            answer = ' '.join(words[:60]) + '...'
        
        # Add follow-ups
        answer = self._add_followups(answer, query)
        
        return answer

    def _add_followups(self, answer: str, query: str) -> str:
        """Add clean follow-up questions"""
        
        followups = extract_topics_for_followups(query)
        
        # Clean answer first
        answer = answer.strip()
        
        # Add follow-ups in clean format
        followup_text = "\n\nWould you like to know:\n"
        for i, topic in enumerate(followups, 1):
            followup_text += f"{i}. {topic}\n"
        
        return answer + followup_text