"""
main.py — FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()
from database import create_tables
create_tables()
from routes.analyze import router

app = FastAPI(
    title="BI Platform API",
    description="Multi-Agent Business Intelligence Platform",
    version="1.0.0",
)

# ── CORS — allow Next.js frontend ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://multi-agent-bi-platform.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Serve static files (charts + reports) ────────────────────────────────────
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)

@app.get("/")
def root():
    return {
        "status":  "BI Platform API running",
        "version": "1.0.0",
        "docs":    "/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}