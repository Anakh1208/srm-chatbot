"""
API Module
---------
FastAPI routes and schemas for the SRM Chatbot API.
"""

from .routes import router
from .schemas import ChatRequest, ChatResponse, HealthResponse

__all__ = ['router', 'ChatRequest', 'ChatResponse', 'HealthResponse']