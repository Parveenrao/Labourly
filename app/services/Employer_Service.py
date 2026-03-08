from sqlalchemy.orm import Session
from loguru import logger

from app.repositories.Employer_Repo import EmployerRepository
from app.repositories.User_Repo import UserRepository
from app.schemas.Employer import EmployeeCreate, EmployerUpdate, EmployerResponse, EmployerProfileResponse
from app.utils.exception import EmployerNotFoundException, UserNotFoundException
from app.utils.Helpers import get_pagination_offset


class EmployerService:
    
    def __init__(self ,  db : Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.employer_repo = EmployerRepository(db)
        
    
    def create_profile(self , user_id : int ,  data : EmployeeCreate) -> EmployerResponse:         
        
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException()
        
        # check existing user 
        
        existing = self.employer_repo.get_by_id(user_id)
        
        if existing:
            return EmployerResponse.model_validate(existing)
        
        
        employer = self.employer_repo.Create(
            
            user_id  = user_id , 
            name = data.name,
            bio = data.bio,
            city = data.city,
            area = data.area , 
            latitude = data.latitude,
            longitude = data.longitude,
            total_job_posted = 0 ,
            
            avg_rating = 0
             )
        logger.info(f"Employer profile created | user_id={user_id} name={data.name}")
        return EmployerResponse.model_validate(employer)
        
    # Get profile of employer 
    
    def get_profile(self , employer_id : int) -> EmployerResponse:
        
        employer = self.employer_repo.get_by_id(employer_id)
        
        if not employer:
            raise EmployerNotFoundException(employer_id)
        
        return EmployerResponse.model_validate(employer)
    
    # Get profile by user_id 
    
    def get_profile_user_id(self , user_id : int) -> EmployerResponse:  
        
        employer = self.employer_repo.get_by_user_id(user_id)
        
        if not employer:
            raise EmployerNotFoundException()
        
        return EmployerResponse.model_validate(employer)
        
    
    # Get full profile of employer
    
    def get_by_full_profile(self, employer_id : int) -> EmployerProfileResponse:  
        
        employer = self.employer_repo.get_by_ratings(employer_id)
        
        if not employer:
            raise EmployerNotFoundException()
        
        EmployerProfileResponse.model_validate(employer)
    
    # Update profile 
    
    def update_profile(self , user_id : int , data : EmployerUpdate) -> EmployerResponse:  
        
        employer =   self.employer_repo.get_by_user_id(user_id)
        
        if not employer:
            raise EmployerNotFoundException()
        
        update_data = data.model_dump(exclude_unset= True)
        if not update_data:
            return EmployerResponse.model_validate(employer)
        
        updated = self.employer_repo.update(employer.id , **update_data)
        logger.info(f"Employer profile updated | employer_id={employer.id}")
        return EmployerResponse.model_validate(updated)

              
            