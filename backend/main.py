"""
FastAPI Application - Mac Compatible (Ollama)
------------------------------------
Main application file for the SRM Chatbot API.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging
from contextlib import asynccontextmanager
from backend.api.routes import router, initialize_rag_engine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info("🚀 Starting SRM Chatbot API with Ollama...")

    try:
        initialize_rag_engine(
            vectorstore_dir="data/vectorstore"
        )
        logger.info("✅ RAG engine initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {str(e)}")
        logger.error("⚠️  API will start but /chat endpoint will not work")

    logger.info("✅ API is ready!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down SRM Chatbot API...")
    logger.info("✅ Cleanup complete")


# ✅ Create FastAPI app FIRST before anything uses it
app = FastAPI(
    title="SRM Chatbot API",
    description="RAG-powered chatbot for SRM University (Ollama-based)",
    version="2.0.0",
    lifespan=lifespan
)


# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✅ CORS enabled")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    logger.warning(f"❌ Validation error: {error_messages}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": error_messages,
            "timestamp": str(time.time())
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": str(time.time())
        }
    )


# ✅ Include routers AFTER app is defined
app.include_router(router, prefix="", tags=["chatbot"])


logger.info("✅ All routes registered (chat + auth)")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "SRM Chatbot API",
        "version": "2.0.0",
        "description": "RAG-powered chatbot for SRM Institute of Science and Technology",
        "features": [
            "Retrieval Augmented Generation (RAG)",
            "Ollama local LLM",
            "SMS OTP Authentication",
            "Source citations",
            "Confidence scoring"
        ],
        "endpoints": {
            "/": "GET - API information",
            "/chat": "POST - Ask questions about SRM",
            "/auth/send-otp": "POST - Send OTP",
            "/auth/verify-otp": "POST - Verify OTP",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        },
        "documentation": "/docs"
    }


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )