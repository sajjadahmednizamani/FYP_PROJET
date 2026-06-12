import os
import json
import httpx
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# ✅ Prefix set to /docs-assistant for consistent routing
router = APIRouter(prefix="/docs-assistant", tags=["Document Assistant"])

# AI Setup
genai.configure(api_key=os.getenv(" "))

def get_working_model_content(prompt):
    """
    Model fallback logic: Tries 2.5-flash, then 1.5-flash, then Pro
    to handle Quota (429) errors.
    """
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_order = [
            'models/gemini-2.5-flash', 
            'models/gemini-1.5-flash', 
            'models/gemini-pro'
        ]
        
        final_list = priority_order + [m for m in available_models if m not in priority_order]

        for model_name in final_list:
            if model_name in available_models:
                try:
                    print(f"🔄 AI Attempting with: {model_name}")
                    model_instance = genai.GenerativeModel(model_name)
                    response = model_instance.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    print(f"⚠️ {model_name} busy or error: {str(e)[:50]}")
                    continue
        return None
    except Exception as e:
        print(f"❌ Critical Discovery Error: {str(e)}")
        return None

# Model for SOP Request
class DocRequest(BaseModel):
    type: str
    fullName: str
    nationality: str
    university: Optional[str] = ""
    course: str
    cgpa: str
    ielts: Optional[str] = "N/A"
    workExp: Optional[str] = "0"
    background: Optional[str] = ""
    futureGoals: Optional[str] = ""

# 1️⃣ Route: SOP Generate Karna
@router.post("/generate-sop")
async def generate_document(req: DocRequest):
    try:
        if req.type == "SOP":
            prompt = f"""
            Role: Expert Academic Consultant. 
            Task: Write a high-quality, professional 1000-word Statement of Purpose for {req.fullName}.
            
            Details:
            - Nationality: {req.nationality}
            - Program: {req.course} at {req.university}
            - Academics: CGPA {req.cgpa}, IELTS {req.ielts}
            - Experience: {req.workExp} years
            - Career Goals: {req.futureGoals}
            
            Use formal academic tone and express a strong intent to return to {req.nationality}.
            """
        else:
            prompt = f"Write a formal visa cover letter for {req.fullName} from {req.nationality} applying for {req.course}."

        result = get_working_model_content(prompt)
        if not result:
            raise HTTPException(status_code=500, detail="AI Service overloaded. Try again in 1 min.")
        
        return {"status": "success", "generated_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2️⃣ Route: LinkedIn Data Import (FIXED DATA EXTRACTION)
@router.post("/import-linkedin")
async def import_linkedin_data(payload: dict):
    access_token = payload.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Access Token required")

    async with httpx.AsyncClient() as client:
        # A. LinkedIn official API se basic profile fetch karna
        user_res = await client.get(

            "https://api.linkedin.com/v2/userinfo",
            
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch data from LinkedIn API")
            
        raw_data = user_res.json()

        # B. AI Logic: Strictly Extracting real data only
        prompt = f"""
        Extract professional information from this raw LinkedIn JSON: {json.dumps(raw_data)}
        
        STRICT RULES:
        1. Extract the actual "full_name" and "email".
        2. For "skills", "projects", and "achievements", ONLY extract them if they are explicitly present in the provided JSON.
        3. If any field is NOT found in the JSON, you MUST return the string "Not Available" for that field. 
        4. DO NOT invent, guess, or suggest fake skills or projects based on the name.
        
        Return the result in this STRICT JSON format:
        {{
            "full_name": "string",
            "email": "string",
            "education_level": "string or Not Available",
            "work_exp_years": integer or 0,
            "skills": "string or Not Available",
            "projects": "string or Not Available",
            "achievements": "string or Not Available"
        }}
        IMPORTANT: Return ONLY the JSON object.
        """
        
        result = get_working_model_content(prompt)
        
        if result:
            try:
                # Clean JSON Markdown
                clean_json = result.replace("```json", "").replace("```", "").strip()
                return {"status": "success", "data": json.loads(clean_json)}
            except:
                raise HTTPException(status_code=500, detail="AI returned invalid data format.")

        # Fallback if AI fails
        return {
            "status": "success", 
            "data": {
                "full_name": raw_data.get('name', 'Not Available'),
                "email": raw_data.get('email', 'Not Available'),
                "education_level": "Not Available",
                "work_exp_years": 0,
                "skills": "Not Available",
                "projects": "Not Available",
                "achievements": "Not Available"
            }
        }