# nutrisnap-backend/main.py
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import models, schemas, database
from typing import List

# Create tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS: Allow Nuxt (port 3000) to talk to FastAPI (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "NutriSnap Backend Running 🚀"}

@app.get("/dashboard", response_model=List[schemas.MealOut])
def get_dashboard(db: Session = Depends(database.get_db)):
    # Hardcoded user_id 1 for prototype
    meals = db.query(models.Meal).filter(models.Meal.user_id == 1).order_by(models.Meal.created_at.desc()).all()
    return meals

@app.post("/log", response_model=schemas.MealOut)
async def log_meal(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # 1. READ IMAGE
    file_bytes = await file.read()
    
    # 2. CALL AI SERVICE (The other container)
    # Ensure your AI container is named 'cv_model' in docker-compose
    try:
        # We send the bytes to the AI service
        response = requests.post(
            "http://cv_model:8001/predict", 
            files={"file": (file.filename, file_bytes, file.content_type)}
        )
        ai_data = response.json()
    except Exception as e:
        print(f"AI Service failed: {e}")
        # Fallback dummy data if AI service is down
        ai_data = {"foods": "Error/Manual", "macros": {"protein":0, "carbs":0, "fat":0}, "triggers": "Unknown"}

    # 3. SAVE TO DB
    # Create dummy user if not exists (Prototype only)
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(email="demo@test.com", name="Demo")
        db.add(user)
        db.commit()

    new_meal = models.Meal(
        image_url="placeholder.jpg",
        identified_foods=ai_data.get("foods"),
        protein=ai_data["macros"]["protein"],
        carbs=ai_data["macros"]["carbs"],
        fat=ai_data["macros"]["fat"],
        triggers=ai_data.get("triggers"),
        user_id=1
    )
    
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    return new_meal