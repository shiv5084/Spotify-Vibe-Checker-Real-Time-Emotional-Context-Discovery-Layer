import structlog
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.config import settings

logger = structlog.get_logger()

class AuthService:
    def __init__(self):
        # We use the anon key for user-facing auth client verification
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify the given JWT token against Supabase Auth.
        Returns a dictionary with user info if valid, else None.
        """
        if not token:
            return None
            
        try:
            logger.info("Verifying user JWT via Supabase Auth...")
            # Supabase auth.get_user verifies the token against the Supabase backend
            res = self.supabase.auth.get_user(token)
            if res and res.user:
                logger.info("Supabase JWT verification successful.", user_id=res.user.id)
                return {
                    "id": res.user.id,
                    "email": res.user.email,
                    "display_name": res.user.user_metadata.get("full_name") or res.user.user_metadata.get("name"),
                    "avatar_url": res.user.user_metadata.get("avatar_url")
                }
        except Exception as e:
            logger.warning("Supabase JWT verification failed.", error=str(e))
            
        return None
