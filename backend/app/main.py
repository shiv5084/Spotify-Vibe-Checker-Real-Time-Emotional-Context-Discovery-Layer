import time
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logging import setup_logging
from app.utils.errors import VibeException
from app.middleware.request_id import RequestIDMiddleware
from app.routers import health_router, examples_router, auth_router, vibe_router

# Initialize structured logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(
        "Starting Vibe-Checker Backend API Server...",
        environment=settings.APP_ENV,
        qdrant_url=settings.QDRANT_URL,
        supabase_url=settings.SUPABASE_URL
    )
    yield
    # Shutdown actions
    logger.info("Stopping Vibe-Checker Backend API Server...")

# Initialize FastAPI App
app = FastAPI(
    title="Vibe-Checker API",
    description="Real-Time Emotional Context Discovery Layer API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# Allow local development and standard configured FRONTEND_URL
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL:
    clean_url = settings.FRONTEND_URL.rstrip("/")
    allowed_origins.extend([clean_url, f"{clean_url}/"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID Middleware
app.add_middleware(RequestIDMiddleware)

# Register routers
app.include_router(health_router, prefix="/api")
app.include_router(examples_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(vibe_router, prefix="/api")

# Root Endpoint
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Vibe-Checker API server!",
        "documentation": "/docs",
        "health": "/api/health"
    }

# Global Middleware for Request Logging (Timing/Latency)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Exclude health check from verbose request logging to prevent spam
    if not request.url.path.endswith("/health"):
        logger.info(
            "Processed HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
    return response

# Custom VibeException Handler (Empathetic error responses)
@app.exception_handler(VibeException)
async def vibe_exception_handler(request: Request, exc: VibeException):
    logger.warning(
        "Vibe Exception handled.",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "suggestion": exc.suggestion
            }
        }
    )

# General Exception Fallback Handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception.", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "A critical system error occurred on the server.",
                "suggestion": "Our team has been notified. Please try again shortly."
            }
        }
    )
