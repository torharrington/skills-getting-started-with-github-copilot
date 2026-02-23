from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_list_activities_includes_new_entries():
    # ensure activities dict contains expected keys including newly added ones
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Robotics Club" in data
    assert "Photography Club" in data
    assert "Music Band" in data


def test_signup_and_prevent_duplicates():
    # pick an existing activity
    name = "Robotics Club"
    email = "student@example.com"

    # fresh sign up
    response = client.post(f"/activities/{name}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[name]["participants"]

    # GET immediately should show the participant as well (mimics front-end refresh)
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[name]["participants"]

    # duplicate signup should fail
    response = client.post(f"/activities/{name}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity():
    response = client.post("/activities/NotARealClub/signup", params={"email": "x@y.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant():
    name = "Robotics Club"
    email = "tester@school.edu"

    # signup first
    r = client.post(f"/activities/{name}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[name]["participants"]

    # remove participant
    r = client.delete(f"/activities/{name}/signup", params={"email": email})
    assert r.status_code == 200
    assert email not in activities[name]["participants"]

    # removing again should give 404 since not present
    r = client.delete(f"/activities/{name}/signup", params={"email": email})
    assert r.status_code == 404
    assert r.json()["detail"] == "Student not found in activity"
