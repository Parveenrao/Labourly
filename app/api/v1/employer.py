from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_employer, get_current_user
from app.services.Employer_Service import EmployerService
from app.schemas.Employer import EmployeeCreate, EmployerUpdate, EmployerResponse, EmployerProfileResponse
from app.schemas.Common import APIResponse

router = APIRouter()


# create employer profile 

@router.post("/create" , response_model=APIResponse[EmployerResponse])

def create_employer_profile(data : EmployeeCreate , db : Session = Depends(get_db) , current_user : dict = Depends(get_current_user)):
    
    user_id = int(current_user["sub"])
    
    employer = EmployerService(db).create_profile(user_id , data)
    
    return APIResponse(message="Profile created" , data = employer)


# Get My Profile 
@router.get("/me", response_model=APIResponse[EmployerResponse])

def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_employer),
                                              ):
    user_id = int(current_user["sub"])
    employer =  EmployerService(db).get_profile_user_id(user_id)
    return APIResponse(data=employer)


# Get Employer by ID 
@router.get("/{employer_id}", response_model=APIResponse[EmployerProfileResponse])

def get_profile(
    employer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    employer = EmployerService(db).get_by_full_profile(employer_id)
    return APIResponse(data=employer)


# Update My Profile 
@router.put("/me", response_model=APIResponse[EmployerResponse])

def update_profile(
    data: EmployerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_employer),
):
    user_id = int(current_user["sub"])
    employer = EmployerService(db).update_profile(user_id, data)
    return APIResponse(message="Profile updated", data=employer)