from app.models.email import EmailData
from app.services.murfai_service import MurfAIService
from app.services.langchain_service import LangchainService
from fastapi import HTTPException
from typing import Dict, Any

class EmailSummarizerController:
    def __init__(self):
        self.murf_service = MurfAIService()
        self.langchain_service = LangchainService()

    async def summarize_email(self, email_data: EmailData) -> Dict[str, Any]:
        """
        Summarize the email content and convert it to speech
        
        Args:
            email_data (EmailData): The email data containing subject, sender, and body
            
        Returns:
            Dict[str, Any]: A dictionary containing the summary and audio file
            
        Raises:
            HTTPException: If there's an error in summarization or text-to-speech conversion
        """
        try:
            # Create a summary text from the email data
            summary_text = self.langchain_service.summarize_email(
                email_data.subject, 
                email_data.sender,
                email_data.body
            )
            
            if not summary_text:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate email summary"
                )
            
            # Convert the summary to speech
            audio_file = await self.murf_service.text_to_speech(summary_text)
            
            if not audio_file:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate audio file"
                )
            
            return {
                "status": "success",
                "data": {
                    "summary": summary_text,
                    "audio_file": audio_file
                }
            }
            
        except Exception as e:
            # Log the error here if you have a logging system
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while processing the email: {str(e)}"
            ) 