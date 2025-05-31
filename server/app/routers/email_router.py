from fastapi import APIRouter, HTTPException
from app.controllers.email_summarizer_controller import EmailSummarizerController
from app.models.email import EmailData
from typing import Dict, Any
from pydantic import BaseModel
from app.models.email_summary import EmailSummaryData

email_summariser_router = APIRouter()
email_controller = EmailSummarizerController()

@email_summariser_router.post("/summarize", response_model=EmailSummaryData)
async def summarize_email(email_data: EmailData):
    """
    Summarize the given email content and convert it to speech
    
    Args:
        email_data (EmailData): The email data containing subject, sender, and body
        
    Returns:
        EmailSummaryData: A response containing the status and data with summary and audio file
        
    Raises:
        HTTPException: If there's an error in processing the email
    """
    try:
        return await email_controller.summarize_email(email_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 