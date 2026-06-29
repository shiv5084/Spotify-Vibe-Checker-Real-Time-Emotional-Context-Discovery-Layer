import logging
from typing import Optional, Tuple, Dict, Any
import json
from app.services.cache import CacheService

logger = logging.getLogger(__name__)

class InputProcessor:
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service

    def process(
        self, 
        prompt: str, 
        identifier: str, 
        is_authenticated: bool = False
    ) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        """
        Sanitize prompt, validate lengths, check cache, and enforce rate limiting.
        
        Args:
            prompt: Raw user input text.
            identifier: IP address, fingerprint, or user ID for rate limiting.
            is_authenticated: True if the request comes from an authenticated user.
            
        Returns:
            Tuple[sanitized_prompt, cached_queue_dict, block_error_message]
        """
        logger.info(f"Processing input prompt. Identifier: {identifier}, Authenticated: {is_authenticated}")

        # 1. Enforce Rate Limiting
        # Authenticated: 20 requests per hour (3600 seconds)
        # Anonymous: 3 prompts per day (24 hours window in cache/Redis)
        if is_authenticated:
            limit = 20
            window = 3600
            rate_limit_id = f"auth:{identifier}"
            limit_msg = "Rate limit exceeded. Authenticated users are limited to 20 requests per hour."
        else:
            limit = 3
            window = 86400  # 24 hours window for "daily" limit
            rate_limit_id = f"anon:{identifier}"
            limit_msg = "Free trial limit reached (3 prompts per day). Please sign in with Google to continue."

        is_blocked, current_count, retry_after = self.cache_service.check_rate_limit(
            rate_limit_id, 
            limit=limit, 
            window_seconds=window
        )
        
        if is_blocked:
            logger.warning(f"Rate limit hit for {rate_limit_id}. Count: {current_count}")
            return "", None, limit_msg

        # 2. Sanitize and Validate Prompt
        # Remove extra whitespace
        sanitized = prompt.strip()
        if not sanitized:
            return "", None, "Vibe prompt cannot be empty."
            
        if len(sanitized) > 500:
            return "", None, "Vibe prompt must be 500 characters or less."

        # 3. Check Cache
        cached_data = self.cache_service.get_cached_queue(sanitized)
        if cached_data:
            logger.info("Cache hit! Returning cached Vibe Queue.")
            try:
                queue_dict = json.loads(cached_data)
                return sanitized, queue_dict, None
            except Exception as e:
                logger.error(f"Failed to parse cached queue JSON: {e}")

        # Cache miss or parse error: proceed with pipeline
        return sanitized, None, None
