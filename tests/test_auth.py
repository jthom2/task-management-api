import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    return {"username": "testuser", "email": "test@example.com", "password": "testpass"}

def test_create_user(client, test_user):
    response = client.post("/users/", json=test_user.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email

def test_login(test_user):
    response = client.post("/auth/token", json={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
