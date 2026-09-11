import os
from pathlib import Path

# Configure the test environment BEFORE importing the application.
os.environ["DATABASE_URL"] = "sqlite:///./test_leads.db"
os.environ["UPLOAD_DIR"] = "./test_uploads"
os.environ["ADMIN_EMAIL"] = "attorney@example.com"
os.environ["ADMIN_PASSWORD"] = "change-me"
os.environ["JWT_SECRET"] = "test-secret-key-for-local-testing-123456"

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_state():
    """Give every test a clean database and upload directory."""
    get_settings.cache_clear()

    # Reset schema without deleting the SQLite file while
    # SQLAlchemy may still have pooled connections to it.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    upload_dir = Path("./test_uploads")
    upload_dir.mkdir(exist_ok=True)

    for path in upload_dir.iterdir():
        if path.is_file():
            path.unlink()

    yield

    # Clean database contents/schema after the test.
    Base.metadata.drop_all(bind=engine)

    # Close pooled SQLite connections.
    engine.dispose()

    for path in upload_dir.iterdir():
        if path.is_file():
            path.unlink()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "attorney@example.com",
            "password": "change-me",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }