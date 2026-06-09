import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.goglobal_db
profile_collection = database.get_collection("profiles")

# Helper function to format MongoDB data
def profile_helper(profile) -> dict:
    return {
        "id": str(profile["_id"]),
        "full_name": profile["full_name"],
        "email": profile["email"],
        "education_level": profile["education_level"],
        "gpa": profile["gpa"],
        "ielts_score": profile["ielts_score"],
        "work_exp": profile["work_experience_years"],
        "target_country": profile["target_country"],
    }