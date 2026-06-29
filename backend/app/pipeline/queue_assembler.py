import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.emotion import EmotionalProfile
from app.models.track import RankedTrack
from app.models.queue import VibeQueue
from app.services.cache import CacheService
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

class QueueAssembler:
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def assemble(
        self,
        prompt: str,
        profile: EmotionalProfile,
        ranked_tracks: List[RankedTrack],
        latency_ms: int,
        request_id: str,
        user_id: Optional[str] = None,
        cache_hit: bool = False,
        ai_explanation: Optional[str] = None
    ) -> VibeQueue:
        """
        Build final VibeQueue object, write to Redis cache, and log into database.
        
        Args:
            prompt: Original user prompt.
            profile: Extracted emotional profile model.
            ranked_tracks: Fully sequenced tracks.
            latency_ms: Calculation time of the pipeline execution in milliseconds.
            request_id: UUID tracking the request.
            user_id: Optional user UUID.
            cache_hit: Boolean indicating if this response came from the cache.
            ai_explanation: Optional AI generated summary explaining the recommendations.
            
        Returns:
            Fully assembled VibeQueue object.
        """
        logger.info(f"Assembling Vibe Queue for prompt '{prompt}' with {len(ranked_tracks)} tracks")

        # 1. Instantiate the VibeQueue model
        vibe_queue = VibeQueue(
            prompt=prompt,
            emotion_type=profile.emotion_type,
            emotional_profile=profile,
            confidence=profile.confidence,
            tracks=ranked_tracks,
            queue_size=len(ranked_tracks),
            ai_explanation=ai_explanation,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )

        # 2. Convert to dictionary / JSON string
        queue_dict = vibe_queue.model_dump()
        queue_json = json.dumps(queue_dict)

        # 3. Write to Redis Cache if this was a fresh generation (cache miss)
        if not cache_hit:
            try:
                # Cache for 24 hours (86400 seconds)
                self.cache_service.set_cached_queue(prompt, queue_json, ttl=86400)
                logger.info("Successfully cached new Vibe Queue in Redis.")
            except Exception as cache_err:
                logger.warning(f"Failed to cache generated queue: {cache_err}")

        # 4. Write to prompt_history and audit_log tables in Supabase
        # Run asynchronously/backgrounded if possible, but standard synchronous writes with try/except are safe.
        try:
            # Insert into prompt_history
            history_data = {
                "user_id": user_id if user_id else None,
                "prompt_text": prompt,
                "emotional_profile": json.loads(profile.model_dump_json()),
                "queue_result": queue_dict,
                "confidence": float(profile.confidence),
                "latency_ms": latency_ms,
                "cache_hit": cache_hit
            }
            self.supabase.table("prompt_history").insert(history_data).execute()
            logger.info("Logged prompt to prompt_history.")
        except Exception as db_err:
            logger.warning(f"Failed to write to prompt_history: {db_err}")

        try:
            # Insert into audit_log
            audit_data = {
                "request_id": request_id,
                "component": "pipeline_orchestrator",
                "action": "generate_queue",
                "input_data": {"prompt": prompt, "user_id": user_id},
                "output_data": {"queue_size": len(ranked_tracks), "confidence": profile.confidence},
                "latency_ms": latency_ms,
                "error": None
            }
            self.supabase.table("audit_log").insert(audit_data).execute()
            logger.info("Logged action to audit_log.")
        except Exception as db_err:
            logger.warning(f"Failed to write to audit_log: {db_err}")

        return vibe_queue
