import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header(test_user):
    client.post("/users/", json=test_user)
    response = client.post("/auth/token", json={"username": test_user["username"], "password": test_user["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_project(client, auth_header):
    response = client.post(
        "/projects/",
        json={"title": "Test Project", "description": "A test project"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Project"

def test_get_projects(auth_header):
    response = client.get("/projects/", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)