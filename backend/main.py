# nutrisnap-backend/main.py
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import models, schemas, database
from typing import List, Union
from sqlalchemy import desc
from inference import predict as run_inference

NUTRITION_LOOKUP = {
    "ramen": {"macros": {"protein": 10, "carbs": 40, "fat": 1}, "triggers": "None"},
    "grilled_salmon": {"macros": {"protein": 34, "carbs": 0, "fat": 14}, "triggers": "None"},
    "cheeseburger": {"macros": {"protein": 28, "carbs": 33, "fat": 32}, "triggers": "Gluten, Lactose"},
    "oatmeal": {"macros": {"protein": 6, "carbs": 27, "fat": 3}, "triggers": "None"},
    "spaghetti_bolognese": {"macros": {"protein": 22, "carbs": 63, "fat": 17}, "triggers": "Gluten"},
}

DEFAULT_MACROS = {"protein": 0, "carbs": 0, "fat": 0}

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

@app.get("/dashboard/symptoms", response_model=List[schemas.SymptomOut])
def get_symptoms(db: Session = Depends(database.get_db)):
    symptoms = db.query(models.Symptom).filter(models.Symptom.user_id == 1).order_by(models.Symptom.created_at.desc()).all()
    return symptoms

@app.get("/dashboard/recent")
def get_recent_activity(db: Session = Depends(database.get_db)):
    # Get recent meals and symptoms, combine and sort
    meals = db.query(models.Meal).filter(models.Meal.user_id == 1).order_by(models.Meal.created_at.desc()).limit(5).all()
    symptoms = db.query(models.Symptom).filter(models.Symptom.user_id == 1).order_by(models.Symptom.created_at.desc()).limit(5).all()
    
    # Combine and sort by created_at
    activity = []
    for m in meals:
        activity.append({
            "type": "meal",
            "data": m,
            "date": m.created_at
        })
    for s in symptoms:
        activity.append({
            "type": "symptom",
            "data": s,
            "date": s.created_at
        })
    
    # Sort descending
    activity.sort(key=lambda x: x["date"], reverse=True)
    return activity[:5] # Return top 5 mixed

@app.get("/dashboard/triggers")
def get_triggers(db: Session = Depends(database.get_db)):
    # Simple mock analysis for prototype
    # In a real app, this would correlate meals with symptoms
    return ["Lactose", "Gluten", "Spicy Food"]

@app.post("/log/food", response_model=schemas.MealOut)
async def log_food(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        predictions = run_inference(image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    if not predictions.get("top1"):
        raise HTTPException(status_code=500, detail="Model returned no predictions.")

    top_label = predictions["top1"][0]["label"]
    label_key = top_label.replace(" ", "_").lower()
    nutrition = NUTRITION_LOOKUP.get(label_key, {})
    macros = nutrition.get("macros", DEFAULT_MACROS)
    triggers = nutrition.get("triggers")
    identified_foods = ", ".join([pred["label"] for pred in predictions.get("topk", [])]) or top_label

    # Ensure user exists
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(email="demo@test.com", name="Demo")
        db.add(user)
        db.commit()

    new_meal = models.Meal(
        image_url="https://via.placeholder.com/150?text=Food", # Placeholder since we aren't storing the file
        identified_foods=identified_foods,
        protein=macros["protein"],
        carbs=macros["carbs"],
        fat=macros["fat"],
        triggers=triggers,
        user_id=1
    )
    
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    return new_meal

@app.post("/log/symptom", response_model=schemas.SymptomOut)
def log_symptom(symptom: schemas.SymptomCreate, db: Session = Depends(database.get_db)):
    # Ensure user exists
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(email="demo@test.com", name="Demo")
        db.add(user)
        db.commit()
        
    new_symptom = models.Symptom(
        symptom_name=symptom.symptom_name,
        severity=symptom.severity,
        notes=symptom.notes,
        user_id=1 # Hardcoded for prototype
    )
    
    db.add(new_symptom)
    db.commit()
    db.refresh(new_symptom)
    
    return new_symptom
