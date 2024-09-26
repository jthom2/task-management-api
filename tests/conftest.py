import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from app import models, schemas, crud
from app.dependencies import get_password_hash
from app.models import User, Project, Task

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass"
    }

@pytest.fixture(scope="module")
def auth_header(client, test_user):
    # Create the user
    response = client.post("/users/", json=test_user.dict())
    assert response.status_code == 200, "User creation failed"

    # Log in to get the access token
    login_data = {
        "username": test_user.username,
        "password": test_user.password
    }
    response = client.post("/auth/token", json=login_data)
    assert response.status_code == 200, "Login failed"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers
