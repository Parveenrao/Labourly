from app.utils.constants import NotificationType
from pydantic import BaseModel , field_validator , Field
from typing import Dict , List , Optional ,Any
from datetime import datetime


# --------------------- Resquest Schema ----------------------------------------

# used internally by services , not exposed to api 

class CreateNotificationRequest(BaseModel):
    user_id : str 
    
    title : str 
    body : str      
    type : NotificationType
    data : Dict[str , Any] = Field(default_factory=dict)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls , value):
        if not value.strip():
            raise ValueError("Title cannot be empty")
        
        if len(value) > 150:
            raise ValueError("Title too long")
        
        return value
    
    @field_validator("body")
    @classmethod
    def validate_body(cls, value):
        if not value.strip():
            raise ValueError("Body cannot be empty")
        return value
    
    
class MarkAsReadRequest(BaseModel):
    """Mark specific notifications as read"""
    notification_ids: List[int]  = Field(min_length=1 , max_length=1000)
    
    @field_validator("notification_ids")
    @classmethod
    def validate_notifications(cls , values):
        if any(i <= 0 for i in values):
            return ValueError("Notification ids must be positive id integer")
        
        return list(set(values))
    

#---------------- Response Schema ------------------------------------------

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    data: Dict[str, Any]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Use orm_mode=True if Pydantic v1


class NotificationListResponse(BaseModel):
    """Paginated notification list with unread count"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int = 1
    page_size: int = 10
    total_pages: int


class UnreadCountResponse(BaseModel):
    """Quick unread count — polled by frontend for badge"""
    unread_count: int    
