import json
from unittest.mock import MagicMock
import pytest
from app.pipeline.input_processor import InputProcessor
from app.services.cache import CacheService

@pytest.fixture
def mock_cache_service():
    service = MagicMock(spec=CacheService)
    # Default behavior: not blocked, no cache
    service.check_rate_limit.return_value = (False, 1, 0)
    service.get_cached_queue.return_value = None
    return service

def test_input_processor_happy_path(mock_cache_service):
    processor = InputProcessor(mock_cache_service)
    prompt = "Feeling energetic and ready to run!"
    
    sanitized, cached_queue, err = processor.process(prompt, "test-ip", is_authenticated=False)
    
    assert err is None
    assert cached_queue is None
    assert sanitized == "Feeling energetic and ready to run!"
    mock_cache_service.check_rate_limit.assert_called_once_with("anon:test-ip", limit=3, window_seconds=86400)

def test_input_processor_empty_prompt(mock_cache_service):
    processor = InputProcessor(mock_cache_service)
    
    sanitized, cached_queue, err = processor.process("   ", "test-ip", is_authenticated=False)
    
    assert err == "Vibe prompt cannot be empty."
    assert sanitized == ""
    assert cached_queue is None

def test_input_processor_too_long_prompt(mock_cache_service):
    processor = InputProcessor(mock_cache_service)
    long_prompt = "a" * 501
    
    sanitized, cached_queue, err = processor.process(long_prompt, "test-ip", is_authenticated=False)
    
    assert err == "Vibe prompt must be 500 characters or less."
    assert sanitized == ""
    assert cached_queue is None

def test_input_processor_cache_hit(mock_cache_service):
    processor = InputProcessor(mock_cache_service)
    mock_queue = {"prompt": "happy", "queue_size": 12, "tracks": []}
    mock_cache_service.get_cached_queue.return_value = json.dumps(mock_queue)
    
    sanitized, cached_queue, err = processor.process("happy", "test-ip", is_authenticated=False)
    
    assert err is None
    assert cached_queue == mock_queue
    assert sanitized == "happy"
    mock_cache_service.get_cached_queue.assert_called_once_with("happy")

def test_input_processor_rate_limit_exceeded(mock_cache_service):
    processor = InputProcessor(mock_cache_service)
    # Simulate rate limited
    mock_cache_service.check_rate_limit.return_value = (True, 4, 30)
    
    sanitized, cached_queue, err = processor.process("happy", "test-ip", is_authenticated=False)
    
    assert "Free trial limit reached" in err
    assert sanitized == ""
    assert cached_queue is None
