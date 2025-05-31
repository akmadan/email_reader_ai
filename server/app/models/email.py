from pydantic import BaseModel, Field, validator
from typing import Optional

class EmailData(BaseModel):
    """Structure for email data with validation"""
    subject: str = Field(..., min_length=1, description="Email subject")
    sender: str = Field(..., min_length=1, description="Email sender")
    body: str = Field(..., min_length=1, description="Email body content")

    @validator('subject', 'sender', 'body')
    def remove_whitespace(cls, v):
        """Remove leading/trailing whitespace from fields"""
        if isinstance(v, str):
            return v.strip()
        return v

    @validator('body')
    def validate_body_length(cls, v):
        """Validate body length"""
        if len(v) < 10:
            raise ValueError('Email body must be at least 10 characters long')
        return v

