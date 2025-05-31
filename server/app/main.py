from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
import os
from app.utils.logging import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Email Reader AI",
    description="An API for summarizing emails and converting them to speech",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1")

# Health check endpoint
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok", "message": "API is running"}