from app.models.email import EmailData
from app.services.murfai_service import MurfAIService
from app.services.langchain_service import LangchainService
from fastapi import HTTPException
from typing import Dict, Any
from app.utils.logging import logger

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
            Dict[str, Any]: A dictionary containing the summary and audio file URL
            
        Raises:
            HTTPException: If there's an error in processing the email
        """
        try:

            # Add Logging
            logger.info(f"Subject - {email_data.subject}")
            logger.info(f"Sender - {email_data.sender}")
            logger.info(f"Body - {email_data.body}")

            # Create a summary text from the email data
            summary_text: str = self.langchain_service.summarize_email(
                email_data.subject, 
                email_data.sender,
                email_data.body
            )

            logger.info(f"Summary Text - {summary_text}")
            
            if not summary_text:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate email summary"
                )
            
            # Convert the summary to speech
            audio_file = await self.murf_service.text_to_speech(text=summary_text)
            
            if not audio_file:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate audio file"
                )
            
            return {
                "summary": summary_text,
                "summary_audio_link": audio_file
            }
            
        except HTTPException as he:
            logger.error(f"HTTP error in summarize_email: {str(he)}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error in summarize_email: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while processing the email: {str(e)}"
            ) 