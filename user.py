from fastapi import APIRouter, Form
from pymongo import MongoClient
import hashlib, os
from dotenv import load_dotenv

# ==========================================================
# Setup
# ==========================================================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in environment variables")

client = MongoClient(MONGO_URI)
db = client["chatpdf"]
users_collection = db["users"]

router = APIRouter(prefix="/user", tags=["user"])

# ==========================================================
# Helpers
# ==========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================================
# Routes
# ==========================================================
@router.post("/register")
def register_user(email: str = Form(...), password: str = Form(...)):
    if users_collection.find_one({"email": email}):
        return {"status": "error", "message": "User already exists ❌"}
    
    users_collection.insert_one({
        "email": email,
        "password": hash_password(password)
    })
    return {"status": "success", "message": "User registered ✅"}

@router.post("/login")
def login_user(email: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"email": email})
    if not user or user["password"] != hash_password(password):
        return {"status": "error", "message": "Invalid credentials ❌"}
    return {"status": "success", "message": "Login successful ✅", "email": email}
