"""Tests for High School Activities API."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 15
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_initial_participants_loaded(self, client):
        """Test that initial participants are loaded correctly."""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Basketball Team"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student1@mergington.edu" in data["message"]

    def test_signup_updates_participants_list(self, client, reset_activities):
        """Test that signup adds participant to activity."""
        # Signup
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "student2@mergington.edu" in data["Soccer Club"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signup is prevented."""
        # First signup
        client.post(
            "/activities/Art Club/signup",
            params={"email": "student3@mergington.edu"}
        )
        
        # Duplicate signup
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": "student3@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_already_existing_participant(self, client):
        """Test that existing participants cannot sign up again."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity."""
        # First signup
        client.post(
            "/activities/Drama Club/signup",
            params={"email": "student4@mergington.edu"}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Drama Club/unregister",
            params={"email": "student4@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity."""
        # Signup
        client.post(
            "/activities/Music Club/signup",
            params={"email": "student5@mergington.edu"}
        )
        
        # Unregister
        client.delete(
            "/activities/Music Club/unregister",
            params={"email": "student5@mergington.edu"}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "student5@mergington.edu" not in data["Music Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister when student is not signed up."""
        response = client.delete(
            "/activities/Science Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_already_existing_participant(self, client):
        """Test unregister of existing participant."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for workflow scenarios."""

    def test_complete_signup_flow(self, client, reset_activities):
        """Test complete workflow: view activities, signup, and unregister."""
        # Get activities
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        initial_count = len(activities["Debate Club"]["participants"])
        
        # Signup
        response = client.post(
            "/activities/Debate Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()["Debate Club"]["participants"]) == initial_count + 1
        
        # Unregister
        response = client.delete(
            "/activities/Debate Club/unregister",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()["Debate Club"]["participants"]) == initial_count

    def test_multiple_participants_per_activity(self, client, reset_activities):
        """Test that multiple participants can signup for same activity."""
        emails = [f"student{i}@mergington.edu" for i in range(1, 4)]
        
        for email in emails:
            response = client.post(
                "/activities/Tennis Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        for email in emails:
            assert email in participants
