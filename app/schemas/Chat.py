from app.core.config import settings
from pydantic import BaseModel , field_validator
from typing import Optional , List
from datetime import datetime

class SendMessageRequest(BaseModel):
    content : str             
    
    @field_validator
    @classmethod
    def validate_message(cls , v):
        
        v = v.strip()
        
        if not v:
            raise ValueError("Message cannot be empty")
        
        if len(v) > settings.WS_MESSAGE_MAX_LENGTH:
            raise ValueError(f"Message too long. Max {settings.WS_MESSAGE_MAX_LENGTH} characters")
        
        return v
    

# --------------------------------------- Response Schemas --------------------------------------------
class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    id: int
    application_id: int
    worker_id: int
    employer_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------  WebSocket Message Format ------------------------------------------

# This is the JSON format sent/received over WebSocket
class WSMessage(BaseModel):
    type: str           # "message" | "read" | "typing" | "error"
    room_id: int
    sender_id: Optional[int] = None
    content: Optional[str] = None
    message_id: Optional[int] = None    