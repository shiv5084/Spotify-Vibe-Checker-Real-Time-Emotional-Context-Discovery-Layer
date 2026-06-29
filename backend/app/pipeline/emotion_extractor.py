import logging
from typing import Dict, Any
from app.services.groq_client import GroqClient
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType

logger = logging.getLogger(__name__)

class EmotionExtractor:
    def __init__(self, groq_client: GroqClient):
        self.groq_client = groq_client

    def extract(self, prompt: str) -> EmotionalProfile:
        """
        Extract structured emotional profile from the sanitized prompt using Groq API.
        
        Args:
            prompt: Sanitized text prompt.
            
        Returns:
            An EmotionalProfile object.
        """
        logger.info(f"Extracting emotions from prompt: '{prompt}'")
        
        try:
            profile_dict = self.groq_client.extract_emotional_profile(prompt)
            
            # 1. Handle fallback for missing states or structures
            if "current_state" in profile_dict:
                # The LLM outputs "current_state", let's map it to "current" for Pydantic schema compatibility
                profile_dict["current"] = profile_dict.pop("current_state")
            if "desired_state" in profile_dict:
                # Map "desired_state" to "desired"
                profile_dict["desired"] = profile_dict.pop("desired_state")
                
            # If desired state is missing or empty, set it to None
            if not profile_dict.get("desired") or not profile_dict["desired"].get("primary_emotion"):
                profile_dict["desired"] = None

            # 2. Parse into Pydantic model (performing validations)
            profile = EmotionalProfile(**profile_dict)
            
            # 3. Handle very low confidence (e.g. gibberish inputs)
            if profile.confidence <= 0.2:
                logger.warning(f"Extracted emotional profile has critically low confidence: {profile.confidence}")
                # Perform neutral fallback but keep low confidence
                profile = self._get_neutral_fallback(profile.confidence)
                
            return profile
            
        except Exception as e:
            logger.error(f"Error during emotional profile extraction/parsing: {e}")
            # Raise exception so orchestrator can handle retries or hard fail
            raise ValueError(f"Failed to extract valid emotional profile: {e}") from e

    def _get_neutral_fallback(self, confidence: float) -> EmotionalProfile:
        """
        Return a neutral, safe fallback profile for nonsensical prompts.
        """
        neutral_state = StateProfile(
            primary_emotion="neutral",
            secondary_emotion=None,
            energy=0.5,
            valence=0.5,
            danceability=0.5,
            acousticness=0.5,
            instrumentalness=0.2,
            tempo_range=[90.0, 120.0]
        )
        return EmotionalProfile(
            emotion_type=EmotionType.CURRENT_ONLY,
            current=neutral_state,
            desired=None,
            transition="maintain",
            confidence=confidence
        )
