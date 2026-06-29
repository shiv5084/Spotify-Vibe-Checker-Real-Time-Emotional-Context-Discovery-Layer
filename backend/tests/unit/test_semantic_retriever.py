from unittest.mock import MagicMock, patch
import pytest
from app.pipeline.semantic_retriever import SemanticRetriever
from app.services.qdrant_client import QdrantService
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType

@pytest.fixture
def mock_qdrant_service():
    service = MagicMock(spec=QdrantService)
    service.collection_name = "spotify_tracks"
    return service

@patch("app.pipeline.semantic_retriever.TextEmbedding")
@patch("app.pipeline.semantic_retriever.create_client")
def test_semantic_retriever_retrieve(mock_create_client, mock_text_embedding_class, mock_qdrant_service):
    import numpy as np
    # Setup mock embedding model
    mock_model_instance = MagicMock()
    mock_model_instance.embed.return_value = iter([np.array([0.1] * 384)])
    mock_text_embedding_class.return_value = mock_model_instance

    # Setup mock Supabase client
    mock_supabase_instance = MagicMock()
    mock_supabase_response = MagicMock()
    mock_supabase_response.data = [
        {
            "id": "track_1",
            "track_name": "Test Track 1",
            "artist": "Test Artist 1",
            "album": "Test Album 1",
            "valence": 0.5,
            "energy": 0.5,
            "danceability": 0.5,
            "tempo": 120.0,
            "acousticness": 0.5,
            "instrumentalness": 0.0,
            "loudness": -6.0,
            "speechiness": 0.05,
            "liveness": 0.1,
            "mode": 1,
            "duration_ms": 200000,
            "popularity": 80,
            "track_genre": "pop",
            "embedding_text": "sample"
        }
    ]
    mock_supabase_instance.table.return_value.select.return_value.in_.return_value.execute.return_value = mock_supabase_response
    mock_create_client.return_value = mock_supabase_instance

    # Setup mock Qdrant points
    mock_point = MagicMock()
    mock_point.payload = {"track_id": "track_1"}
    mock_point.score = 0.85
    mock_qdrant_service.search_similar_tracks.return_value = [mock_point]

    # Initialize retriever
    retriever = SemanticRetriever(mock_qdrant_service)

    # Test inputs
    current_state = StateProfile(
        primary_emotion="happy",
        secondary_emotion=None,
        energy=0.8,
        valence=0.8,
        danceability=0.8,
        acousticness=0.1,
        instrumentalness=0.0,
        tempo_range=[110.0, 130.0]
    )
    profile = EmotionalProfile(
        emotion_type=EmotionType.CURRENT_ONLY,
        current=current_state,
        desired=None,
        transition="maintain",
        confidence=0.9
    )

    candidates = retriever.retrieve(profile)

    assert len(candidates) == 1
    assert candidates[0].track.id == "track_1"
    assert candidates[0].similarity_score == 0.85
    assert candidates[0].track.track_name == "Test Track 1"
    
    # Verify calls
    mock_qdrant_service.search_similar_tracks.assert_called_once()
    mock_supabase_instance.table.assert_called_with("tracks")
