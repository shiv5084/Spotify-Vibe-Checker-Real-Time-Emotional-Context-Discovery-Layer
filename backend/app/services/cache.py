import hashlib
import logging
import re
from typing import Optional
import redis
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.redis_enabled = False
        self._local_cache = {}  # In-memory fallback for local testing if Redis is offline
        self._local_rate_limits = {}  # In-memory rate limiting fallback
        
        try:
            # Parse Redis URL and connect
            if settings.REDIS_URL:
                logger.info(f"Connecting to Redis at URL: {settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL}")
                self.redis_client = redis.Redis.from_url(
                    settings.REDIS_URL, 
                    decode_responses=True,
                    socket_timeout=2.0,
                    socket_connect_timeout=2.0
                )
                # Test connection
                if self.redis_client.ping():
                    self.redis_enabled = True
                    logger.info("Successfully connected to Redis cache.")
                else:
                    logger.warning("Redis ping failed. Falling back to in-memory caching.")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching and rate-limiting will fallback to in-memory.")

    def normalize_prompt(self, prompt: str) -> str:
        """
        Normalize prompt by converting to lowercase, stripping whitespace, 
        and removing non-alphanumeric punctuation for consistent cache hit rates.
        """
        # Convert to lowercase and strip whitespace
        normalized = prompt.strip().lower()
        # Remove punctuation except spaces
        normalized = re.sub(r"[^\w\s]", "", normalized)
        # Collapse multiple spaces into one
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def get_prompt_hash(self, prompt: str) -> str:
        """
        Generate SHA-256 hash for the normalized prompt.
        """
        normalized = self.normalize_prompt(prompt)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get_cached_queue(self, prompt: str) -> Optional[str]:
        """
        Retrieve cached Vibe Queue JSON string. Returns None on cache miss or Redis failure.
        """
        prompt_hash = self.get_prompt_hash(prompt)
        key = f"vibe_cache:{prompt_hash}"
        
        if self.redis_enabled:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.warning(f"Error fetching from Redis cache: {e}")
                
        # In-memory fallback
        return self._local_cache.get(key)

    def set_cached_queue(self, prompt: str, queue_json: str, ttl: int = 86400) -> None:
        """
        Store Vibe Queue JSON string in cache with TTL.
        """
        prompt_hash = self.get_prompt_hash(prompt)
        key = f"vibe_cache:{prompt_hash}"
        
        if self.redis_enabled:
            try:
                self.redis_client.set(key, queue_json, ex=ttl)
                return
            except Exception as e:
                logger.warning(f"Error writing to Redis cache: {e}")
                
        # In-memory fallback
        self._local_cache[key] = queue_json

    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """
        Check rate limit for a given identifier (user_id or IP).
        Returns (is_blocked, current_count, retry_after_seconds)
        """
        key = f"rate_limit:{identifier}"
        
        if self.redis_enabled:
            try:
                pipe = self.redis_client.pipeline()
                pipe.incr(key)
                pipe.ttl(key)
                current_count, ttl = pipe.execute()
                
                # If key is new, set expiration
                if current_count == 1 or ttl < 0:
                    self.redis_client.expire(key, window_seconds)
                    ttl = window_seconds
                    
                is_blocked = current_count > limit
                retry_after = ttl if is_blocked else 0
                return is_blocked, current_count, retry_after
            except Exception as e:
                logger.warning(f"Redis rate limit check error: {e}. Falling back to in-memory.")
                
        # In-memory rate limiting fallback
        import time
        now = time.time()
        
        if key not in self._local_rate_limits:
            self._local_rate_limits[key] = {"count": 1, "expires_at": now + window_seconds}
            return False, 1, 0
            
        data = self._local_rate_limits[key]
        if now > data["expires_at"]:
            # Window expired, reset
            self._local_rate_limits[key] = {"count": 1, "expires_at": now + window_seconds}
            return False, 1, 0
            
        data["count"] += 1
        is_blocked = data["count"] > limit
        retry_after = int(max(0.0, data["expires_at"] - now)) if is_blocked else 0
        return is_blocked, data["count"], retry_after
