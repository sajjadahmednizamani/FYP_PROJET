import os
import uuid
from datetime import datetime
from typing import Optional
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Database connection
from app.db.mongo import chat_messages 
# PDF Search components
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

# ✅ 1. Configuration & API Key
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# ✅ 2. DYNAMIC MODEL DISCOVERY (Wahi purana kamyab tareeka)
def discover_working_model():
    try:
        print("🔍 Searching for available AI models...")
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority List
        for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
            if preferred in available_models:
                print(f"✅ Auto-Selected Model: {preferred}")
                return genai.GenerativeModel(preferred)
        
        # Agar koi bhi mil jaye
        print(f"✅ Using first available model: {available_models[0]}")
        return genai.GenerativeModel(available_models[0])
    except Exception as e:
        print(f"⚠️ Model discovery failed, using fallback: {e}")
        return genai.GenerativeModel('gemini-pro')

# Initialize the working model
model_engine = discover_working_model()

# ✅ 3. Vector DB Setup (Local PDF Search)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# app/api folder se bahar nikal kar vectorstore dhoondo
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "vectorstore", "db_faiss")
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

def load_vector_db():
    if os.path.exists(DB_PATH):
        try:
            return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"❌ FAISS Load Error: {e}")
    return None

vector_db = load_vector_db()

class ChatRequest(BaseModel):
    question: str
    email: Optional[str] = "guest_user"
    session_id: Optional[str] = None

# --- ROUTES ---

@router.get("/sessions/{email}")
async def get_user_sessions(email: str):
    try:
        pipeline = [
            {"$match": {"email": email.lower()}},
            {"$group": {
                "_id": "$session_id",
                "title": {"$first": "$content"},
                "time": {"$max": "$timestamp"}
            }},
            {"$sort": {"time": -1}}
        ]
        return [{"session_id": r["_id"], "title": r["title"][:30] + "..."} for r in list(chat_messages.aggregate(pipeline))]
    except: return []

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        msgs = list(chat_messages.find({"session_id": session_id}).sort("timestamp", 1))
        for m in msgs: m["_id"] = str(m["_id"])
        return msgs
    except: return []

@router.post("")
async def ask_chatbot(req: ChatRequest):
    global vector_db
    sid = req.session_id if req.session_id and req.session_id != "null" else str(uuid.uuid4())

    # Greeting handling
    if req.question.lower() in ["hi", "hello", "hey"]:
        answer = "Hello! I am your GoGlobalAI assistant. How can I help you with your visa application today?"
    else:
        # ✅ STEP A: PDF Context Retrieval
        if not vector_db:
            vector_db = load_vector_db()
        
        context = ""
        if vector_db:
            docs = vector_db.similarity_search(req.question, k=4)
            context = "\n\n".join([d.page_content.replace('\n', ' ') for d in docs])

        # chatbot.py mein prompt wali jagah ye update karein:

        prompt = f"""
        You are GoGlobalAI Visa Consultant. 
        
        INSTRUCTIONS:
        1. Detect the language of the User Question.
        2. Answer accurately using ONLY the provided Context.
        3. ALWAYS respond in the same language the user used (e.g., if user asks in Urdu, answer in Urdu).
        4. If the info is not in context, politely say so in the user's language.

        CONTEXT:
        {context}

        USER QUESTION: {req.question}
        ANSWER:"""
        try:
            # ✅ STEP C: Generate response using discovered model
            response = model_engine.generate_content(prompt)
            answer = response.text
        except Exception as e:
            print(f"❌ AI Error: {e}")
            answer = "I apologize, the AI engine is refreshing. Please try again in 5 seconds."

    # ✅ STEP D: Save to History
    try:
        chat_messages.insert_many([
            {"session_id": sid, "email": req.email.lower(), "role": "user", "content": req.question, "timestamp": datetime.utcnow()},
            {"session_id": sid, "email": req.email.lower(), "role": "bot", "content": answer, "timestamp": datetime.utcnow()}
        ])
    except: pass

    return {"answer": answer, "session_id": sid}