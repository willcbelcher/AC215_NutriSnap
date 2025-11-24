# nutrisnap-backend/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MealCreate(BaseModel):
    user_id: int # Simplified for prototype

class MealOut(BaseModel):
    id: int
    identified_foods: str
    protein: float
    carbs: float
    fat: float
    triggers: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class SymptomCreate(BaseModel):
    user_id: int
    symptom_name: str
    severity: int
    notes: Optional[str] = None

class SymptomOut(BaseModel):
    id: int
    symptom_name: str
    severity: int
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True