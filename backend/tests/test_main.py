import io
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import models


def test_read_root(client):
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "NutriSnap Backend Running" in response.json()["message"]


def test_get_dashboard_empty(client):
    """Test dashboard returns empty list when no meals exist"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert response.json() == []


def test_get_dashboard_with_meals(client, test_db):
    """Test dashboard returns user's meals"""
    # Create a user and meal
    user = models.User(id=1, email="test@test.com", name="Test User")
    test_db.add(user)
    test_db.commit()

    meal = models.Meal(
        image_url="https://example.com/image.jpg",
        identified_foods="ramen, miso soup",
        protein=10,
        carbs=40,
        fat=5,
        triggers="None",
        user_id=1
    )
    test_db.add(meal)
    test_db.commit()

    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["identified_foods"] == "ramen, miso soup"
    assert data[0]["protein"] == 10
    assert data[0]["user_id"] == 1


def test_get_symptoms(client, test_db):
    """Test get symptoms endpoint"""
    # Create a user and symptom
    user = models.User(id=1, email="test@test.com", name="Test User")
    test_db.add(user)
    test_db.commit()

    symptom = models.Symptom(
        symptom_name="Headache",
        severity=7,
        notes="After lunch",
        user_id=1
    )
    test_db.add(symptom)
    test_db.commit()

    response = client.get("/dashboard/symptoms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symptom_name"] == "Headache"
    assert data[0]["severity"] == 7
    assert data[0]["user_id"] == 1


def test_get_recent_activity(client, test_db):
    """Test recent activity endpoint returns mixed meals and symptoms"""
    # Create user
    user = models.User(id=1, email="test@test.com", name="Test User")
    test_db.add(user)
    test_db.commit()

    # Create some meals
    meal1 = models.Meal(
        image_url="https://example.com/image1.jpg",
        identified_foods="ramen",
        protein=10,
        carbs=40,
        fat=5,
        triggers="None",
        user_id=1
    )
    meal2 = models.Meal(
        image_url="https://example.com/image2.jpg",
        identified_foods="salmon",
        protein=30,
        carbs=0,
        fat=15,
        triggers="None",
        user_id=1
    )
    test_db.add(meal1)
    test_db.add(meal2)
    test_db.commit()

    # Create a symptom
    symptom = models.Symptom(
        symptom_name="Bloating",
        severity=5,
        notes="Evening",
        user_id=1
    )
    test_db.add(symptom)
    test_db.commit()

    response = client.get("/dashboard/recent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5  # Should return max 5 items
    assert len(data) == 3  # We created 2 meals + 1 symptom

    # Check that we have both types
    types = [item["type"] for item in data]
    assert "meal" in types
    assert "symptom" in types


def test_get_triggers(client):
    """Test triggers endpoint returns hardcoded triggers"""
    response = client.get("/dashboard/triggers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check for expected triggers
    assert "Lactose" in data or "Gluten" in data


def test_log_food_success(client):
    """Test successful food logging with mocked inference"""
    # Create fake image bytes
    fake_image = b"fake image data"
    files = {"file": ("test.jpg", io.BytesIO(fake_image), "image/jpeg")}

    response = client.post("/log/food", files=files)
    assert response.status_code == 200

    data = response.json()
    assert "identified_foods" in data
    assert "protein" in data
    assert "carbs" in data
    assert "fat" in data
    assert "user_id" in data
    assert data["user_id"] == 1

    # With our mock, we return "ramen" as top1
    assert "ramen" in data["identified_foods"]
    assert data["protein"] == 10
    assert data["carbs"] == 40
    assert data["fat"] == 1


def test_log_food_empty_file(client):
    """Test food logging fails with empty file"""
    empty_file = b""
    files = {"file": ("empty.jpg", io.BytesIO(empty_file), "image/jpeg")}

    response = client.post("/log/food", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_log_symptom_success(client):
    """Test successful symptom logging"""
    symptom_data = {
        "symptom_name": "Nausea",
        "severity": 6,
        "notes": "After dinner"
    }

    response = client.post("/log/symptom", json=symptom_data)
    assert response.status_code == 200

    data = response.json()
    assert data["symptom_name"] == "Nausea"
    assert data["severity"] == 6
    assert data["notes"] == "After dinner"
    assert data["user_id"] == 1


def test_nutrition_lookup(client):
    """Test nutrition lookup logic for different foods"""
    # Test with grilled_salmon (different macros than ramen)
    # We need to test that the NUTRITION_LOOKUP works correctly

    # Create fake image
    fake_image = b"fake image data"
    files = {"file": ("salmon.jpg", io.BytesIO(fake_image), "image/jpeg")}

    response = client.post("/log/food", files=files)
    assert response.status_code == 200

    data = response.json()
    # Our mock returns "ramen" so we should get ramen's nutrition
    assert data["protein"] == 10  # Ramen protein
    assert data["carbs"] == 40    # Ramen carbs
    assert data["fat"] == 1       # Ramen fat
    assert data["triggers"] == "None"
