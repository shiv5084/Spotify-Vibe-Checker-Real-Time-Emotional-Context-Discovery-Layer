from typing import Optional
from pydantic import BaseModel, Field

class Track(BaseModel):
    id: str = Field(..., description="Spotify track ID")
    track_name: str = Field(..., description="Name of the track")
    artist: str = Field(..., description="Artist of the track")
    album: Optional[str] = Field(None, description="Album name")
    valence: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    danceability: float = Field(..., ge=0.0, le=1.0)
    tempo: float = Field(..., description="Tempo in BPM")
    acousticness: float = Field(..., ge=0.0, le=1.0)
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    loudness: float = Field(..., description="Loudness in dB")
    speechiness: float = Field(0.0, ge=0.0, le=1.0)
    liveness: float = Field(0.0, ge=0.0, le=1.0)
    mode: int = Field(..., description="0 for minor, 1 for major")
    duration_ms: int = Field(..., description="Duration of track in milliseconds")
    popularity: int = Field(..., ge=0, le=100, description="Track popularity score")
    track_genre: Optional[str] = Field(None, description="Genre of the track")
    embedding_text: Optional[str] = Field(None, description="Generated description used for embedding")

class CandidateTrack(BaseModel):
    track: Track
    similarity_score: float = Field(..., description="Cosine similarity score from vector DB")

class RankedTrack(BaseModel):
    track: Track
    similarity_score: float = Field(..., description="Semantic search similarity score")
    alignment_score: float = Field(..., description="Audio feature emotional alignment score")
    diversity_score: float = Field(..., description="Diversity penalty/bonus score")
    arc_score: float = Field(..., description="Positional emotional arc alignment score")
    composite_score: float = Field(..., description="Calculated composite rank score")
    position: int = Field(..., description="Position in the assembled queue")
