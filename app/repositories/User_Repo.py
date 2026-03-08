from sqlalchemy.orm import Session  , joinedload 
from sqlalchemy import select , update , delete
from typing import Optional , List , Dict
from loguru import logger


from app.repositories.Base_repo import BaseRepository
from app.models.User import User
from app.utils.constants import UserRole
from app.repositories.Base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    
    def __init__(self  , db : Session):
        super().__init__(User , db)
        
    # Get user by phone 
    def get_by_phone(self , phone : str) -> Optional[User]:
        
        result = self._db.execute(select(User).where(User.phone == phone))
        
        return result.scalar_one_or_none()
    
    def get_by_phone_and_role(self , phone : str , role : UserRole) -> Optional[User]:
        
        stmt = (select(User).where(User.phone == phone,
                                   User.role == role))
        
        result = self._db.execute(stmt)
        
        return result.scalar_one_or_none()
    
    
    def get_with_worker_profile(self, user_id: int) -> Optional[User]:
        """Fetches user + worker profile in a single query"""
        result =self._db.execute(
            select(User)
            .options(joinedload(User.worker_profile))
            .where(User.id == user_id)
             )
        return result.scalar_one_or_none()

    def get_with_employer_profile(self, user_id: int) -> Optional[User]:
        """Fetches user + employer profile in a single query"""
        result = self._db.execute(
            select(User)
            .options(joinedload(User.employer_profile))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    
    def phone_exist(self, phone:str) -> bool:
        
        return self.exist("phone" , phone) 
    
    def is_wokrer(self , user_id : int) -> bool:
        
        query = (select(User).where(User.id == user_id , User.role == UserRole.Worker))
        
        result = self._db.execute(query)
        
        return result.scalar_one_or_none() is not None
    
    def is_employer(self  , user_id : int) -> bool:
        
        query = (select(User).where(User.id == user_id , User.role == UserRole.Employer))
        
        result = self._db.execute(query)
        
        return result.scalar_one_or_none() is not None
    
    
    def mark_verified(self , user_id : int) -> None:
        self.update(user_id, is_verified = True)
        logger.debug(f"User marked verified | user_id={user_id}")
        
    
    
    def deactivate(self, user_id: int) -> None:
        """Soft delete — deactivates account without deleting data"""
        self.update(user_id, is_active=False)
        logger.info(f"User deactivated | user_id={user_id}")

    def reactivate(self, user_id: int) -> None:
        self.update(user_id, is_active=True)
        logger.info(f"User reactivated | user_id={user_id}")
    
    
    
        
        
        
    
    