import openai
import os
from typing import Dict, Optional
from models.email import EmailData

class OpenAIService:
    """OpenAI Service Class"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI Service
        
        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        
        # Configuration
        self.model = "gpt-4o"  
        self.max_tokens = 500  # Reasonable summary length
        self.temperature = 0.3  # Lower temperature for consistent summaries
    

    def create_summary_prompt(self, email_data: EmailData) -> str:
        """
        Create a well-structured prompt for email summarization
        
        Args:
            email_data: EmailData object containing email information
            
        Returns:
            str: Formatted prompt for OpenAI
        """
        prompt = f"""Please provide a concise summary of this email. Focus on the main purpose, key information, and any required actions.

        Subject: {email_data.subject}
        Sender: {email_data.sender}
        Email Body: {email_data.body}

        Summary:"""
        
        return prompt
    
    def summarize_email(self, subject: str, sender: str, body: str) -> Dict[str, any]:
        """
        Generate a summary of an email using OpenAI
        
        Args:
            subject: Email subject line
            sender: Email sender
            body: Email body content
            
        Returns:
            Dict containing:
                - success: bool
                - summary: str (if successful)
                - error: str (if failed)
                - token_usage: dict (API usage info)
        """
        try:
            # Create email data object
            email_data = EmailData(subject=subject, sender=sender, body=body)
            
            
            prompt = self.create_summary_prompt(email_data)
            
            # Check prompt length (OpenAI has token limits)
            if len(prompt) > 12000:  # Rough estimate for token limit
                # Truncate body if too long
                max_body_length = 8000 - len(email_data.subject) - len(email_data.sender)
                email_data.body = email_data.body[:max_body_length] + "... [truncated]"
                prompt = self._create_summary_prompt(email_data)
                
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that creates concise, clear email summaries. Focus on key information and actionable items."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,  # Encourage diverse language
                frequency_penalty=0.1   # Reduce repetition
            )
            
            # Extract summary from response
            summary = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "summary": summary,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "method": "openai_api"
            }
            
        except openai.error.RateLimitError:
            return {
                "success": False,
                "error": "API rate limit exceeded. Please try again later."
            }
            
        except openai.error.AuthenticationError:
            return {
                "success": False,
                "error": "Invalid API key. Please check your OpenAI credentials."
            }
            
        except openai.error.InvalidRequestError as e:
            return {
                "success": False,
                "error": f"Invalid request: {str(e)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }
