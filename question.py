from fastapi import APIRouter
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import requests, os
from dotenv import load_dotenv

# ==========================================================
# Setup
# ==========================================================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in .env")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")

client = MongoClient(MONGO_URI)
db = client["chatpdf"]
chats_collection = db["chats"]

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

router = APIRouter(prefix="/question", tags=["question"])

# ==========================================================
# Route
# ==========================================================
@router.get("/ask")
def ask_question(chat_id: str, question: str, onlycontext: bool = True):
    chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        return {"status": "error", "answer": "Chat not found ❌"}

    context = chat["context"]

    instruction = """
    You are a study assistant 📘🧠.
    RULES:
    • Answer ONLY from the CONTEXT given.
    • Use simple, clear language.
    • If not found in context, say: "❌ Sorry, I couldn’t find anything related in your uploads."
    """

    user_prompt = f"{instruction}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}"

    payload = {"contents": [{"role": "user", "parts": [{"text": user_prompt}]}]}
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=60)
        data = response.json()
        answer = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "❌ Sorry, I couldn’t find anything related.")
            .strip()
        )

        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": {"role": "user", "text": question, "timestamp": datetime.utcnow().isoformat()}}}
        )
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": {"role": "assistant", "text": answer, "timestamp": datetime.utcnow().isoformat()}}}
        )

        return {"status": "success", "answer": answer}

    except Exception as e:
        return {"status": "error", "answer": f"API error: {str(e)}"}
