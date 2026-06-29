import structlog
from fastapi import APIRouter, Depends, status, Body
from app.middleware.rate_limiter import get_required_user, get_optional_user
from app.services.auth import AuthService
from app.utils.errors import AuthenticationException
from supabase import create_client, Client
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()
auth_service = AuthService()

# Client used to update profile details in Supabase database
db_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@router.post("/auth/google", status_code=status.HTTP_200_OK)
def authenticate_google(id_token: str = Body(..., embed=True)):
    """
    Verify Google OAuth token and upsert the corresponding user profile in profiles table.
    """
    user_info = auth_service.verify_token(id_token)
    if not user_info:
        raise AuthenticationException("Google authentication failed. Invalid token.")
        
    try:
        # Sync user profile with database
        logger.info("Syncing user profile with database...", user_id=user_info["id"])
        db_client.table("profiles").upsert({
            "id": user_info["id"],
            "email": user_info["email"],
            "display_name": user_info["display_name"],
            "avatar_url": user_info["avatar_url"],
            "updated_at": "now()"
        }).execute()
    except Exception as db_err:
        logger.warning("Failed to sync profile in database. Proceeding anyway.", error=str(db_err))
        
    return {
        "access_token": id_token,
        "user": user_info
    }

@router.get("/auth/me", status_code=status.HTTP_200_OK)
def get_me(user: dict = Depends(get_required_user)):
    """
    Return the current authenticated user's profile.
    """
    return user
