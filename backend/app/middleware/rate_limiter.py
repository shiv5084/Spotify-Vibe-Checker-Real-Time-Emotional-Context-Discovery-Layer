import structlog
from typing import Optional
from fastapi import Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import AuthService
from app.utils.errors import AuthenticationException

logger = structlog.get_logger()

# Security scheme helper
security = HTTPBearer(auto_error=False)
auth_service = AuthService()

def get_client_ip(request: Request) -> str:
    """
    Extract the client's real IP address from headers or connection state.
    """
    # Check X-Forwarded-For header if behind a reverse proxy (e.g. Nginx, Cloudflare)
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs separated by commas; take the first one
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    FastAPI dependency to extract and verify the bearer token, returning the user dict if valid,
    or None if missing/invalid (allows anonymous usage).
    """
    if not credentials:
        logger.info("No credentials provided. Request is anonymous.")
        return None
        
    token = credentials.credentials
    user = auth_service.verify_token(token)
    
    if not user:
        logger.warning("Credentials provided but token verification failed.")
        # If user explicitly sent a token but it's invalid, raise Authentication Error
        raise AuthenticationException("Invalid or expired authentication token.")
        
    return user

def get_required_user(user: Optional[dict] = Depends(get_optional_user)) -> dict:
    """
    FastAPI dependency that requires a verified user token.
    Raises AuthenticationException if not signed in.
    """
    if not user:
        raise AuthenticationException("You must be signed in to perform this action.")
    return user
