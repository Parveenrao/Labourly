from pydantic import BaseModel , field_validator
from typing import List , Optional
from datetime import datetime

# -------------------- Request Schema -----------------------

class EmployeeCreate(BaseModel):
    name : str       
    bio : Optional[str]  = None
    city : str    
    area : str   
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    
    @field_validator("name")
    @classmethod
    def validate_name(cls , v):
        
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        elif len(v) < 100:
            raise ValueError("Name must be under 100 characters")
        
        return v
    
    
    @field_validator("latitude")
    def validate_latitude(cls, v):
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v
    
    
    
class EmployerUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters")
        return v

# -------------------------------------- Response Schemas -----------------------------------------------------
class EmployerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    photo_url: Optional[str]
    bio: Optional[str]
    city: str
    area: str
    latitude: Optional[float]
    longitude: Optional[float]
    total_jobs_posted: int
    avg_rating: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployerSummary(BaseModel):
    
    # Shorter version used in job listings
    
    id: int
    name: str
    photo_url: Optional[str]
    avg_rating: float
    total_jobs_posted: int
    city: str
    area: str

    class Config:
        from_attributes = True


class EmployerProfileResponse(BaseModel):
    
    # Full profile with jobs and ratings — shown on employer profile page
    
    id: int
    user_id: int
    name: str
    photo_url: Optional[str]
    bio: Optional[str]
    city: str
    area: str
    total_jobs_posted: int
    avg_rating: float
    created_at: datetime

    # included when fetching full profile
    recent_ratings: Optional[List[dict]] = []

    class Config:
        from_attributes = True    