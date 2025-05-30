from murf import Murf
import os

class MurfAIService:
    def __init__(self, api_key: str = "YOUR_API_KEY"):
        """
        Initialize the MurfAI service with an API key.
        
        Args:
            api_key (str): The Murf API key. Defaults to "YOUR_API_KEY"
        """
        self.client = Murf(api_key=api_key)
        self.default_voice = "en-US-natalie"

    async def text_to_speech(self, text: str, voice_id: str = None) -> str:
        """
        Convert text to speech using Murf AI.
        
        Args:
            text (str): The text to convert to speech
            voice_id (str, optional): The voice ID to use. Defaults to the default voice.
            
        Returns:
            str: The generated audio file
        """
        voice = voice_id or self.default_voice
        
        response = self.client.text_to_speech.generate(
            text=text,
            voice_id=voice
        )
        
        return response.audio_file