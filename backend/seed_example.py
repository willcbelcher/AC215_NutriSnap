from database import engine, SessionLocal, Base
import models
from datetime import datetime, timedelta


def reset_and_seed_example():
    print("⚠️  Wiping database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 Seeding comprehensive example data...")
        
        # Create User
        user = models.User(email="demo@test.com", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Base time: 5 days ago
        base_time = datetime.now() - timedelta(days=5)
        
        # Data Patterns:
        # Lactose -> Bloating
        # Gluten -> Lethargy
        # Spicy Food -> Heartburn
        
        meals_data = [
            # Day 1
            {"food": "Greek Yogurt Parfait", "triggers": "Lactose", "offset_hours": 8}, # Breakfast
            {"food": "Grilled Chicken Salad", "triggers": "None", "offset_hours": 13}, # Lunch
            {"food": "Pepperoni Pizza", "triggers": "Gluten, Lactose, High Sodium", "offset_hours": 19}, # Dinner
            
            # Day 2
            {"food": "Scrambled Eggs & Avocado", "triggers": "None", "offset_hours": 32}, # Breakfast
            {"food": "Turkey Sandwich on Wheat", "triggers": "Gluten", "offset_hours": 37}, # Lunch
            {"food": "Spicy Beef Tacos", "triggers": "Spicy Food, Gluten", "offset_hours": 43}, # Dinner
            
            # Day 3
            {"food": "Oatmeal with Berries", "triggers": "None", "offset_hours": 56}, # Breakfast
            {"food": "Pasta Carbonara", "triggers": "Gluten, Lactose", "offset_hours": 61}, # Lunch
            {"food": "Chocolate Ice Cream", "triggers": "Lactose, Sugar", "offset_hours": 67}, # Snack
            {"food": "Grilled Salmon with Rice", "triggers": "None", "offset_hours": 70}, # Dinner
            
            # Day 4
            {"food": "Green Smoothie", "triggers": "None", "offset_hours": 80}, # Breakfast
            {"food": "Chicken Curry", "triggers": "Spicy Food", "offset_hours": 85}, # Lunch
            {"food": "Cheeseburger", "triggers": "Gluten, Lactose, Red Meat", "offset_hours": 91}, # Dinner
            
            # Day 5 (Today)
            {"food": "Cereal with Whole Milk", "triggers": "Lactose, Gluten", "offset_hours": 104}, # Breakfast
            {"food": "Sushi Roll", "triggers": "None", "offset_hours": 109}, # Lunch
        ]
        
        symptoms_data = [
            # Day 1
            {"name": "Bloating", "severity": 4, "notes": "Felt bloated immediately after breakfast.", "offset_hours": 9},
            {"name": "Bloating", "severity": 7, "notes": "Stomach feels very tight and uncomfortable.", "offset_hours": 21},
            {"name": "Lethargy", "severity": 6, "notes": "Feeling super tired, hard to keep eyes open.", "offset_hours": 21},
            
            # Day 2
            {"name": "Lethargy", "severity": 5, "notes": "Brain fog hitting hard at work.", "offset_hours": 39},
            {"name": "Heartburn", "severity": 6, "notes": "Burning sensation in chest after tacos.", "offset_hours": 44},
            
            # Day 3
            {"name": "Lethargy", "severity": 7, "notes": "Need a nap right after lunch.", "offset_hours": 63},
            {"name": "Bloating", "severity": 5, "notes": "Stomach rumbling.", "offset_hours": 68},
            
            # Day 4
            {"name": "Heartburn", "severity": 5, "notes": "Mild acid reflux.", "offset_hours": 87},
            {"name": "Bloating", "severity": 6, "notes": "Feeling heavy and bloated.", "offset_hours": 93},
            {"name": "Lethargy", "severity": 4, "notes": "Food coma.", "offset_hours": 93},
            
            # Day 5
            {"name": "Bloating", "severity": 5, "notes": "Gas pain after cereal.", "offset_hours": 105},
        ]
        
        # Insert Meals
        for m in meals_data:
            meal = models.Meal(
                user_id=user.id,
                image_url="https://via.placeholder.com/150",
                identified_foods=m["food"],
                triggers=m["triggers"],
                created_at=base_time + timedelta(hours=m["offset_hours"])
            )
            db.add(meal)
            
        # Insert Symptoms
        for s in symptoms_data:
            symptom = models.Symptom(
                user_id=user.id,
                symptom_name=s["name"],
                severity=s["severity"],
                notes=s["notes"],
                created_at=base_time + timedelta(hours=s["offset_hours"])
            )
            db.add(symptom)
            
        db.commit()
        print("✅ Comprehensive example data seeded!")
        print("Expected Top Triggers: Lactose, Gluten, Spicy Food")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_example()
