from unittest.mock import MagicMock
from app.models.queue import VibeQueue
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType
from app.models.track import RankedTrack, Track

def create_mock_vibe_queue():
    """Helper to instantiate a dummy VibeQueue object."""
    profile = EmotionalProfile(
        emotion_type=EmotionType.CURRENT_ONLY,
        current=StateProfile(
            primary_emotion="peaceful",
            energy=0.2,
            valence=0.8,
            danceability=0.3,
            acousticness=0.9,
            instrumentalness=0.9,
            tempo_range=[70, 90]
        ),
        desired=None,
        transition="maintain",
        confidence=0.95
    )
    
    tracks = [
        RankedTrack(
            track=Track(
                id="track-id-1",
                track_name="Test Song",
                artist="Artist A",
                album="Album A",
                valence=0.8,
                energy=0.2,
                danceability=0.3,
                tempo=80.0,
                acousticness=0.9,
                instrumentalness=0.9,
                loudness=-10.0,
                speechiness=0.05,
                liveness=0.1,
                mode=1,
                duration_ms=180000,
                popularity=50,
                track_genre="ambient",
                embedding_text="A peaceful ambient song..."
            ),
            similarity_score=0.9,
            alignment_score=0.95,
            diversity_score=1.0,
            arc_score=0.95,
            composite_score=0.92,
            position=1
        )
    ]
    
    return VibeQueue(
        prompt="something peaceful",
        emotion_type=EmotionType.CURRENT_ONLY,
        emotional_profile=profile,
        confidence=0.95,
        tracks=tracks,
        queue_size=len(tracks),
        ai_explanation="This playlist matches your peaceful vibe.",
        generated_at="2026-06-29T12:00:00Z"
    )

def test_vibe_endpoint_success(client, mock_orchestrator):
    """
    Test POST /api/vibe returns successfully with a structured VibeQueue.
    """
    # Setup mock orchestrator response
    mock_orchestrator.return_value = create_mock_vibe_queue()

    payload = {"prompt": "something peaceful"}
    response = client.post("/api/vibe", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "something peaceful"
    assert data["queue_size"] == 1
    assert data["tracks"][0]["track"]["track_name"] == "Test Song"
    assert data["ai_explanation"] == "This playlist matches your peaceful vibe."

def test_vibe_endpoint_validation_error(client):
    """
    Test POST /api/vibe validation constraints (e.g. empty prompt).
    """
    # Empty prompt
    payload = {"prompt": ""}
    response = client.post("/api/vibe", json=payload)
    assert response.status_code == 422
    # Check that FastAPI validation handles empty prompt or custom error handles it
    assert "detail" in response.json() or "error" in response.json()

def test_vibe_endpoint_rate_limit_error(client, mock_orchestrator):
    """
    Test POST /api/vibe handles rate limit exceptions correctly.
    """
    mock_orchestrator.side_effect = ValueError("Free trial limit reached (3 anonymous prompts).")

    payload = {"prompt": "Feeling happy"}
    response = client.post("/api/vibe", json=payload)
    
    assert response.status_code == 429
    data = response.json()
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "trial limit reached" in data["error"]["message"]
