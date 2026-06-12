import bcrypt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db.mongo import db  # Aapki mongo connection file

from app.db.mongo import users

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- CONFIGURATION ---
# Note: Real project mein inhein .env file mein hona chahiye
SECRET_KEY = " "
ALGORITHM = " "
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 Hours

# --- MODELS ---
class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- HELPER FUNCTIONS (Updated to use direct bcrypt) ---

def get_password_hash(password: str):
    # Password ko bytes mein convert karna zaroori hai
    pwd_bytes = password.encode('utf-8')
    # Salt generate karein aur hash banayein
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Database mein save karne ke liye wapas string mein convert karein
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        # Plain password aur hashed password dono ko bytes mein convert karke check karein
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ROUTES ---

@router.post("/signup")
async def signup(user: UserSignup):
    # 1. Check karein ke email pehle se toh nahi hai
    existing_user = db.users.find_one({"email": user.email.lower().strip()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        # 2. Password hash karein
        hashed_pwd = get_password_hash(user.password)
        
        # 3. Data prepare karein
        user_data = {
            "full_name": user.full_name,
            "email": user.email.lower().strip(),
            "password": hashed_pwd,
            "created_at": datetime.utcnow()
        }
        
        # 4. MongoDB mein save karein
        db.users.insert_one(user_data)
        return {"status": "success", "message": "User created successfully!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup Error: {str(e)}")

@router.post("/login")
async def login(user: UserLogin):
    clean_email = user.email.lower().strip()
    
    # 1. User dhoondein
    db_user = db.users.find_one({"email": clean_email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")
    
    # 2. Password verify karein
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid Email or Password")
    
    # 3. Token generate karein
    token = create_access_token(data={"sub": db_user["email"], "name": db_user["full_name"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": db_user["full_name"],
            "email": db_user["email"]
        }
    }