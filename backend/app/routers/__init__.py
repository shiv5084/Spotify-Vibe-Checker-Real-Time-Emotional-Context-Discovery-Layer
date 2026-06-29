from app.routers.health import router as health_router
from app.routers.examples import router as examples_router
from app.routers.auth import router as auth_router
from app.routers.vibe import router as vibe_router

__all__ = [
    "health_router",
    "examples_router",
    "auth_router",
    "vibe_router",
]
