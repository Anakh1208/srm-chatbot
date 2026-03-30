"""
API Schemas
----------
Pydantic models for request/response validation.

Why Pydantic?
------------
Pydantic provides:
✅ Automatic data validation
✅ Type checking
✅ JSON serialization/deserialization
✅ Auto-generated API documentation
✅ Clear error messages

Example:
-------
If user sends: {"query": 123}  (wrong type)
Pydantic returns: "query must be a string"
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.
    
    Example:
    -------
    POST /chat
    {
        "query": "What programs does SRM offer?",
        "conversation_id": "user123_session456"  (optional)
    }
    """
    query: str = Field(
        ...,  # Required field
        min_length=1,
        max_length=500,
        description="User's question (1-500 characters)",
        example="What programs does SRM offer?"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID for tracking",
        example="user123_session456"
    )
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        """Ensure query is not just whitespace."""
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class Source(BaseModel):
    """
    Model for a source/citation.
    
    Represents one chunk that was retrieved to answer the question.
    """
    title: str = Field(
        ...,
        description="Title of the source page",
        example="Admissions - SRMIST"
    )
    
    url: str = Field(
        ...,
        description="URL of the source",
        example="https://www.srmist.edu.in/admissions"
    )
    
    preview: str = Field(
        ...,
        description="Preview/snippet of the content",
        example="The admission process for B.Tech programs..."
    )
    
    relevance_score: float = Field(
        ...,
        description="Similarity score (lower = more relevant)",
        example=0.23
    )


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    
    Example:
    -------
    {
        "answer": "SRM offers B.Tech programs in...",
        "sources": [
            {
                "title": "Academics - SRMIST",
                "url": "https://...",
                "preview": "...",
                "relevance_score": 0.23
            }
        ],
        "confidence": "high",
        "has_context": true,
        "query": "What programs does SRM offer?",
        "timestamp": "2024-02-05T10:30:45.123456"
    }
    """
    answer: str = Field(
        ...,
        description="Generated answer to the user's question",
        example="SRM offers various B.Tech programs including Computer Science, AI/ML, Mechanical Engineering..."
    )
    
    sources: List[Source] = Field(
        default_factory=list,
        description="List of sources used to generate the answer"
    )
    
    confidence: str = Field(
        ...,
        description="Confidence level: high, medium, or low",
        example="high"
    )
    
    has_context: bool = Field(
        ...,
        description="Whether relevant context was found",
        example=True
    )
    
    query: str = Field(
        ...,
        description="The original query (for reference)",
        example="What programs does SRM offer?"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID if provided in request"
    )


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Example:
    -------
    GET /health
    {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-02-05T10:30:45.123456",
        "services": {
            "rag_engine": "ready",
            "vector_store": "ready",
            "llm": "ready"
        },
        "stats": {
            "total_chunks": 198,
            "embedding_dimension": 384
        }
    }
    """
    status: str = Field(
        ...,
        description="Overall service status",
        example="healthy"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )
    
    services: dict = Field(
        default_factory=dict,
        description="Status of individual services",
        example={
            "rag_engine": "ready",
            "vector_store": "ready",
            "llm": "ready"
        }
    )
    
    stats: Optional[dict] = Field(
        None,
        description="Optional system statistics",
        example={
            "total_chunks": 198,
            "embedding_dimension": 384
        }
    )


class ErrorResponse(BaseModel):
    """
    Response model for errors.
    
    Example:
    -------
    {
        "error": "Invalid request",
        "detail": "Query is too long (max 500 characters)",
        "timestamp": "2024-02-05T10:30:45.123456"
    }
    """
    error: str = Field(
        ...,
        description="Error type",
        example="Invalid request"
    )
    
    detail: str = Field(
        ...,
        description="Detailed error message",
        example="Query is too long (max 500 characters)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )


# Example usage for documentation
EXAMPLE_CHAT_REQUEST = {
    "query": "What are the admission requirements for B.Tech?",
    "conversation_id": "user123_conv456"
}

EXAMPLE_CHAT_RESPONSE = {
    "answer": "The admission requirements for B.Tech at SRM include passing 12th grade with Physics, Chemistry, and Mathematics with at least 60% marks. Students must also take the SRMJEEE entrance exam.",
    "sources": [
        {
            "title": "Admissions - SRMIST",
            "url": "https://www.srmist.edu.in/admissions",
            "preview": "Candidates seeking admission to B.Tech programs must have...",
            "relevance_score": 0.23
        }
    ],
    "confidence": "high",
    "has_context": True,
    "query": "What are the admission requirements for B.Tech?",
    "timestamp": "2024-02-05T10:30:45.123456",
    "conversation_id": "user123_conv456"
}