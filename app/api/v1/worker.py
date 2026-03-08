from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_worker, get_current_user, get_current_user_id
from app.services.Worker_Service import WorkerService
from app.schemas.Worker import WorkerCreate, WorkerUpdate, WorkerResponse, WorkerSummary
from app.schemas.Common import APIResponse, PaginatedResponse

router = APIRouter()


# Create Worker Profile 
@router.post("/", response_model=APIResponse[WorkerResponse])

def create_profile(
    data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_worker),
):
    user_id = int(current_user["sub"])
    worker = WorkerService(db).register_worker(user_id, data)
    return APIResponse(message="Profile created", data=worker)


# Get My Profile 
@router.get("/me", response_model=APIResponse[WorkerResponse])

def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_worker),
):
    user_id = int(current_user["sub"])
    worker = WorkerService(db).get_profile_by_user_id(user_id)
    return APIResponse(data=worker)


# Get Worker by ID 
@router.get("/{worker_id}", response_model=APIResponse[WorkerResponse])

def get_profile(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    worker = WorkerService(db).get_worker_profile(worker_id)
    return APIResponse(data=worker)


# Update My Profile
@router.put("/me", response_model=APIResponse[WorkerResponse])

def update_profile(
    data: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_worker),
):
    user_id = int(current_user["sub"])
    worker = WorkerService(db).update_worker_profile(user_id, data)
    return APIResponse(message="Profile updated", data=worker)


# Update Availability ─
@router.patch("/me/availability", response_model=APIResponse[WorkerResponse])


def update_availability(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_worker),
):
    user_id = int(current_user["sub"])
    worker = WorkerService(db).update_availability(user_id, data["availability"])
    return APIResponse(message="Availability updated", data=worker)


# Search Workers by Skill ─
@router.get("/search/skill", response_model=PaginatedResponse[WorkerSummary])

def search_by_skill(
    skill: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return WorkerService(db).search_worker(skill, page, page_size)


# ─── Get Nearby Workers ──────────────────────────────────────────
@router.get("/search/nearby", response_model=PaginatedResponse[WorkerSummary])

def get_nearby(
    skill: str = Query(...),
    city: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return WorkerService(db).get_nearby(skill, city, page, page_size)