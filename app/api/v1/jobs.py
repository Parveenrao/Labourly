from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_worker, get_current_employer
from app.services.Job_Service import JobService
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobSummary, JobApplyRequest, JobApplicationResponse
from app.schemas.Common import APIResponse, PaginatedResponse

router = APIRouter()


# Post a Job 
@router.post("/", response_model=APIResponse[JobResponse])

def post_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_employer),
):
    user_id = int(current_user["sub"])
    job = JobService(db).post_job(user_id, data)
    return APIResponse(message="Job posted successfully", data=job)


# Get Job by ID 

@router.get("/{job_id}", response_model=APIResponse[JobResponse])

def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    job = JobService(db).get_job(job_id)
    return APIResponse(data=job)


# Get Nearby Jobs 
@router.get("/search/nearby", response_model=PaginatedResponse[JobSummary])

def get_nearby_jobs(
    skill: str = Query(...),
    city: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
                                        ):
    return JobService(db).get_nearby_jobs(skill, city, page, page_size)


# Apply to Job 
@router.post("/{job_id}/apply", response_model=APIResponse[JobApplicationResponse])

def apply_to_job(
    job_id: int,
    data: JobApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_worker),
                                              ):
    user_id = int(current_user["sub"])
    application = JobService(db).apply_to_job(user_id, job_id, data.cover_note)
    return APIResponse(message="Application submitted", data=application)


# ─── Hire Worker ─────────────────────────────────────────────────
@router.post("/{job_id}/hire/{application_id}", response_model=APIResponse[JobApplicationResponse])
async def hire_worker(
    job_id: int,
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_employer),
):
    user_id = int(current_user["sub"])
    application = await JobService(db).hire_worker(user_id, job_id, application_id)
    return APIResponse(message="Worker hired successfully", data=application)


#Complete Job 
@router.post("/{job_id}/complete", response_model=APIResponse[JobResponse])

def complete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_employer),
):
    user_id = int(current_user["sub"])
    job = JobService(db).complete_job(user_id, job_id)
    return APIResponse(message="Job marked as completed", data=job)