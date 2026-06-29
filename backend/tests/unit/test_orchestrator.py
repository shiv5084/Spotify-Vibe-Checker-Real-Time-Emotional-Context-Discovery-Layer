from unittest.mock import MagicMock, patch
import pytest
from app.pipeline.orchestrator import PipelineOrchestrator
from app.models.queue import VibeQueue
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType

@patch("app.pipeline.orchestrator.CacheService")
@patch("app.pipeline.orchestrator.GroqClient")
@patch("app.pipeline.orchestrator.QdrantService")
def test_orchestrator_cache_hit(mock_qdrant, mock_groq, mock_cache):
    orchestrator = PipelineOrchestrator()
    
    # Mock Input Processor to return cached data
    mock_input_processor = MagicMock()
    mock_cached_queue = {
        "prompt": "happy",
        "emotion_type": "current_only",
        "confidence": 0.9,
        "tracks": [],
        "queue_size": 0,
        "generated_at": "2026-06-29T12:00:00Z",
        "emotional_profile": {
            "emotion_type": "current_only",
            "current": {
                "primary_emotion": "happy",
                "secondary_emotion": None,
                "energy": 0.8,
                "valence": 0.8,
                "danceability": 0.8,
                "acousticness": 0.1,
                "instrumentalness": 0.0,
                "tempo_range": [110.0, 130.0]
            },
            "desired": None,
            "transition": "maintain",
            "confidence": 0.9
        }
    }
    mock_input_processor.process.return_value = ("happy", mock_cached_queue, None)
    orchestrator.input_processor = mock_input_processor
    
    # Mock Queue Assembler
    orchestrator.queue_assembler = MagicMock()

    result = orchestrator.run("happy", "user_123", is_authenticated=True)

    assert result.prompt == "happy"
    assert result.confidence == 0.9
    mock_input_processor.process.assert_called_once_with(
        prompt="happy",
        identifier="user_123",
        is_authenticated=True
    )
    # Ensure queue assembler was called to log the cache hit
    orchestrator.queue_assembler.assemble.assert_called_once()

@patch("app.pipeline.orchestrator.CacheService")
@patch("app.pipeline.orchestrator.GroqClient")
@patch("app.pipeline.orchestrator.QdrantService")
def test_orchestrator_cache_miss_full_pipeline(mock_qdrant, mock_groq, mock_cache):
    orchestrator = PipelineOrchestrator()

    # Mock Input Processor (no cache hit)
    mock_input_processor = MagicMock()
    mock_input_processor.process.return_value = ("happy", None, None)
    orchestrator.input_processor = mock_input_processor

    # Mock Emotion Extractor
    mock_extractor = MagicMock()
    current_state = StateProfile(
        primary_emotion="happy", energy=0.8, valence=0.8, danceability=0.8,
        acousticness=0.1, instrumentalness=0.0, tempo_range=[110.0, 130.0]
    )
    mock_profile = EmotionalProfile(
        emotion_type=EmotionType.CURRENT_ONLY,
        current=current_state,
        desired=None,
        transition="maintain",
        confidence=0.9
    )
    mock_extractor.extract.return_value = mock_profile
    orchestrator.emotion_extractor = mock_extractor

    # Mock Semantic Retriever
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [MagicMock()] # dummy candidate
    orchestrator.semantic_retriever = mock_retriever

    # Mock Ranking Engine
    mock_ranking = MagicMock()
    mock_ranked_tracks = [MagicMock()] # dummy ranked track
    mock_ranking.rank.return_value = mock_ranked_tracks
    orchestrator.ranking_engine = mock_ranking

    # Mock Queue Assembler
    mock_assembler = MagicMock()
    mock_assembled_queue = VibeQueue(
        prompt="happy",
        emotion_type=EmotionType.CURRENT_ONLY,
        emotional_profile=mock_profile,
        confidence=0.9,
        tracks=[],
        queue_size=0
    )
    mock_assembler.assemble.return_value = mock_assembled_queue
    orchestrator.queue_assembler = mock_assembler

    result = orchestrator.run("happy", "user_123", is_authenticated=True)

    assert result == mock_assembled_queue
    mock_input_processor.process.assert_called_once()
    mock_extractor.extract.assert_called_with("happy")
    mock_retriever.retrieve.assert_called_with(mock_profile)
    mock_ranking.rank.assert_called_once()
    mock_assembler.assemble.assert_called_once()
