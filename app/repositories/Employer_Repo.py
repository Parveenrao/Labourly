from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Employer import Employer


class EmployerRepository(BaseRepository[Employer]):
    def __init__(self , db : Session):
        super().__init__(self , Employer , db)
        
    
    # Get by user_id 
    
    def get_by_user_id(self , user_id : int) -> Optional[Employer]:
        
        result = self._db.execute(select(Employer).where(Employer.id == user_id))
        
        return result.scalar_one_or_none()
    
    # Get employer with jobs
    def get_with_jobs(self, employer_id : int) ->Optional[Employer]:
        
        result = self._db.execute(select(Employer).options(joinedload(Employer.jobs)).where(Employer.id == employer_id))
        
        return result.scalar_one_or_none()
    
    
    
    # Get Ratings of Employers 
    
    def get_by_ratings(self , employer_id : int) -> Optional[Employer]:
        
        # Fetch all employers with their ratings
        
        result = self._db.execute(select(Employer).options(joinedload(Employer.ratings_received)).where(Employer.id == employer_id))
        
        return result.scalar_one_or_none()
    
    # Search employer by city  
    
    def get_by_city(self , city : str , offset : int = 0 , limit :int = 20) -> Tuple[List[Employer] , int]:
        
        base_query = (select(Employer).where(Employer.city == city))
        
        count_query = (select(func.count(Employer.id)).where(Employer.city == city))
        
        result = self._db.execute(base_query.order_by(Employer.avg_rating.desc()).offset(offset).limit(limit)) 
        
        count = self._db.execute(count_query)
        
        return List(result.scalars().all() , count.scalar_one())   
    
    
    # Update  ratings 
    
    def update_ratings(self , employer_id : int , new_rating : float) -> None:
        
        employer = self.get_by_id(employer_id)
        
        if not employer:
            return None
        
        total_ratings = employer.total_jobs_posted
        
        if total_ratings == 0:
            avg = new_rating
        else:
            avg = ((employer.avg_rating * total_ratings) + new_rating) / (total_ratings + 1)
            
        
        self._db.update(employer_id, new_rating = round(avg , 2))
        
        logger.debug(
            f"Employer rating updated | id={employer_id} "
            f"avg_rating={avg:.2f}")
        
        # ─── Increment Jobs Posted ───────────────────────────────────
    def increment_jobs_posted(self, employer_id: int) -> None:
        """Called every time employer posts a new job"""
        employer = self.get_by_id(employer_id)
        if not employer:
            return
        self.update(
            employer_id,
            total_jobs_posted=employer.total_jobs_posted + 1
        )
        logger.debug(f"Jobs posted incremented | employer_id={employer_id}")
    
    
    
    