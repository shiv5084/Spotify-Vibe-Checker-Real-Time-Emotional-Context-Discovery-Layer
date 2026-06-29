from unittest.mock import MagicMock
import pytest
from app.pipeline.emotion_extractor import EmotionExtractor
from app.services.groq_client import GroqClient
from app.models.emotion import EmotionType

@pytest.fixture
def mock_groq_client():
    return MagicMock(spec=GroqClient)

def test_emotion_extractor_happy_path(mock_groq_client):
    extractor = EmotionExtractor(mock_groq_client)
    mock_groq_client.extract_emotional_profile.return_value = {
        "emotion_type": "current_with_desired",
        "current_state": {
            "primary_emotion": "sad",
            "secondary_emotion": "lonely",
            "energy": 0.2,
            "valence": 0.15,
            "danceability": 0.2,
            "acousticness": 0.8,
            "instrumentalness": 0.1,
            "tempo_range": [60.0, 90.0]
        },
        "desired_state": {
            "primary_emotion": "cheerful",
            "secondary_emotion": None,
            "energy": 0.7,
            "valence": 0.8,
            "danceability": 0.7,
            "acousticness": 0.2,
            "instrumentalness": 0.1,
            "tempo_range": [110.0, 140.0]
        },
        "transition": "gradual",
        "confidence": 0.9
    }

    profile = extractor.extract("feeling low, want to feel better")

    assert profile.emotion_type == EmotionType.CURRENT_WITH_DESIRED
    assert profile.current.primary_emotion == "sad"
    assert profile.desired.primary_emotion == "cheerful"
    assert profile.transition == "gradual"
    assert profile.confidence == 0.9

def test_emotion_extractor_low_confidence_fallback(mock_groq_client):
    extractor = EmotionExtractor(mock_groq_client)
    # Simulate gibberish extraction returning low confidence
    mock_groq_client.extract_emotional_profile.return_value = {
        "emotion_type": "current_only",
        "current_state": {
            "primary_emotion": "unknown",
            "secondary_emotion": None,
            "energy": 0.1,
            "valence": 0.1,
            "danceability": 0.1,
            "acousticness": 0.1,
            "instrumentalness": 0.1,
            "tempo_range": [80.0, 80.0]
        },
        "transition": "maintain",
        "confidence": 0.15
    }

    profile = extractor.extract("asdfghjkl")

    # Should trigger the neutral fallback
    assert profile.current.primary_emotion == "neutral"
    assert profile.current.valence == 0.5
    assert profile.current.energy == 0.5
    assert profile.confidence == 0.15

def test_emotion_extractor_invalid_response_raises(mock_groq_client):
    extractor = EmotionExtractor(mock_groq_client)
    # Return malformed structure
    mock_groq_client.extract_emotional_profile.return_value = {
        "bad_key": "bad_value"
    }

    with pytest.raises(ValueError, match="Failed to extract valid emotional profile"):
        extractor.extract("error prompt")
