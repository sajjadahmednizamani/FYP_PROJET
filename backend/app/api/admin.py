from fastapi import APIRouter, HTTPException
from app.db.mongo import profiles
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

# --- ADMIN CREDENTIALS ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "fyp_admin_123"

class AdminLogin(BaseModel):
    username: str
    password: str

# 1️⃣ LOGIN ROUTE
@router.post("/login")
async def admin_login(credentials: AdminLogin):
    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        return {"status": "success", "message": "Welcome Admin"}
    else:
        raise HTTPException(status_code=401, detail="Ghalat Username ya Password!")

# 2️⃣ DYNAMIC DASHBOARD DATA (With Filtered/Clean Data)
@router.get("/dashboard-data")
async def get_dashboard_data():
    try:
        # Filter logic: Faltu data (string, None, empty) ko count nahi karna
        junk_filter = {"full_name": {"$nin": ["string", "", None]}, "target_country": {"$nin": ["string", "", None]}}

        # 📊 Stats Calculation
        total_users = profiles.count_documents(junk_filter)
        high_success = profiles.count_documents({**junk_filter, "prediction.result": "High Success Chance"})
        moderate_success = profiles.count_documents({**junk_filter, "prediction.result": "Moderate Success Chance"})
        low_success = profiles.count_documents({**junk_filter, "prediction.result": "Low Success Chance"})
        
        # 🗺️ Country Distribution Chart (Filtered)
        country_pipeline = [
            {"$match": junk_filter},
            {"$group": {"_id": "$target_country", "count": {"$sum": 1}}}
        ]
        
        countries = []
        for doc in profiles.aggregate(country_pipeline):
            name = doc["_id"]
            # Formatting "Pak" to "Pakistan"
            if name.lower() == "pak": name = "Pakistan"
            countries.append({"name": name, "value": doc["count"]})

        # 🎯 Eligibility Chart Data
        eligibility_data = [
            {"name": "High Chance", "value": high_success},
            {"name": "Moderate", "value": moderate_success},
            {"name": "Low Chance", "value": low_success}
        ]

        # 📋 Recent 15 Users (Filter out junk)
        cursor = profiles.find(junk_filter).sort("_id", -1).limit(15)
        recent_users = []
        for u in cursor:
            u["_id"] = str(u["_id"])
            # In-loop cleanup for display
            if u.get("target_country", "").lower() == "pak":
                u["target_country"] = "Pakistan"
            recent_users.append(u)

        return {
            "stats": {
                "total": total_users, 
                "high": high_success, 
                "countries_count": len(countries)
            },
            "charts": {
                "countries": countries, 
                "eligibility": eligibility_data
            },
            "recent_users": recent_users
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3️⃣ DELETE USER ROUTE
@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    try:
        profiles.delete_one({"_id": ObjectId(user_id)})
        return {"status": "success", "message": "User deleted"}
    except:
        raise HTTPException(status_code=400, detail="ID invalid")

# 4️⃣ PERMANENT DATABASE CLEANUP (Faltu data delete karne ke liye)
@router.post("/clean-database")
async def clean_database():
    try:
        # Yeh query dhundegi aur delete karegi "string", null, aur empty records ko
        query = {
            "$or": [
                {"full_name": "string"},
                {"email": "string"},
                {"target_country": "string"},
                {"target_country": None},
                {"target_country": ""},
                {"full_name": "Pak"},
                {"email": {"$regex": "example.com"}} # Optional: junk emails delete karne ke liye
            ]
        }
        
        result = profiles.delete_many(query)
        
        return {
            "status": "success", 
            "message": f"Permanently deleted {result.deleted_count} junk records."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))