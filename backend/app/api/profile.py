from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.mongo import profiles
from bson import ObjectId

router = APIRouter(prefix="/profile", tags=["User Profile"])

# Pydantic model taake data validate ho sakay
class ProfileData(BaseModel):
    full_name: str
    email: str
    gpa: float
    ielts_score: float
    education_level: str
    work_experience_years: int
    target_country: str
    skills: Optional[str] = ""
    projects: Optional[str] = ""
    achievements: Optional[str] = ""
    source: str = "Manual"

# 1. Profile Save karne ka route
@router.post("/save")
def save_profile(data: ProfileData):
    try:
        user_dict = data.dict()
        email = user_dict["email"].lower().strip()
        user_dict["email"] = email
        
        # Database mein update ya insert (Upsert)
        profiles.update_one(
            {"email": email},
            {"$set": user_dict},
            upsert=True
        )
        return {"status": "success", "message": "Profile saved successfully"}
    except Exception as e:
        print(f"Error saving profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. Profile Details lane ka route (Dashboard ke liye)
@router.get("/details/{email}")
def get_user_details(email: str):
    try:
        user = profiles.find_one({"email": email.lower().strip()})
        
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # MongoDB ID ko string mein badalna zaroori hai JSON ke liye
        user["_id"] = str(user["_id"])
        
        return {
            "status": "success",
            "data": user
        }
    except Exception as e:
        print(f"Error fetching details: {e}")
        raise HTTPException(status_code=500, detail=str(e))