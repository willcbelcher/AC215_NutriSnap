# nutrisnap-backend/main.py
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
import database
from typing import List
from inference import predict as run_inference
import os
import httpx
import gemini_utils
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")

# Simple nutrition lookup for prototype
NUTRITION_LOOKUP = {
    "ramen": {"protein": 10.0, "carbs": 40.0, "fat": 15.0},
    "grilled salmon": {"protein": 30.0, "carbs": 0.0, "fat": 15.0},
    "caesar salad": {"protein": 7.0, "carbs": 10.0, "fat": 12.0},
    "pizza": {"protein": 12.0, "carbs": 30.0, "fat": 10.0},
    "burger": {"protein": 25.0, "carbs": 35.0, "fat": 20.0},
    "sushi": {"protein": 15.0, "carbs": 45.0, "fat": 5.0},
    "pasta": {"protein": 12.0, "carbs": 60.0, "fat": 8.0},
    "steak": {"protein": 40.0, "carbs": 0.0, "fat": 25.0},
    "chicken breast": {"protein": 30.0, "carbs": 0.0, "fat": 3.0},
    "rice": {"protein": 4.0, "carbs": 45.0, "fat": 0.5},
}


# Create tables on startup (skip during tests - conftest.py handles this)
if os.getenv("TESTING") != "1":
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
    user_id = 1 # Hardcoded for prototype
    
    # 1. Get all symptoms
    symptoms = db.query(models.Symptom).filter(models.Symptom.user_id == user_id).all()
    
    # Require at least a few symptoms to make a guess
    if len(symptoms) < 3:
        return []
        
    trigger_counts = {}
    
    for symptom in symptoms:
        # Find meals eaten within 6 hours BEFORE the symptom
        window_start = symptom.created_at - timedelta(hours=6)
        
        meals = db.query(models.Meal).filter(
            models.Meal.user_id == user_id,
            models.Meal.created_at >= window_start,
            models.Meal.created_at <= symptom.created_at
        ).all()
        
        for meal in meals:
            if meal.triggers and meal.triggers != "None":
                # Split by comma and clean up
                parts = [t.strip() for t in meal.triggers.split(",")]
                for part in parts:
                    if part and part.lower() != "none":
                        trigger_counts[part] = trigger_counts.get(part, 0) + 1
                        
    # Sort by frequency
    sorted_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top 3 most frequent triggers
    return [t[0] for t in sorted_triggers[:3]]

@app.post("/log/food", response_model=schemas.MealOut)
async def log_food(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Resize image to reduce payload size (Vertex AI limit ~1.5MB)
    from PIL import Image
    import io
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB (handle PNG/RGBA)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize to max 512x512 (ViT usually takes 224x224, but 512 is safe for quality)
        image.thumbnail((512, 512))
        
        # Save to buffer as JPEG
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        resized_bytes = buffered.getvalue()
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        # Fallback to original if resize fails (unlikely)
        resized_bytes = image_bytes

    # Vertex AI Configuration
    vertex_endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
    vertex_project_id = os.getenv("VERTEX_PROJECT_ID")
    vertex_region = os.getenv("VERTEX_REGION", "us-central1")

    predictions = {}
    if vertex_endpoint_id:
        try:
            # Get credentials
            import google.auth
            from google.auth.transport.requests import Request as GoogleRequest
            
            credentials, _ = google.auth.default()
            credentials.refresh(GoogleRequest())
            token = credentials.token
            
            # Encode image
            import base64
            encoded_image = base64.b64encode(resized_bytes).decode("utf-8")
            
            # Prepare request
            # The endpoint_id might be the full resource name or just the ID. 
            # If it's the full path, we can extract the ID or use it directly if the URL construction handles it.
            # The user provided full path: projects/.../endpoints/...
            # API expects: https://{REGION}-aiplatform.googleapis.com/v1/{ENDPOINT}:predict
            
            # If the user passed the full path, we can use it directly in the URL if we format correctly.
            # But usually the library or API expects the resource name.
            
            # Check if VERTEX_ENDPOINT_ID is already a full path
            if "projects/" in vertex_endpoint_id:
                 url = f"https://{vertex_region}-aiplatform.googleapis.com/v1/{vertex_endpoint_id}:predict"
            else:
                 url = f"https://{vertex_region}-aiplatform.googleapis.com/v1/projects/{vertex_project_id}/locations/{vertex_region}/endpoints/{vertex_endpoint_id}:predict"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"instances": [encoded_image]}, # Custom model expects list of strings
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Adapt response. Vertex AI returns {"predictions": [...]}
                # Our model returns {"top1": ..., "topk": ...} inside the prediction
                if result.get("predictions"):
                    # The prediction list usually contains the output of the model.
                    # Assuming our model output structure is preserved.
                    predictions = result["predictions"][0]

        except Exception as exc:
            logger.error(f"Vertex AI inference failed: {exc}")
            raise HTTPException(status_code=500, detail=f"Vertex AI inference failed: {exc}")
    elif MODEL_SERVICE_URL:
         # Keep legacy internal call just in case, or remove it?
         # User said "leave the model outside of kubernetes", so we can probably remove or deprecate.
         # I'll leave it as a fallback if VERTEX_ENDPOINT_ID is not set.
        try:
            # Encode image to base64 for the Vertex/Model service
            import base64
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{MODEL_SERVICE_URL}/predict",
                    json={"instances": [encoded_image]},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                if result.get("predictions"):
                    predictions = result["predictions"][0]
        except Exception as exc:
            logger.error(f"Model service failed: {exc}")
            raise HTTPException(status_code=500, detail=f"Model service failed: {exc}")
    else:
        # Fallback to local inference
        try:
            predictions = run_inference(image_bytes)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    if not predictions.get("top1"):
        raise HTTPException(status_code=500, detail="Model returned no predictions.")

    top_label = predictions["top1"][0]["label"]
    # Format label: replace underscores with spaces and title case
    formatted_label = top_label.replace("_", " ").title()
    identified_foods = formatted_label
    
    # Get triggers from Gemini
    triggers = gemini_utils.get_food_triggers(formatted_label, resized_bytes)
    
    # Ensure user exists
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(email="demo@test.com", name="Demo")
        db.add(user)
        db.commit()

    # Lookup nutrition
    nutrition = NUTRITION_LOOKUP.get(identified_foods.lower(), {"protein": 0.0, "carbs": 0.0, "fat": 0.0})

    new_meal = models.Meal(
        image_url="https://via.placeholder.com/150?text=Food", # Placeholder since we aren't storing the file
        identified_foods=identified_foods,
        protein=nutrition["protein"],
        carbs=nutrition["carbs"],
        fat=nutrition["fat"],
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
