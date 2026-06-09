import os
from fastapi import APIRouter, UploadFile, File
import google.generativeai as genai
import json
from PIL import Image
import io

router = APIRouter(prefix="/ocr", tags=["AI Resume Parser"])

# Gemini Setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@router.post("/scan-resume")
async def scan_resume(file: UploadFile = File(...)):
    try:
        # File read karna (Image ya PDF preview ke liye)
        request_object_content = await file.read()
        
        # AI Prompt for Extracting Data
        prompt = """
        Analyze this Resume/CV or Transcript image. 
        Extract the following information and return it in STRICT RAW JSON format:
        {
            "full_name": "string",
            "email": "string",
            "education_level": "Bachelor/Master/PhD",
            "suggested_gpa": float,
            "suggested_ielts": float,
            "work_exp_years": integer,
            "skills": "comma separated skills",
            "projects": "main projects list",
            "achievements": "awards or certifications"
        }
        If a value is not found, provide a realistic estimate based on the profile.
        Return ONLY the JSON.
        """

        # AI processing
        img = Image.open(io.BytesIO(request_object_content))
        response = model.generate_content([prompt, img])
        
        # Clean JSON Response
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)

        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}