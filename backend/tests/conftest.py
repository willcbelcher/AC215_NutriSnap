import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import database
import models
from main import app

# Use SQLite for tests (fast, in-memory)
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

@pytest.fixture
def test_db():
    """Create a test database for each test"""
    engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
    models.Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db, monkeypatch):
    """Create a test client with mocked inference and database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Mock inference to avoid loading model
    def mock_predict(image_bytes):
        return {
            "top1": [{"label": "ramen", "score": 0.95}],
            "topk": [
                {"label": "ramen", "score": 0.95},
                {"label": "grilled_salmon", "score": 0.03}
            ]
        }

    monkeypatch.setattr("main.run_inference", mock_predict)
    app.dependency_overrides[database.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
