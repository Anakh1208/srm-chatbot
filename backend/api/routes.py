"""
API Routes (Groq removed)
---------
FastAPI endpoints for the SRM chatbot.
"""

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from datetime import datetime

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


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest, req: Request):

    if rag_engine is None:
        logger.error("RAG engine not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG engine is not initialized. Please try again later."
        )
    
    try:
        logger.info(f"📥 Received query: {request.query}")
        
        result = rag_engine.answer_question(request.query)

        # ✅ Directly use answer (no Groq)
        conversational_answer = result['answer']
        
        # Build sources list
        sources = []
        for i, source_data in enumerate(result.get('sources', [])):
            sources.append(Source(
                title=source_data.get('title', 'SRM Source'),
                url=source_data.get('url', ''),
                preview=source_data.get('text', ''),
                relevance_score=source_data.get('score', 0.0)
            ))
        
        confidence = calculate_confidence(
            [s.get('score', 1.0) for s in result.get('sources', [])]
        )
        
        response = ChatResponse(
            answer=conversational_answer,
            sources=sources,
            confidence=confidence,
            has_context=result.get('has_context', False),
            query=request.query,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"✅ Query processed successfully. Confidence: {confidence}")
        
        return response
        
    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your query"
        )


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