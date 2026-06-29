from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from app.models.emotion import EmotionType, EmotionalProfile
from app.models.track import RankedTrack

from typing import List, Optional

class VibeQueue(BaseModel):
    prompt: str = Field(..., description="Original user prompt")
    emotion_type: EmotionType = Field(..., description="Extracted emotion pattern type")
    emotional_profile: EmotionalProfile = Field(..., description="Full structured emotional profile details")
    confidence: float = Field(..., description="LLM extraction confidence")
    tracks: List[RankedTrack] = Field(..., description="Ordered list of recommended tracks")
    queue_size: int = Field(..., description="Total number of tracks in the queue")
    ai_explanation: Optional[str] = Field(None, description="Short AI-generated explanation of why these songs were recommended")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Timestamp when queue was generated")
