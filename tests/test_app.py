from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_list_activities_includes_new_entries():
    # Arrange
    # (no special setup needed beyond the default activities dict)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Robotics Club" in data
    assert "Photography Club" in data
    assert "Music Band" in data


def test_signup_and_prevent_duplicates():
    # Arrange
    name = "Robotics Club"
    email = "student@example.com"

    # Act – first signup
    response = client.post(f"/activities/{name}/signup", params={"email": email})

    # Assert – signup succeeded and state updated
    assert response.status_code == 200
    assert email in activities[name]["participants"]

    # Act – fetch activities to mimic front‑end refresh
    resp2 = client.get("/activities")

    # Assert – the new participant is returned in the list
    assert resp2.status_code == 200
    assert email in resp2.json()[name]["participants"]

    # Act – attempt duplicate signup
    duplicate = client.post(f"/activities/{name}/signup", params={"email": email})

    # Assert – duplicate is rejected with proper error
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity():
    # Arrange
    bogus_name = "NotARealClub"
    bogus_email = "x@y.com"

    # Act
    response = client.post(f"/activities/{bogus_name}/signup", params={"email": bogus_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant():
    # Arrange
    name = "Robotics Club"
    email = "tester@school.edu"

    # Act – sign up the participant first
    r = client.post(f"/activities/{name}/signup", params={"email": email})

    # Assert – signup worked
    assert r.status_code == 200
    assert email in activities[name]["participants"]

    # Act – remove the participant
    r = client.delete(f"/activities/{name}/signup", params={"email": email})

    # Assert – removal succeeded and participant gone
    assert r.status_code == 200
    assert email not in activities[name]["participants"]

    # Act – attempt to remove again
    r = client.delete(f"/activities/{name}/signup", params={"email": email})

    # Assert – now returns not‑found error
    assert r.status_code == 404
    assert r.json()["detail"] == "Student not found in activity"

# ---------------------------------------------------------------------------
# Additional tests
# ---------------------------------------------------------------------------
# You can add new test functions below using the AAA (Arrange‑Act‑Assert)
# pattern. Here's a simple template to get you started:
#
# def test_example_feature():
#     # Arrange – set up any required variables or state
#     ...
#
#     # Act – perform the action you're testing (e.g. HTTP call)
#     ...
#
#     # Assert – check the response or side effects
#     assert ...
#
# Replace `test_example_feature` and the ellipses with your own logic.
