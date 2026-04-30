"""
Pytest tests for the FastAPI app using the AAA (Arrange-Act-Assert) pattern.
Tests include GET activities, signup, duplicate signup, delete participant, and delete nonexistent participant.
"""

import copy
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


# Store the original activities state to reset between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities module state before each test."""
    # Arrange: Restore original state
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Test GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange - no setup needed, activities are pre-populated
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_returns_error(self, client):
        """Test that signing up with an email already in the activity returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_to_nonexistent_activity_returns_error(self, client):
        """Test that signing up for a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestDeleteParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint."""

    def test_delete_participant_successful(self, client):
        """Test successful removal of a participant from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_delete_nonexistent_participant_returns_error(self, client):
        """Test that removing a participant not in the activity returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "nobody@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_delete_from_nonexistent_activity_returns_error(self, client):
        """Test that deleting from a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]