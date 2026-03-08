from pydantic import BaseModel , field_validator
from typing import Optional , List
from datetime import datetime
from app.utils.constants import JobStatus , JobType , JobUrgency , Skill , ApplicationStatus
from app.schemas.Employer import EmployerSummary


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    skill_required: List[str]
    workers_needed: int = 1
    job_type: str = JobType.ONE_TIME
    urgency: str = JobUrgency.FLEXIBLE
    city: str
    area: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    
    @field_validator("skill_required")
    @classmethod
    def validate_skills(cls , values:List[int])-> List[int]:
        
        if not values:
            raise ValueError("At least one skill is required")
        
        invalid_skills = [skills for skills in values if skills not in Skill.All]
        
        if invalid_skills:
            raise ValueError(f"Invalid skills : {invalid_skills} . Choose from {Skill.All}")
        
        return values
        
        
        @field_validator("job_type")
        @classmethod
        def validate_job(cls , v):
            if v not in [JobType.ONE_TIME , JobType.RECURRING]:
                raise ValueError("Invalid job type")
            
            return v
        
        
        @field_validator("job_type")
        def validate_job_type(cls, v):
            if v not in [JobType.ONE_TIME, JobType.RECURRING]:
                raise ValueError("Invalid job type")
            return v

        @field_validator("urgency")
        def validate_urgency(cls, v):
            if v not in [JobUrgency.TODAY, JobUrgency.THIS_WEEK, JobUrgency.FLEXIBLE]:
                raise ValueError("Invalid urgency")
            return v

        @field_validator("workers_needed")
        def validate_workers_needed(cls, v):
            if v < 1:
                raise ValueError("workers_needed must be at least 1")
            return v
    
class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    urgency: Optional[JobUrgency] = None
    status: Optional[JobStatus] = None
    
    field_validator("title", "description")
    @classmethod
    def validate_non_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty")
        return v
    
    
class JobApplyRequest(BaseModel):
    cover_note: Optional[str] = None    # optional message from worker
    
    
    

# --------------- Response Schemas -------------------------------------
class JobResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    skill_required: List[Skill]
    workers_needed: int
    job_type: JobType
    urgency: JobUrgency
    city: str
    area: str
    status: str
    employer: EmployerSummary
    created_at: datetime

    class Config:
        from_attributes = True


class JobSummary(BaseModel):
    """Shorter version for search/nearby results"""
    id: int
    title: str
    skill_required: List[Skill]
    urgency: str
    city: str
    area: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobApplicationResponse(BaseModel):
    id: int
    job_id: int
    worker_id: int
    cover_note: Optional[str]
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True    