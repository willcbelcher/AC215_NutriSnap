from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import models


def test_user_creation(test_db):
    """Test user creation and relationships"""
    # Create a user
    user = models.User(
        email="testuser@example.com",
        name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Verify user was created
    assert user.id is not None
    assert user.email == "testuser@example.com"
    assert user.name == "Test User"

    # Verify relationships exist (should be empty lists)
    assert user.meals == []
    assert user.symptoms == []

    # Create a meal for the user
    meal = models.Meal(
        image_url="https://example.com/test.jpg",
        identified_foods="test food",
        protein=20.0,
        carbs=30.0,
        fat=10.0,
        triggers="None",
        user_id=user.id
    )
    test_db.add(meal)
    test_db.commit()
    test_db.refresh(user)

    # Verify relationship works
    assert len(user.meals) == 1
    assert user.meals[0].identified_foods == "test food"


def test_meal_creation(test_db):
    """Test meal creation with all fields"""
    # Create a user first
    user = models.User(
        email="mealtest@example.com",
        name="Meal Test User"
    )
    test_db.add(user)
    test_db.commit()

    # Create a meal
    meal = models.Meal(
        image_url="https://example.com/ramen.jpg",
        identified_foods="ramen, miso soup, noodles",
        protein=15.5,
        carbs=45.0,
        fat=8.5,
        triggers="Gluten",
        user_id=user.id
    )
    test_db.add(meal)
    test_db.commit()
    test_db.refresh(meal)

    # Verify all fields
    assert meal.id is not None
    assert meal.image_url == "https://example.com/ramen.jpg"
    assert meal.identified_foods == "ramen, miso soup, noodles"
    assert meal.protein == 15.5
    assert meal.carbs == 45.0
    assert meal.fat == 8.5
    assert meal.triggers == "Gluten"
    assert meal.user_id == user.id
    assert meal.created_at is not None

    # Verify relationship
    assert meal.owner.email == "mealtest@example.com"
