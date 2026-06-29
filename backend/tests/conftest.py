import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth import AuthService
from app.pipeline.orchestrator import PipelineOrchestrator

@pytest.fixture
def client():
    """
    Returns a FastAPI TestClient instance.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_auth_service():
    """
    Mock AuthService verify_token method.
    """
    with patch.object(AuthService, "verify_token") as mock_verify:
        yield mock_verify

@pytest.fixture
def mock_orchestrator():
    """
    Mock PipelineOrchestrator run method.
    """
    with patch.object(PipelineOrchestrator, "run") as mock_run:
        yield mock_run
