from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.User_Repo import UserRepository
from app.schemas.Common import APIResponse, SuccessResponse

router = APIRouter()


# Get Current User 
@router.get("/me", response_model=APIResponse[dict])

def get_me(
    current_user: dict = Depends(get_current_user),
):
    return APIResponse(data={
        "user_id": current_user.get("sub"),
        "role": current_user.get("role"),
        "phone": current_user.get("phone"),
    })


# Deactivate Account 
@router.delete("/me", response_model=SuccessResponse)

def deactivate_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    UserRepository(db).deactivate(user_id)
    return SuccessResponse(message="Account deactivated successfully")


# Reactivate Account 
@router.patch("/me/reactivate", response_model=SuccessResponse)

def reactivate_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    UserRepository(db).reactivate(user_id)
    return SuccessResponse(message="Account reactivated successfully")