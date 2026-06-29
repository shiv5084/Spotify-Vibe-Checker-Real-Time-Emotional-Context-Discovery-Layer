import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Extract X-Request-ID from request headers, or generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # 2. Bind request_id to the thread-local/async contextvars context for structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # 3. Process the request
        response = await call_next(request)
        
        # 4. Attach request_id to the response headers
        response.headers["X-Request-ID"] = request_id
        return response
