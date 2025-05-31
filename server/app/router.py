from fastapi import APIRouter, HTTPException
from app.controllers.email_summarizer_controller import EmailSummarizerController
from app.models.email import EmailData
from typing import Dict, Any
from app.routers.email_router import email_summariser_router

router = APIRouter()

# Include the email summarizer router
router.include_router(email_summariser_router)
