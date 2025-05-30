from pydantic import BaseModel

class EmailData(BaseModel):
    subject: str
    sender: str
    body: str

