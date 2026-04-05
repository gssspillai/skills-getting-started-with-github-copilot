"""Pytest configuration and fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """Reset activities to initial state before each test."""
    # This ensures each test starts with a clean state
    yield
    # Reset participants for activities after each test
    from app import activities
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = []
    activities["Soccer Club"]["participants"] = []
    activities["Art Club"]["participants"] = []
    activities["Drama Club"]["participants"] = []
    activities["Debate Club"]["participants"] = []
    activities["Science Club"]["participants"] = []
    activities["Tennis Club"]["participants"] = []
    activities["Volleyball Team"]["participants"] = []
    activities["Music Club"]["participants"] = []
    activities["Dance Club"]["participants"] = []
    activities["Math Club"]["participants"] = []
    activities["History Club"]["participants"] = []
