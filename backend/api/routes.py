"""
API Routes (Groq removed)
---------
FastAPI endpoints for the SRM chatbot.
"""

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
import logging
import time
from typing import Optional
from datetime import datetime

# ADD after imports
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_chunks_from_supabase() -> list:
    """Fetch chunks from Supabase for RAG queries"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("documents").select("content").execute()
        
        if response.data:
            return [doc['content'] for doc in response.data]
        return []
        
    except Exception as e:
        print(f"❌ Supabase fetch failed: {str(e)}")
        return []

from backend.api.schemas import (
    ChatRequest, 
    ChatResponse, 
    HealthResponse,
    ErrorResponse,
    Source
)
from backend.core.rag_engine import RAGEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global RAG engine instance
rag_engine: Optional[RAGEngine] = None


def initialize_rag_engine(vectorstore_dir: str):
    global rag_engine


rag_engine = None

try:
    rag_engine = RAGEngine(vectorstore_dir='data/vectorstore')
    logger.info("✅ RAG engine initialized successfully")

except Exception as e:
    logger.error(f"❌ Failed to initialize RAG engine: {str(e)}")


def calculate_confidence(scores: list) -> str:
    if not scores:
        return "low"
    
    avg_score = sum(scores) / len(scores)
    
    if avg_score < 0.5:
        return "high"
    elif avg_score < 1.0:
        return "medium"
    else:
        return "low"


@router.get("/")
async def root():
    return {
        "name": "SRM Chatbot API",
        "version": "2.0.0",
        "description": "RAG-powered chatbot for SRM Institute of Science and Technology",
        "features": [
            "Retrieval Augmented Generation (RAG)",
            "Ollama local LLM responses",
            "Source citations",
            "Confidence scoring"
        ],
        "endpoints": {
            "/": "GET - API information",
            "/chat": "POST - Ask questions",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Enhanced chat endpoint with sources, confidence, and follow-ups
    DEMO-READY VERSION
    """
    try:
        logger.info(f"📥 Received query: {request.query}")
        
        # Get RAG response
        result = rag_engine.answer_question(request.query)
        
        # 🔥 CLEAN OUTPUT
        import re
        clean_answer = re.sub(r'http\S+', '', result['answer'])  # remove links
        clean_answer = clean_answer.split("You can also")[0]     # remove extra junk
        
        # Enhanced response structure for demo
        response = {
            'query': request.query,
            'answer': clean_answer,
            'suggestions': [
                "Ask about academic programs",
                "Learn about admissions process",
                "Explore campus facilities"
            ],
            'confidence': result['confidence'],
            'has_context': result['has_context'],
            'sources': result.get('sources', []),
            'timestamp': str(time.time())
        }
        
        logger.info(f"✅ Query processed successfully. Confidence: {result['confidence']}")
        
        return response

    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
  
        return {
            'query': request.query,
            'answer': "I encountered an error processing your question. Please try rephrasing or ask something else.",
            'confidence': 'Error',
            'has_context': False,
            'sources': [],
            'follow_ups': ["General admission process", "Available programs", "Contact information"],
            'timestamp': str(time.time())
        }


@router.get("/health", response_model=HealthResponse)
async def health_check():

    if rag_engine is None:
        return HealthResponse(
            status="unhealthy",
            version="2.0.0",
            services={
                "rag_engine": "not_initialized",
                "vector_store": "unknown",
                "llm": "unknown"
            }
        )
    
    try:
        stats = rag_engine.vector_store.get_stats()
        
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            services={
                "rag_engine": "ready",
                "vector_store": "ready",
                "llm": "ollama"
            },
            stats={
                "total_chunks": stats['total_vectors'],
                "embedding_dimension": stats['dimension'],
                "memory_usage_mb": round(stats['memory_usage_mb'], 2)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        
        return HealthResponse(
            status="degraded",
            version="2.0.0",
            services={
                "rag_engine": "error",
                "vector_store": "unknown",
                "llm": "unknown"
            }
        )


@router.get("/stats")
async def get_statistics():

    if rag_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG engine not initialized"
        )
    
    try:
        stats = rag_engine.vector_store.get_stats()
        
        return {
            "vector_store": {
                "total_vectors": stats['total_vectors'],
                "dimension": stats['dimension'],
                "index_type": stats['index_type'],
                "memory_usage_mb": round(stats['memory_usage_mb'], 2)
            },
            "models": {
                "embedding_model": rag_engine.embeddings_generator.model_name,
                "llm_model": "ollama (gemma3:1b)"
            },
            "config": {
                "top_k": rag_engine.top_k
            },
            "features": [
                "RAG with source citations",
                "Ollama local LLM",
                "Confidence scoring"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )