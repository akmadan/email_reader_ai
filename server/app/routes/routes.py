from fastapi import APIRouter, HTTPException
from app.controllers.email_summarizer_controller import EmailSummarizerController
from app.models.email import EmailData
from typing import Dict, Any
from email_routes import email_summariser_router

router = APIRouter()

router.use(email_summariser_router)
