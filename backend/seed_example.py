from database import engine, SessionLocal, Base
import models
from datetime import datetime, timedelta

def reset_and_seed_example():
    print("⚠️  Wiping database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 Seeding example data...")
        
        # Create User
        user = models.User(email="demo@test.com", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Base time: 3 days ago
        base_time = datetime.now() - timedelta(days=3)
        
        # Data Patterns:
        # Lactose -> Bloating
        # Gluten -> Lethargy
        
        meals_data = [
            # Day 1
            {"food": "Grilled Chicken Salad", "triggers": "None", "offset_hours": 0}, # Lunch
            {"food": "Cheese Pizza", "triggers": "Lactose, Gluten", "offset_hours": 6}, # Dinner
            
            # Day 2
            {"food": "Oatmeal With Berries", "triggers": "None", "offset_hours": 24}, # Breakfast
            {"food": "Turkey Sandwich", "triggers": "Gluten", "offset_hours": 29}, # Lunch
            {"food": "Ice Cream", "triggers": "Lactose, Sugar", "offset_hours": 34}, # Snack
            
            # Day 3
            {"food": "Greek Yogurt", "triggers": "Lactose", "offset_hours": 48}, # Breakfast
            {"food": "Pasta Carbonara", "triggers": "Gluten, Lactose", "offset_hours": 54}, # Dinner
        ]
        
        symptoms_data = [
            # Day 1: Bloating after Pizza
            {"name": "Bloating", "severity": 7, "offset_hours": 8}, # 2 hours after Pizza
            
            # Day 2: Lethargy after Sandwich
            {"name": "Lethargy", "severity": 5, "offset_hours": 31}, # 2 hours after Sandwich
            
            # Day 2: Bloating after Ice Cream
            {"name": "Bloating", "severity": 6, "offset_hours": 35}, # 1 hour after Ice Cream
            
            # Day 3: Bloating after Yogurt
            {"name": "Bloating", "severity": 4, "offset_hours": 49}, # 1 hour after Yogurt
            
            # Day 3: Lethargy/Bloating after Pasta
            {"name": "Bloating", "severity": 8, "offset_hours": 56}, # 2 hours after Pasta
            {"name": "Lethargy", "severity": 6, "offset_hours": 56},
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
                notes="Generated example data",
                created_at=base_time + timedelta(hours=s["offset_hours"])
            )
            db.add(symptom)
            
        db.commit()
        print("✅ Example data seeded! Triggers 'Lactose' and 'Gluten' should be prominent.")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_example()
