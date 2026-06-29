import structlog
from fastapi import APIRouter, status
from app.services.cache import CacheService
from app.services.qdrant_client import QdrantService
from supabase import create_client, Client
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
def check_health():
    """
    Check the health of external services: Redis, Qdrant, and Supabase.
    """
    health_status = {
        "status": "healthy",
        "services": {
            "redis": "healthy",
            "qdrant": "healthy",
            "supabase": "healthy"
        }
    }
    
    # 1. Check Redis
    try:
        cache = CacheService()
        if not cache.redis_enabled:
            health_status["services"]["redis"] = "degraded (in-memory fallback)"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error("Health check: Redis connectivity failed.", error=str(e))
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # 2. Check Qdrant
    try:
        qdrant = QdrantService()
        # Fetching collection is a lightweight connectivity check
        qdrant.client.get_collection(qdrant.collection_name)
    except Exception as e:
        logger.error("Health check: Qdrant connectivity failed.", error=str(e))
        health_status["services"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # 3. Check Supabase
    try:
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        # Run a simple select count check
        supabase.table("profiles").select("count", count="exact").limit(1).execute()
    except Exception as e:
        logger.error("Health check: Supabase connectivity failed.", error=str(e))
        health_status["services"]["supabase"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
