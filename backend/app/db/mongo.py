import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv(" ")

# ✅ Connection Setup
client = MongoClient( )
db = client["goglobalai"]

# ✅ Collections (Directly export karein taake 'None' ka masla na ho)
users = db["users"]
profiles = db["profiles"]
user_documents = db["user_documents"]
chat_messages = db["chat_messages"]
user_predictions = db["user_predictions"]

print("✅ MongoDB Atlas Collections Initialized")