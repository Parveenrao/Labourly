from pydantic import BaseModel, field_validator , Field
from typing import Optional, List
from datetime import datetime

# ----- Request Schema ---------------------------------------------------------

class RatingCreate(BaseModel):
    
    # Employer can rate worker or Worker can rate employer
    
    # Role is determined by JWT 
    
    job_id : int    
    
    stars : str      
    
    review : Optional[str] = None
    
    @field_validator("stars")
    @classmethod
    def validate_stars(cls , v):
        
        if not v:
            raise ValueError("Star rating is required at leat 1")
        
        elif v < 1.0  and v > 5.0:
            raise ValueError("Star must be  between 1 and 5")      
        
        return round(v , 1)           
    
    @field_validator("review")
    @classmethod
    def validate_review(cls , v : str | None) -> str | None:
        
        if not v:
            return None
        
        cleaned = v.strip()
        
        if not cleaned:
            raise ValueError('Review cannot be empty')
        
        if len(cleaned) > 500:
            raise ValueError('Review must be under 500 characters')
        
        return cleaned
 
 
# ----------- Respons --------------------------------------------------   
    
from pydantic import model_validator

class RatingResponse(BaseModel):
    id: int
    job_id: int
    rated_by_user_id: int
    worker_id: Optional[int]
    employer_id: Optional[int]
    stars: float
    review: Optional[str]
    created_at: datetime

    @model_validator(mode="after")
    def validate_target(cls, model):                           # atlest one is set if both worker and employer are none who rate whom
        if bool(model.worker_id) == bool(model.employer_id):
            raise ValueError(
                "Exactly one of worker_id or employer_id must be set"
            )
        return model

    class Config:
        from_attributes = True    
        

class RatingWithRaterInfo(BaseModel):
    """Rating with info about who gave it — shown on profile page"""
    id: int
    job_id: int
    stars: float
    review: Optional[str]
    rated_by_name: str              # name of person who gave the rating
    rated_by_photo: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RatingSummary(BaseModel):
    avg_rating: float
    total_ratings: int
    five_star: int
    four_star: int
    three_star: int
    two_star: int
    one_star: int
    recent_ratings: List[RatingWithRaterInfo] = Field(default_factory=list)                