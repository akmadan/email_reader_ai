from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from app.models.email import EmailData
from typing import Dict, Union
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelProvider(Enum):
    """Enum for supported model providers"""
    GEMINI = "gemini"
    OPENAI = "openai"

class LangchainService:
    """Langchain Service to talk to multiple LLM providers"""

    def __init__(self, model_provider: Union[ModelProvider, str] = ModelProvider.GEMINI):
        """
        Initialize the Langchain Service with specified provider
        
        Args:
            model_provider: Either ModelProvider enum or string ("gemini"/"openai")
        """
        # Handle string input
        if isinstance(model_provider, str):
            try:
                model_provider = ModelProvider(model_provider.lower())
            except ValueError:
                raise ValueError(f"Invalid model provider: {model_provider}. Use 'gemini' or 'openai'")
        
        self.model_provider = model_provider
        
        # Common configuration
        self.max_tokens = 500  # Reasonable summary length
        self.temperature = 0.3  # Lower temperature for consistent summaries
        
        # Initialize LLM based on provider
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """
        Initialize the appropriate LLM based on the model provider
        
        Returns:
            Configured LLM instance
        """
        if self.model_provider == ModelProvider.GEMINI:
            return self._initialize_gemini()
        elif self.model_provider == ModelProvider.OPENAI:
            return self._initialize_openai()
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def _initialize_gemini(self):
        """Initialize Gemini LLM"""
        
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        print(f"Debug - GEMINI_API_KEY present: {bool(gemini_api_key)}")
        print(f"Debug - GEMINI_API_KEY length: {len(gemini_api_key) if gemini_api_key else 0}")
        
        if not gemini_api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY in env"
            )
        
        # Gemini model configuration
        self.model_name = "gemini-2.0-flash-001"  # Latest fast model
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                google_api_key=gemini_api_key,
                top_p=0.8,
                top_k=40,
            )
            return llm
        except Exception as e:
            print(f"Debug - Error initializing Gemini: {str(e)}")
            raise

    def _initialize_openai(self):
        """Initialize OpenAI LLM"""
        # Check for API key
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
            )
        
        # OpenAI model configuration
        self.model_name = "gpt-4o"
        
        try:
            llm = ChatOpenAI(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                openai_api_key=openai_api_key,
                )
            return llm
        except Exception as e:
            raise

    def create_summary_prompt(self, email_data: EmailData) -> str:
        """
        Create a well-structured prompt for email summarization
        
        Args:
            email_data: EmailData object containing email information
            
        Returns:
            str: Formatted prompt for the LLM
        """
        prompt = f"""Please provide a concise summary of this email. Focus on the main purpose, key information, and any required actions.

Subject: {email_data.subject}
Sender: {email_data.sender}
Email Body: {email_data.body}

Please summarize this email in 2-3 clear sentences that capture:
1. The main purpose or reason for the email
2. Key information or important details
3. Any actions required or deadlines mentioned

Summary:"""
        
        return prompt

    def _validate_email_data(self, email_data: EmailData) -> Dict[str, any]:
        """
        Validate email data before processing
        
        Args:
            email_data: EmailData object to validate
            
        Returns:
            Dict: Validation result
        """
        # Check if essential fields are present
        if not email_data.subject and not email_data.body:
            return {
                "valid": False,
                "error": "Email has no subject or body content"
            }
        
        # Check minimum content length
        total_content = f"{email_data.subject} {email_data.body}".strip()
        if len(total_content) < 10:
            return {
                "valid": False,
                "error": "Email content too short for meaningful summary",
                "suggestion": f"Brief email from {email_data.sender}: {total_content}"
            }
        
        return {"valid": True}

    def _handle_long_content(self, email_data: EmailData) -> EmailData:
        """
        Handle very long email content that might exceed token limits
        
        Args:
            email_data: EmailData object
            
        Returns:
            EmailData: Potentially truncated email data
        """
        # Conservative estimate: 1 token ≈ 4 characters
        max_input_chars = 12000  # Leave room for prompt and response
        
        total_content = f"{email_data.subject} {email_data.sender} {email_data.body}"
        
        if len(total_content) > max_input_chars:
            # Calculate available space for body
            overhead = len(email_data.subject) + len(email_data.sender) + 200  # Buffer
            max_body_length = max_input_chars - overhead
            
            if max_body_length > 0:
                original_length = len(email_data.body)
                email_data.body = email_data.body[:max_body_length] + f"\n\n[Content truncated - original: {original_length} chars]"
        
        return email_data

    def summarize_email(self, subject: str, sender: str, body: str) -> Dict[str, any]:
        """
        Generate a summary of an email using the configured LLM provider
        
        Args:
            subject: Email subject line
            sender: Email sender
            body: Email body content
            
        Returns:
            Dict containing:
                - success: bool
                - summary: str (if successful)
                - error: str (if failed)
                - provider: str (model provider used)
                - model: str (specific model used)
        """
        try:
            # Create email data object
            email_data = EmailData(subject=subject, sender=sender, body=body)
            
            # Validate email data
            validation = self._validate_email_data(email_data)
            if not validation["valid"]:
                if "suggestion" in validation:
                    # Handle very short emails
                    return {
                        "success": True,
                        "summary": validation["suggestion"],
                        "provider": self.model_provider.value,
                        "model": "short_email_handler"
                    }
                else:
                    return {
                        "success": False,
                        "error": validation["error"]
                    }
            
            # Handle long content
            email_data = self._handle_long_content(email_data)
            
            # Create prompt
            prompt = self.create_summary_prompt(email_data)
            
            # Prepare messages for LangChain
            messages = [
                ("system", "You are a helpful email summarization assistant. Provide clear, concise summaries that capture the essential information and any required actions."),
                ("human", prompt),
            ]
            
            response = self.llm.invoke(messages)
            
            # Extract summary from response
            summary = response.content.strip()
            
            if not summary:
                return {
                    "success": False,
                    "error": "Empty response received from the model"
                }
            return {
                "success": True,
                "summary": summary,
                "provider": self.model_provider.value,
                "model": self.model_name
            }
            
        except Exception as e:
            error_message = str(e)            
            # Handle provider-specific errors
            if self.model_provider == ModelProvider.OPENAI:
                if "rate_limit_exceeded" in error_message.lower():
                    error_message = "OpenAI API rate limit exceeded. Please try again later."
                elif "invalid_api_key" in error_message.lower():
                    error_message = "Invalid OpenAI API key. Please check your credentials."
                elif "insufficient_quota" in error_message.lower():
                    error_message = "OpenAI API quota exceeded. Please check your billing."
            
            elif self.model_provider == ModelProvider.GEMINI:
                if "api_key_invalid" in error_message.lower():
                    error_message = "Invalid Gemini API key. Please check your credentials."
                elif "quota_exceeded" in error_message.lower():
                    error_message = "Gemini API quota exceeded. Please try again later."
                elif "rate_limit" in error_message.lower():
                    error_message = "Gemini API rate limit exceeded. Please try again later."
            
            return {
                "success": False,
                "error": error_message,
                "provider": self.model_provider.value
            }

