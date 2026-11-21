"""
Backend test suite for Mergington High School API.
Follows the Arrange-Act-Assert (AAA) pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Save initial state of activities for test isolation
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange fixture: reset the in-memory activities dict before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Arrange fixture: create FastAPI TestClient."""
    return TestClient(app)


# --- Root and Listing Tests ---

def test_root_redirects_to_index(client):
    # Arrange: URL endpoint is "/"

    # Act: Request root endpoint without following redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to "/static/index.html" with status code 307
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange: Known activity in initial database
    expected_activity = "Chess Club"

    # Act: Retrieve list of activities
    response = client.get("/activities")

    # Assert: Response is 200 OK and contains expected activities and structure
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "description" in data[expected_activity]
    assert "schedule" in data[expected_activity]
    assert "max_participants" in data[expected_activity]
    assert "participants" in data[expected_activity]


# --- Signup Tests ---

def test_signup_success(client):
    # Arrange: Valid activity and a new participant email
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act: Submit signup request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert: Returns 200 OK and student is added to participants list
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_fails(client):
    # Arrange: Existing participant in Chess Club
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    assert existing_email in activities[activity_name]["participants"]

    # Act: Attempt to sign up the same participant again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert: Returns 400 Bad Request with descriptive detail message
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity_fails(client):
    # Arrange: Non-existent activity name
    activity_name = "Quidditch Team"
    email = "harry@mergington.edu"

    # Act: Attempt to sign up for nonexistent activity
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Returns 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# --- Unregister Tests ---

def test_unregister_success(client):
    # Arrange: An activity with an existing participant
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    assert existing_email in activities[activity_name]["participants"]

    # Act: Send request to unregister the student
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": existing_email})

    # Assert: Returns 200 OK and student is removed from participants
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_fails(client):
    # Arrange: Participant who is not signed up for Chess Club
    activity_name = "Chess Club"
    not_signed_up_email = "not_here@mergington.edu"
    assert not_signed_up_email not in activities[activity_name]["participants"]

    # Act: Attempt to unregister participant who is not signed up
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": not_signed_up_email})

    # Assert: Returns 400 Bad Request with error detail
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_nonexistent_activity_fails(client):
    # Arrange: Non-existent activity name
    activity_name = "Quidditch Team"
    email = "harry@mergington.edu"

    # Act: Attempt to unregister from nonexistent activity
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Returns 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
