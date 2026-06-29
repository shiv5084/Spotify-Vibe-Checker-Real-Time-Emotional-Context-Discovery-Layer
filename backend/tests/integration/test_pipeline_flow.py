import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.pipeline.orchestrator import PipelineOrchestrator
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType

@pytest.fixture
def mock_external_services():
    """Mocks out Qdrant and Groq networking for integration flow testing."""
    with patch("app.pipeline.orchestrator.GroqClient") as mock_groq_class, \
         patch("app.pipeline.orchestrator.QdrantService") as mock_qdrant_class, \
         patch("app.pipeline.orchestrator.CacheService") as mock_cache_class:
         
        # Mock Cache to always miss and allow rate limits
        mock_cache = MagicMock()
        mock_cache.get_cached_queue.return_value = None
        mock_cache.check_rate_limit.return_value = (False, 1, 0)
        mock_cache_class.return_value = mock_cache
        
        # Mock Groq Client to return a raw dict
        mock_groq = MagicMock()
        mock_profile_dict = {
            "emotion_type": "current_only",
            "current": {
                "primary_emotion": "peaceful",
                "secondary_emotion": None,
                "energy": 0.2,
                "valence": 0.8,
                "danceability": 0.3,
                "acousticness": 0.9,
                "instrumentalness": 0.9,
                "tempo_range": [70, 90]
            },
            "desired": None,
            "transition": "maintain",
            "confidence": 0.95
        }
        mock_groq.extract_emotional_profile.return_value = mock_profile_dict
        mock_groq.generate_recommendation_explanation.return_value = "A peaceful flow of songs."
        mock_groq_class.return_value = mock_groq
        
        # Mock Qdrant points
        mock_qdrant = MagicMock()
        mock_point = MagicMock()
        mock_point.payload = {"track_id": "track_1"}
        mock_point.score = 0.85
        mock_qdrant.search_similar_tracks.return_value = [mock_point]
        mock_qdrant_class.return_value = mock_qdrant
        
        yield mock_groq, mock_qdrant

@patch("app.pipeline.semantic_retriever.create_client")
@patch("app.pipeline.semantic_retriever.TextEmbedding")
@patch("app.pipeline.queue_assembler.create_client")
def test_full_pipeline_orchestration_flow(
    mock_assembler_supabase_class,
    mock_embedding_class,
    mock_retriever_supabase_class,
    mock_external_services
):
    """
    Verifies that a prompt flows end-to-end through all components of the orchestrator.
    """
    mock_groq, mock_qdrant = mock_external_services
    
    # Mock text embeddings to yield a NumPy array
    mock_model = MagicMock()
    mock_model.embed.return_value = iter([np.array([0.1] * 384)])
    mock_embedding_class.return_value = mock_model
    
    # Mock Supabase clients
    mock_supabase = MagicMock()
    mock_supabase_response = MagicMock()
    mock_supabase_response.data = [
        {
            "id": "track_1",
            "track_name": "Ambient Peace",
            "artist": "Relaxer",
            "album": "Calm Skies",
            "valence": 0.8,
            "energy": 0.2,
            "danceability": 0.3,
            "tempo": 80.0,
            "acousticness": 0.9,
            "instrumentalness": 0.9,
            "loudness": -12.0,
            "speechiness": 0.04,
            "liveness": 0.1,
            "mode": 1,
            "duration_ms": 180000,
            "popularity": 45,
            "track_genre": "ambient",
            "embedding_text": "calming soundscape"
        }
    ]
    mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_supabase_response
    mock_retriever_supabase_class.return_value = mock_supabase
    mock_assembler_supabase_class.return_value = mock_supabase

    orchestrator = PipelineOrchestrator()
    vibe_queue = orchestrator.run("peaceful night", "user_1", is_authenticated=True)
    
    assert vibe_queue.prompt == "peaceful night"
    assert vibe_queue.queue_size == 1
    assert vibe_queue.tracks[0].track.track_name == "Ambient Peace"
    assert vibe_queue.ai_explanation == "A peaceful flow of songs."
