import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Detail (Apni URI yahan dalein)
MONGO_URI = " " 
DB_NAME = "goglobalai" # Jo bhi aapka DB name hai
COLLECTION_NAME = "profiles" # FastAPI isi collection ko use kar raha hai

async def seed_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # JSON File read karein
    with open('data/users_1000_v2.json', 'r') as f:
        data = json.load(f)

    # Data ko FastAPI format mein convert karein
    formatted_data = []
    for user in data:
        formatted_data.append({
            "full_name": user.get("name"),
            "email": user.get("email"),
            "target_country": user.get("country"),
            "gpa": user.get("gpa", 0.0),
            "ielts_score": user.get("ielts", 0.0),
            "work_experience_years": user.get("experience", 0),
            "prediction": {
                "result": user.get("status", "High Success Chance"),
                "note": "Imported from historical data"
            }
        })

    # MongoDB mein save karein
    await collection.delete_many({}) # Purana data saaf karein
    await collection.insert_many(formatted_data)
    print(f"✅ {len(formatted_data)} Users Imported to FastAPI Dashboard!")

if __name__ == "__main__":
    asyncio.run(seed_data())