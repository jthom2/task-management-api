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

@pytest.fixture(scope="module")
def test_project(auth_header):
    response = client.post("/projects/", json={"title": "Test Project"}, headers=auth_header)
    return response.json()

def test_create_task(auth_header, test_project):
    response = client.post(f"/tasks/?project_id={test_project['id']}", json={"title": "Test Task"}, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"

def test_get_tasks(auth_header):
    response = client.get("/tasks/", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
