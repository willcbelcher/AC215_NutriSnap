from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Meal, Symptom
import os

# 1. Setup the database connection
# Ensure we use localhost if running outside Docker, or the env var if inside
db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/nutrisnap_db")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed():
    print("🌱 Seeding database...")
    
    # 2. Check if the demo user already exists
    existing_user = db.query(User).filter(User.email == "demo@nutrisnap.com").first()
    
    if existing_user:
        print(f"User {existing_user.name} already exists. Skipping user creation.")
        user = existing_user
    else:
        # 3. Create the User
        user = User(
            email="demo@nutrisnap.com",
            name="Demo User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"👤 Created user: {user.name}")

    # 4. Create Sample Meals
    # We check if the user has meals to avoid duplicate seeding
    if not user.meals:
        meals_data = [
            Meal(
                image_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
                identified_foods="Grilled Chicken, Brown Rice, Broccoli",
                protein=45.0,
                carbs=50.0,
                fat=10.5,
                triggers=None, # Safe meal
                user_id=user.id
            ),
            Meal(
                image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591",
                identified_foods="Cheese Pizza, Pepperoni",
                protein=20.0,
                carbs=60.0,
                fat=25.0,
                triggers="Lactose, Gluten", # Trigger meal
                user_id=user.id
            ),
            Meal(
                image_url="https://images.unsplash.com/photo-1488477181946-6428a0291777",
                identified_foods="Greek Yogurt Parfait, Berries",
                protein=15.0,
                carbs=25.0,
                fat=5.0,
                triggers="Lactose", # Mild trigger
                user_id=user.id
            )
        ]
        
        db.add_all(meals_data)
        db.commit()
        print(f"🍱 Added {len(meals_data)} sample meals.")
    else:
        print("🍱 Meals already exist for this user.")

    # 5. Create Sample Symptoms
    if not user.symptoms:
        symptoms_data = [
            Symptom(
                symptom_name="Bloating",
                severity=6,
                notes="Felt bloated after lunch",
                user_id=user.id
            ),
            Symptom(
                symptom_name="Headache",
                severity=4,
                notes="Mild headache in the afternoon",
                user_id=user.id
            )
        ]
        db.add_all(symptoms_data)
        db.commit()
        print(f"🤒 Added {len(symptoms_data)} sample symptoms.")
    else:
        print("🤒 Symptoms already exist for this user.")

    print("✅ Seeding complete!")
    db.close()

if __name__ == "__main__":
    seed()