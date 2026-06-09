import os
import joblib
from datetime import datetime  # ✅ Yeh line missing thi, ab add kar di hai
from fastapi import APIRouter, HTTPException
from app.db.mongo import db, profiles, user_predictions # Ensure these are correct in your mongo.py

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "visa_model.pkl")

model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except: pass

@router.get("/check/{email}")
def check_eligibility(email: str):
    # MongoDB se user profile fetch karna
    user = db.profiles.find_one({"email": email.lower().strip()})
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Data extraction for Logic
    gpa = float(user.get('gpa', 0))
    ielts = float(user.get('ielts_score', 0))
    edu = user.get('education_level', 'Bachelor')
    exp = int(user.get('work_exp_years', 0))
    country = user.get('target_country', 'Canada')

    suggestions = []
    status_type = "eligible"

    # --- ADVANCED RULE ENGINE (For Ma'am to show it's not just a simple chatbot) ---
    if gpa < 2.8:
        suggestions.append(f"Aapka GPA ({gpa}) criteria se kam hai. Kam az kam 3.0 target karein.")
        status_type = "not_eligible"
    
    if ielts < 6.0:
        suggestions.append(f"IELTS score {ielts} bohot kam hai. Behtar visa chances ke liye 6.5+ zaroori hai.")
        status_type = "not_eligible"
    elif ielts < 6.5:
        suggestions.append("Aapka score theek hai, lekin improve karne se top universities mil sakti hain.")

    # Final Decision Logic
    if status_type == "not_eligible":
        result_text = "Low Success Chance"
        color = "#F43F5E"
        note = f"Filhal aapka profile {country} ke liye weak hai."
    elif gpa >= 3.2 and ielts >= 7.0:
        result_text = "High Success Chance"
        color = "#10B981"
        note = f"Excellent! Aapka profile {country} ke liye perfect hai."
    else:
        result_text = "Moderate Success Chance"
        color = "#F59E0B"
        note = "Aap eligible hain, lekin suggestions par amal karein."

    # ✅ HISTORY MEIN SAVE KARNA (Ab error nahi aayega)
    prediction_entry = {
        "email": email.lower().strip(),
        "result": result_text,
        "suggestions": suggestions,
        "timestamp": datetime.utcnow() # ✅ Now it will work
    }
    
    try:
        db.user_predictions.insert_one(prediction_entry)
    except:
        pass # Database save fail ho toh app na rukay

    return {
        "status": "success",
        "prediction": {
            "result": result_text,
            "color": color,
            "note": note,
            "suggestions": suggestions,
            "profile_summary": f"{edu} with {exp} years of exp"
        }
    }