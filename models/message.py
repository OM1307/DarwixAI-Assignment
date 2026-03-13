from pydantic import BaseModel

class Message(BaseModel):
    customer_id: str
    channel: str
    text: str
    timestamp: str
