from fastapi import APIRouter, HTTPException
from app.db.mongo import db
import pandas as pd
import os

router = APIRouter(prefix="/recommender", tags=["Recommendations"])

# CSV Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "global_student_migration.csv")

@router.get("/universities/{email}")
def recommend_universities(email: str):
    # 1. MongoDB se user profile uthayein
    user = db.profiles.find_one({"email": email.lower().strip()})
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found. Pehle Eligibility check karein.")

    user_gpa = float(user.get('gpa', 0))
    target_country = user.get('target_country', '').strip()

    try:
        # 2. CSV Load karein
        if not os.path.exists(CSV_PATH):
            raise HTTPException(status_code=500, detail="University database (CSV) missing!")
            
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')

        # 3. Smart Filtering
        # Filter 1: Wohi country jo user ne choose ki
        # Filter 2: GPA range (User ke GPA ke aas paas wali unis)
        mask = (df['destination_country'].str.lower() == target_country.lower()) & \
               (df['gpa_or_score'] <= user_gpa + 0.3) & \
               (df['gpa_or_score'] >= user_gpa - 0.7)
        
        filtered_df = df[mask]

        # Agar koi result na mile toh sirf country base par dikha dein
        if filtered_df.empty:
            filtered_df = df[df['destination_country'].str.lower() == target_country.lower()]

        # 4. Top 5 Results
        recommendations = filtered_df[['university_name', 'destination_city', 'course_name', 'gpa_or_score']] \
                            .sort_values(by='gpa_or_score', ascending=False) \
                            .drop_duplicates(subset=['university_name']) \
                            .head(5) \
                            .to_dict(orient='records')

        return {
            "status": "success",
            "recommended_universities": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))