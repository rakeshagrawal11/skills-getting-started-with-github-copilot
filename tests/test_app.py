from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_new_participant():
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_fails_when_already_signed_up():
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Unknown/signup", params={"email": "nobody@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    response = client.delete("/activities/Chess Club/participant", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_unknown_participant_returns_404():
    response = client.delete("/activities/Chess Club/participant", params={"email": "unknown@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_remove_participant_from_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown/participant", params={"email": "nobody@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
