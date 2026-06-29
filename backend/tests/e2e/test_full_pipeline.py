import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType

@patch("app.services.cache.CacheService.get_cached_queue")
@patch("app.services.cache.CacheService.check_rate_limit")
@patch("app.services.groq_client.GroqClient.extract_emotional_profile")
@patch("app.services.groq_client.GroqClient.generate_recommendation_explanation")
def test_full_pipeline_api_e2e(
    mock_generate_explanation,
    mock_extract_profile,
    mock_check_limit,
    mock_get_cache
):
    """
    E2E test hitting FastAPI /api/vibe. 
    Mocks only the Groq LLM parsing stage to maintain deterministic profiles,
    while running Fastembed, live Qdrant Search, and Supabase database fetches.
    """
    # Force cache misses and allow rate limits
    mock_get_cache.return_value = None
    mock_check_limit.return_value = (False, 1, 0)

    # Setup mock Groq
    mock_profile_dict = {
        "emotion_type": "current_only",
        "current": {
            "primary_emotion": "energetic",
            "secondary_emotion": None,
            "energy": 0.8,
            "valence": 0.7,
            "danceability": 0.8,
            "acousticness": 0.1,
            "instrumentalness": 0.1,
            "tempo_range": [110, 130]
        },
        "desired": None,
        "transition": "maintain",
        "confidence": 0.98
    }
    mock_extract_profile.return_value = mock_profile_dict
    mock_generate_explanation.return_value = "High energy beats to power your running."

    client = TestClient(app)
    
    # Send post request
    response = client.post("/api/vibe", json={"prompt": "High energy running songs"})
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["prompt"] == "High energy running songs"
    assert data["confidence"] == 0.98
    assert "tracks" in data
    assert len(data["tracks"]) > 0
    assert data["tracks"][0]["track"]["track_name"] is not None
    assert data["ai_explanation"] == "High energy beats to power your running."
