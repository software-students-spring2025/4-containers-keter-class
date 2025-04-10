"""
Conftest
"""
from unittest.mock import MagicMock, patch
from google.cloud import vision # pylint: disable=no-name-in-module
import pytest

@pytest.fixture(autouse=True)
def mock_google_auth(monkeypatch):
    """Mock Google Cloud authentication for all tests"""
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "mock_secrets.json")

    mock_client = MagicMock()
    monkeypatch.setattr("google.cloud.vision.ImageAnnotatorClient", lambda: mock_client)

    return mock_client
