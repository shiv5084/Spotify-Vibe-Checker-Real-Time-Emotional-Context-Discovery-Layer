import logging
import time
import uuid
from typing import Optional
from app.services.cache import CacheService
from app.services.groq_client import GroqClient
from app.services.qdrant_client import QdrantService
from app.pipeline.input_processor import InputProcessor
from app.pipeline.emotion_extractor import EmotionExtractor
from app.pipeline.semantic_retriever import SemanticRetriever
from app.pipeline.ranking_engine import RankingEngine
from app.pipeline.queue_assembler import QueueAssembler
from app.models.queue import VibeQueue

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        logger.info("Initializing Pipeline Orchestrator and service dependencies...")
        self.cache_service = CacheService()
        self.groq_client = GroqClient()
        self.qdrant_service = QdrantService()
        
        self.input_processor = InputProcessor(self.cache_service)
        self.emotion_extractor = EmotionExtractor(self.groq_client)
        self.semantic_retriever = SemanticRetriever(self.qdrant_service)
        self.ranking_engine = RankingEngine()
        self.queue_assembler = QueueAssembler(self.cache_service)

    def run(
        self, 
        prompt: str, 
        identifier: str, 
        is_authenticated: bool = False,
        request_id: Optional[str] = None
    ) -> VibeQueue:
        """
        Run the end-to-end AI pipeline to generate a Vibe Queue.
        
        Args:
            prompt: Raw user input text.
            identifier: IP, fingerprint, or user UUID.
            is_authenticated: Boolean if user is signed in.
            request_id: Tracking request UUID. Generated if missing.
            
        Returns:
            VibeQueue object containing recommendation list and profile details.
        """
        if not request_id:
            request_id = str(uuid.uuid4())
            
        logger.info(f"Starting pipeline execution. Request ID: {request_id}, Prompt: '{prompt}'")
        start_time = time.time()

        # Stage 1: Input Processing
        sanitized_prompt, cached_queue_dict, err_msg = self.input_processor.process(
            prompt=prompt,
            identifier=identifier,
            is_authenticated=is_authenticated
        )
        
        if err_msg:
            # Blocked by rate limiting or length requirements
            logger.warning(f"Pipeline blocked at Input Stage: {err_msg}")
            raise ValueError(err_msg)

        # Stage 1.5: Cache Hit Shortcut
        if cached_queue_dict:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Pipeline finished (Cache Hit). Latency: {latency_ms}ms")
            
            # Reconstruct VibeQueue from cached dictionary
            try:
                # Update generated_at and return
                cached_queue = VibeQueue(**cached_queue_dict)
                # Re-log to history in background/assembler if desired (cache hit true)
                self.queue_assembler.assemble(
                    prompt=sanitized_prompt,
                    profile=cached_queue.emotional_profile,
                    ranked_tracks=cached_queue.tracks,
                    latency_ms=latency_ms,
                    request_id=request_id,
                    user_id=identifier if is_authenticated else None,
                    cache_hit=True
                )
                return cached_queue
            except Exception as e:
                logger.error(f"Failed to rebuild VibeQueue from cache: {e}. Re-running full pipeline.")

        # Stage 2: Emotion Extraction (LLM call)
        logger.info("Executing Stage 2: Emotion Extraction...")
        profile = self.emotion_extractor.extract(sanitized_prompt)

        # Stage 3: Semantic Retrieval (Qdrant search + Supabase join)
        logger.info("Executing Stage 3: Semantic Retrieval...")
        candidates = self.semantic_retriever.retrieve(profile)
        
        if not candidates:
            raise ValueError("No matching tracks could be retrieved for your vibe. Try clarifying your mood!")

        # Stage 4: Re-ranking
        logger.info("Executing Stage 4: Re-ranking...")
        # Target default queue size: 12 tracks
        ranked_tracks = self.ranking_engine.rank(candidates, profile, queue_size=12)

        # Stage 5: Final Queue Assembly & Persistence
        logger.info("Executing Stage 5: Queue Assembly...")
        
        # Generate AI explanation using Groq
        logger.info("Generating AI recommendation explanation...")
        profile_desc = (
            f"Vibe: {profile.emotion_type}. Current state: {profile.current.primary_emotion} "
            f"(Valence: {profile.current.valence}, Energy: {profile.current.energy}). "
            f"Desired state: {profile.desired.primary_emotion if profile.desired else 'same'}."
        )
        try:
            ai_explanation = self.groq_client.generate_recommendation_explanation(
                prompt=sanitized_prompt,
                profile_desc=profile_desc,
                tracks=ranked_tracks
            )
        except Exception as expl_err:
            logger.warning(f"Failed to generate recommendation explanation: {expl_err}")
            ai_explanation = "These tracks were selected to match the emotional profile and transition of your prompt."

        latency_ms = int((time.time() - start_time) * 1000)
        
        vibe_queue = self.queue_assembler.assemble(
            prompt=sanitized_prompt,
            profile=profile,
            ranked_tracks=ranked_tracks,
            latency_ms=latency_ms,
            request_id=request_id,
            user_id=identifier if is_authenticated else None,
            cache_hit=False,
            ai_explanation=ai_explanation
        )

        logger.info(f"Pipeline successfully completed! Total Latency: {latency_ms}ms")
        return vibe_queue
