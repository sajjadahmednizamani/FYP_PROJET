from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import linkedin, ocr_assistant
import feedparser # Top par import karein

from app.api import admin # Yeh line top par add karein
from app.api import profile
 
# ✅ Saare routers ko import karna zaroori hai
from app.api import auth, test_db, chatbot, profile, eligibility, recommender, docs_assistant 

# FastAPI Initialize
app = FastAPI(title="GoGlobalAI Backend")

# ✅ CORS Setup (Frontend connection ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Har feature ka router yahan register hona chahiye
app.include_router(auth.router)           # Login/Signup
app.include_router(chatbot.router)        # AI Chatbot (RAG)
app.include_router(profile.router)        # User Profile
app.include_router(eligibility.router)    # ML Prediction
app.include_router(recommender.router)   
app.include_router(docs_assistant.router) # SOP Generator
app.include_router(test_db.router)        # DB Test
app.include_router(ocr_assistant.router)
app.include_router(linkedin.router)
 
app.include_router(admin.router)      # Admin Panel

@app.get("/")
def home():
    return {"message": "GoGlobalAI API is running smoothly"}



# ... (baaki code wahi rehne dein) ...

@app.get("/visa-news")
def get_visa_news():
    try:
        # 1. Google News RSS Feed URL (Specifically for Student Visas & Immigration)
        rss_url = "https://news.google.com/rss/search?q=student+visa+immigration+updates&hl=en-US&gl=US&ceid=US:en"
        
        # 2. Feed parhna
        feed = feedparser.parse(rss_url)
        
        # 3. Pehli 5-7 taza khabrein nikalna
        news_list = []
        for entry in feed.entries[:7]:
            # Sirf title uthayenge ticker ke liye
            news_list.append(entry.title)
            
        # 4. Agar internet na ho ya feed khali ho toh backup news dikhana
        if not news_list:
            return ["🇨🇦 Canada: New sessions starting soon.", "🇬🇧 UK: Check updated visa guidance."]
            
        return news_list

    except Exception as e:
        print(f"News Fetch Error: {e}")
        # Fallback news taake frontend crash na ho
        return ["Stay tuned for live visa updates!"]