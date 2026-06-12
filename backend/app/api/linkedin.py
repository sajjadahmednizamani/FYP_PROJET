



import os
import httpx
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()
router = APIRouter(prefix="/linkedin", tags=["LinkedIn Integration"])

genai.configure(api_key=os.getenv(""))
ai_model = genai.GenerativeModel('gemini-1.5-flash')

CLIENT_ID = os.getenv(" ")
CLIENT_SECRET = os.getenv(" ")
REDIRECT_URI = os.getenv(" ")

class CodeRequest(BaseModel):
    code: str

@router.post("/callback")
async def linkedin_callback(req: CodeRequest):
    async with httpx.AsyncClient() as client:
        # A. Access Token exchange
        token_res = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": req.code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="LinkedIn Auth Failed")
        
        token = token_res.json().get("access_token")

        # B. User Profile metadata (Name, Email, Headline)
        user_res = await client.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        raw_data = user_res.json()

        # ✅ C. POWERFUL AI PREDICTION LOGIC
        # Hum user ki 'headline' se sara data infer (guess) karwayenge
        prompt = f"""
        Analyze this LinkedIn metadata: {json.dumps(raw_data)}
        
        The user wants to check visa eligibility. Based on their name, email, and professional headline, 
        provide a high-quality professional profile. If exact data isn't there, predict it realistically.
        
        Return ONLY a JSON object with these keys:
        {{
            "full_name": "string",
            "email": "string",
            "education_level": "Bachelor or Master",
            "work_exp_years": integer,
            "suggested_gpa": float (between 2.5 and 4.0),
            "suggested_ielts": float (between 6.0 and 8.5),
            "skills": "list of relevant professional skills",
            "projects": "likely professional projects based on headline",
            "achievements": "typical certifications or honors for this role"
        }}
        """
        try:
            ai_res = ai_model.generate_content(prompt)
            clean_json = ai_res.text.replace("```json", "").replace("```", "").strip()
            final_profile = json.loads(clean_json)
        except:
            # Fallback
            final_profile = {
                "full_name": raw_data.get('name', 'User'),
                "email": raw_data.get('email', ''),
                "education_level": "Bachelor",
                "work_exp_years": 2,
                "suggested_gpa": 3.0,
                "suggested_ielts": 6.5,
                "skills": "Professional Communication",
                "projects": "Industrial Experience",
                "achievements": "Professional Excellence"
            }

        return {"status": "success", "data": final_profile}