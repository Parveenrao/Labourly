from pydantic import BaseModel , field_validator 
from app.utils.constants import Availability , Skill , Experience
from datetime import datetime 
from typing import Dict , List , Optional


# ----------------- Request Schema --------------------------------

class WorkerCreate(BaseModel):
    name : str
    bio : Optional[str] = None
    skills : Optional[str] = None
    experience : str     
    rates : Dict[str , float]
    city : str   
    area : str    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    travel_distance_km: int = 5
    
    @field_validator("skills")
    @classmethod
    def validate_skills(cls , v):
        if not v:
            raise ValueError("At least one skill is required") 
        
        invalid = [skills for skills in v if skills not in Skill]  
        
        if invalid:
            raise ValueError(f"Invalid skill : {invalid} . Choose from : {Skill.all}")  
        
        return v 
    
    @field_validator("experience")
    @classmethod
    def validate_experience(cls , v):
        
        valid = [Experience.BEGINNER , Experience.ONE_TO_TWO , Experience.THREE_TO_FIVE , Experience.FIVE_PLUS]
        
        if v not in valid:
            raise ValueError(f"Invalid Experience. Choose from : {valid}")
        
        return v 
    
    
    @field_validator("travel_distance_km")
    @classmethod
    def validate_travel_distance(cls , v):
        
        if v not in [2 ,5 ,10 ,20 ,50]:
            raise ValueError("Travel distance must be 2, 5, 10 ,20 ,50 km")
        return v


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    languages: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    rates: Optional[Dict[str, float]] = None
    city: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    travel_distance_km: Optional[int] = None
    availability: Optional[str] = None
    
class UpdateAvailability(BaseModel):
    availability : str              
    
    @field_validator("availability")
    @classmethod
    def validate_availability(cls , v):
        
        valid = [Availability.BUSY , Availability.ON_LEAVE , Availability.AVAILABLE]
        
        if v not in valid:
            raise ValueError(f"Invalid availability . Choose from {valid}")


# ------------------- Response Schemas ----------------------------------------
class WorkerResponse(BaseModel):
    id: int
    name: str
    photo_url: Optional[str]
    bio: Optional[str]
    languages: List[str]
    skills: List[str]
    experience: str
    rates: Dict[str, float]
    city: str
    area: str
    travel_distance_km: int
    availability: str
    work_photos: List[str]
    total_jobs: int
    avg_rating: float
    is_trusted: bool
    created_at: datetime

    class Config:
        from_attributes = True            
        
        
        
class WorkerSummary(BaseModel):
    """Shorter version used in job applications, search results"""
    id: int
    name: str
    photo_url: Optional[str]
    skills: List[str]
    avg_rating: float
    is_trusted: bool
    availability: str
    city: str
    area: str

    class Config:
        from_attributes = True        