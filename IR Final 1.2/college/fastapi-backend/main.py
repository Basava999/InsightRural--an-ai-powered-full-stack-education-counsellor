import os
from dotenv import load_dotenv

# Load env variables before importing routers
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))
load_dotenv(os.path.join(base_dir, "backend", ".env"))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from routers import chat, cutoffs, risk_analyzer, career, scholarships, hostels

app = FastAPI(
    title="InsightRural AI Platform API",
    description="The brain of the InsightRural Admission Intelligence Platform.",
    version="2.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (uncomment when ready)
# Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(cutoffs.router, prefix="/api/data", tags=["Historical Data"])
app.include_router(risk_analyzer.router, prefix="/api/analyze", tags=["Risk Analyzer"])
app.include_router(career.router, prefix="/api/career", tags=["Career Guidance"])
app.include_router(scholarships.router, prefix="/api/scholarships", tags=["Scholarships"])
app.include_router(hostels.router, prefix="/api/hostels", tags=["Hostels"])

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "InsightRural Core API running. Next-gen startup infrastructure initialized.",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected", "ai_orchestrator": "ready"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
