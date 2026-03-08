from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.Rating_Service import RatingService
from app.schemas.Rating import RatingCreate, RatingResponse, RatingSummary
from app.schemas.Common import APIResponse

router = APIRouter()


#  Submit Rating 
@router.post("/", response_model=APIResponse[RatingResponse])

def submit_rating(
    data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    role = current_user["role"]
    rating = RatingService(db).submit_rating(user_id, role, data)
    return APIResponse(message="Rating submitted", data=rating)


# 
# Get Worker Rating Summary 
@router.get("/worker/{worker_id}", response_model=APIResponse[RatingSummary])

def get_worker_ratings(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    summary = RatingService(db).get_worker_summary(worker_id)
    return APIResponse(data=summary)


# Get Employer Rating Summary 
@router.get("/employer/{employer_id}", response_model=APIResponse[RatingSummary])

def get_employer_ratings(
    employer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    summary = RatingService(db).get_employer_summary(employer_id)
    return APIResponse(data=summary)