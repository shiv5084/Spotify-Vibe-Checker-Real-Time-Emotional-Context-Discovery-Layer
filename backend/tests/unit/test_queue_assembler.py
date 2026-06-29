from unittest.mock import MagicMock, patch
import pytest
from app.pipeline.queue_assembler import QueueAssembler
from app.services.cache import CacheService
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType
from app.models.track import RankedTrack, Track

@pytest.fixture
def mock_cache_service():
    return MagicMock(spec=CacheService)

@patch("app.pipeline.queue_assembler.create_client")
def test_queue_assembler_assemble(mock_create_client, mock_cache_service):
    # Setup mock Supabase client
    mock_supabase_instance = MagicMock()
    mock_create_client.return_value = mock_supabase_instance

    # Initialize assembler
    assembler = QueueAssembler(mock_cache_service)

    # Setup dummy inputs
    current_state = StateProfile(
        primary_emotion="chill", energy=0.4, valence=0.5, danceability=0.5,
        acousticness=0.5, instrumentalness=0.1, tempo_range=[90.0, 110.0]
    )
    profile = EmotionalProfile(
        emotion_type=EmotionType.CURRENT_ONLY,
        current=current_state,
        desired=None,
        transition="maintain",
        confidence=0.8
    )

    track = Track(
        id="t1", track_name="Chill Track", artist="Chill Artist",
        valence=0.5, energy=0.4, danceability=0.5, tempo=100.0,
        acousticness=0.5, instrumentalness=0.1, loudness=-6.0,
        mode=1, duration_ms=200000, popularity=50
    )
    
    ranked_tracks = [
        RankedTrack(
            track=track,
            similarity_score=0.8,
            alignment_score=0.9,
            diversity_score=1.0,
            arc_score=0.9,
            composite_score=0.85,
            position=1
        )
    ]

    vibe_queue = assembler.assemble(
        prompt="something chill",
        profile=profile,
        ranked_tracks=ranked_tracks,
        latency_ms=120,
        request_id="req_123",
        user_id="user_abc",
        cache_hit=False
    )

    # Assert model mapping
    assert vibe_queue.prompt == "something chill"
    assert vibe_queue.queue_size == 1
    assert vibe_queue.tracks[0].track.track_name == "Chill Track"

    # Assert Redis cache write was called
    mock_cache_service.set_cached_queue.assert_called_once()
    
    # Assert Supabase logger was called
    insert_call_args = mock_supabase_instance.table.return_value.insert.call_args_list
    assert len(insert_call_args) >= 1
    
    # Extract the dictionary passed to the first insert call (for prompt_history)
    history_data_passed = insert_call_args[0][0][0]
    assert history_data_passed["user_id"] == "user_abc"
    assert history_data_passed["prompt_text"] == "something chill"
    assert history_data_passed["confidence"] == 0.8
    assert history_data_passed["latency_ms"] == 120
    assert history_data_passed["cache_hit"] is False

