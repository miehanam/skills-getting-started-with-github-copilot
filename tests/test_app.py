from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


CHESS_SIGNUP_URL = "/activities/Chess%20Club/signup"


@pytest.fixture
def client():
    original_activities = deepcopy(activities)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()


def test_signup_adds_participant(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(CHESS_SIGNUP_URL, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "new.student@mergington.edu"
    signup_params = {"email": email}

    # Act
    first_response = client.post(CHESS_SIGNUP_URL, params=signup_params)
    duplicate_response = client.post(CHESS_SIGNUP_URL, params=signup_params)
    activities_response = client.get("/activities")

    # Assert
    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert activities_response.json()["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    signup_url = "/activities/Unknown%20Club/signup"

    # Act
    response = client.post(signup_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_signup_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(CHESS_SIGNUP_URL, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_remove_signup_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "not.signed.up@mergington.edu"

    # Act
    response = client.delete(CHESS_SIGNUP_URL, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    signup_url = "/activities/Unknown%20Club/signup"

    # Act
    response = client.delete(signup_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
