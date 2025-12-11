from database import engine, Base

from seed import seed_data

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Seeding initial data...")
    seed_data()
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()
