from database import SessionLocal
import models

def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding database...")
        
        # Check if the demo user already exists
        # We use the same email as in main.py to avoid duplicates
        existing_user = db.query(models.User).filter(models.User.email == "demo@test.com").first()
        
        if existing_user:
            print(f"User {existing_user.name} already exists. Skipping user creation.")
        else:
            # Create the User
            user = models.User(
                email="demo@test.com",
                name="Demo User"
            )
            db.add(user)
            db.commit()
            print(f"👤 Created user: {user.name}")

        print("✅ Seeding complete!")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()