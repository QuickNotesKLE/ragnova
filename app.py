# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from user import router as user_router
from chat import router as chat_router
from question import router as question_router

app = FastAPI(title="Study API", version="2.0")

# ==========================================================
# CORS Configuration
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Health Check
# ==========================================================
@app.get("/")
def health_check():
    return {"status": "ok", "message": "All routers are working 🚀"}

# ==========================================================
# Register Routers
# ==========================================================
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(question_router)

# ==========================================================
# Run the app
# ==========================================================
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
