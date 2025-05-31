from murf import Murf
import os
from app.utils.logging import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MurfAIService:
    def __init__(self, api_key: str = None):
        """
        Initialize the MurfAI service with an API key.
        
        Args:
            api_key (str): The Murf API key. Defaults to None (will use environment variable)
        """
        self.api_key = api_key or os.getenv('MURF_API_KEY')
        if not self.api_key:
            raise ValueError("MURF_API_KEY is required. Set it in environment variables or pass it to the constructor.")
        
        self.client = Murf(api_key=self.api_key)
        self.default_voice = "en-US-natalie"

    async def text_to_speech(self, text: str, voice_id: str = None) -> str:
        """
        Convert text to speech using Murf AI.
        
        Args:
            text (str): The text to convert to speech
            voice_id (str, optional): The voice ID to use. Defaults to the default voice.
            
        Returns:
            str: The generated audio file URL
            
        Raises:
            Exception: If there's an error in text-to-speech conversion
        """
        try:
            voice = voice_id or self.default_voice
            
            # Ensure text is a string
            if not isinstance(text, str):
                text = str(text)
            
            response = self.client.text_to_speech.generate(
                text=text,
                voice_id=voice,
                format="MP3",  # Using MP3 format for better compatibility
                channel_type="STEREO",
                sample_rate=44100
            )
            
            if not response or not response.audio_file:
                raise Exception("No audio file generated")
                
            return response.audio_file
            
        except Exception as e:
            raise Exception(f"Error in text-to-speech conversion: {str(e)}")
