from typing import Optional

class VibeException(Exception):
    """Base exception class for all Vibe-Checker errors."""
    def __init__(self, code: str, message: str, suggestion: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion
        self.status_code = status_code

class RateLimitException(VibeException):
    """Exception raised when a user exceeds their trial or hourly rate limits."""
    def __init__(self, message: str, suggestion: str = "Please sign in with Google or wait before trying again."):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            suggestion=suggestion,
            status_code=429
        )

class AuthenticationException(VibeException):
    """Exception raised when user authentication fails or token is missing/expired."""
    def __init__(self, message: str = "Authentication failed.", suggestion: str = "Please log in again via Google OAuth."):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=message,
            suggestion=suggestion,
            status_code=401
        )

class ValidationException(VibeException):
    """Exception raised when user input validation fails (e.g. empty or too long prompt)."""
    def __init__(self, message: str, suggestion: str = "Try submitting a short description of your mood, like 'melancholy but hopeful'."):
        super().__init__(
            code="VALIDATION_FAILED",
            message=message,
            suggestion=suggestion,
            status_code=422
        )

class PipelineException(VibeException):
    """Exception raised when execution of the AI pipeline fails."""
    def __init__(self, message: str = "An error occurred while generating your vibe queue.", suggestion: str = "Please check your input or try again in a few moments."):
        super().__init__(
            code="PIPELINE_ERROR",
            message=message,
            suggestion=suggestion,
            status_code=500
        )
