from pydantic import BaseModel

class EmailSummaryData(BaseModel):
    summary: str 
    summary_audio_link: str

