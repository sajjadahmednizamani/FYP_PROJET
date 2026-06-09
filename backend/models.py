from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    # Full Name: Min 3 characters, Max 50
    full_name: str = Field(..., min_length=3, max_length=50, example="John Doe")
    
    # Email: Automatic format validation
    email: EmailStr = Field(..., example="john@example.com")
    
    # Education: e.g., Bachelors, Masters
    education_level: str = Field(..., example="Bachelors")
    
    # GPA: Usually between 0 and 4.0 or 10.0
    gpa: float = Field(..., ge=0, le=10.0, example=3.8)
    
    # IELTS: Range 0 to 9.0
    ielts_score: float = Field(..., ge=0, le=9.0, example=7.5)
    
    # Work Exp: Minimum 0 years
    work_experience_years: int = Field(..., ge=0, example=2)
    
    # Target Country: e.g., CANADA, UK
    target_country: str = Field(..., example="Canada")
    
    # Budget: Minimum 0
    budget: int = Field(..., ge=0, example=25000)

    # Pydantic v2 Configuration
    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "education_level": "Bachelors",
                "gpa": 3.5,
                "ielts_score": 7.5,
                "work_experience_years": 2,
                "target_country": "Canada",
                "budget": 20000
            }
        }
    }