from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class EmotionType(str, Enum):
    MIXED_EMOTION = "mixed_emotion"
    CURRENT_WITH_DESIRED = "current_with_desired"
    DESIRED_ONLY = "desired_only"
    CURRENT_ONLY = "current_only"

class StateProfile(BaseModel):
    primary_emotion: str = Field(..., description="Primary identified emotion")
    secondary_emotion: Optional[str] = Field(None, description="Optional secondary identified emotion")
    energy: float = Field(..., ge=0.0, le=1.0, description="Target energy level (0.0-1.0)")
    valence: float = Field(..., ge=0.0, le=1.0, description="Target valence level (0.0-1.0)")
    danceability: float = Field(..., ge=0.0, le=1.0, description="Target danceability level (0.0-1.0)")
    acousticness: float = Field(..., ge=0.0, le=1.0, description="Target acousticness level (0.0-1.0)")
    instrumentalness: float = Field(..., ge=0.0, le=1.0, description="Target instrumentalness level (0.0-1.0)")
    tempo_range: List[float] = Field(default=[60.0, 180.0], description="Target tempo range [min_bpm, max_bpm]")

    @field_validator("tempo_range")
    @classmethod
    def validate_tempo(cls, v: List[float]) -> List[float]:
        if len(v) != 2:
            raise ValueError("tempo_range must contain exactly two values: [min_bpm, max_bpm]")
        if v[0] < 0 or v[1] < 0:
            raise ValueError("tempo values must be positive")
        if v[0] > v[1]:
            raise ValueError("min_bpm must be less than or equal to max_bpm")
        return v

class EmotionalProfile(BaseModel):
    emotion_type: EmotionType = Field(..., description="Pattern type of the prompt emotion")
    current: StateProfile = Field(..., description="Emotional profile of the current state")
    desired: Optional[StateProfile] = Field(None, description="Emotional profile of the desired state, if specified")
    transition: str = Field(default="maintain", description="Transition speed/style ('maintain', 'gradual', 'immediate')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM extraction confidence (0.0-1.0)")

    @field_validator("transition")
    @classmethod
    def validate_transition(cls, v: str) -> str:
        valid_transitions = {"maintain", "gradual", "immediate"}
        if v.lower() not in valid_transitions:
            raise ValueError(f"transition must be one of {valid_transitions}")
        return v.lower()
