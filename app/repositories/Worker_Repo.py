from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Worker import Worker
from app.models.User import User
from app.utils.constants import Availability

class WorkerRepository(BaseRepository[Worker]):
    def __init__(self , db : Session):
        super().__init__(Worker , db)
        
    
    # get by user_id 
    
    def get_by_user_id(self, user_id : int) -> Optional[Worker]:
        
        result = self._db.execute(select(Worker).where(Worker.id == user_id))
        
        return result.scalar_one_or_none()
    
    # Get by skills
    
    def get_by_skills(self, skills : str , offset : int = 0 , limit : int  = 20) -> Tuple[List[Worker]]:
        
        base_query = (select(Worker).where(Worker.skills.contains([skills])).where(Worker.availability == Availability.AVAILABLE))
        
        result = self._db.execute(base_query.order_by(Worker.avg_rating.desc()).offset(offset).limit(limit))
        
        count_query = (
            select(func.count(Worker.id))
            .where(Worker.skills.contains([skills]))
            .where(Worker.availability == Availability.AVAILABLE)
        )
        
        count = self._db.execute(count_query)
        
        return list(result.scalar_one_or_none() , count.scalar_one())
    
    
    
    def get_nearby(
        self,
        skill: str,
        city: str,
        offset: int = 0,
        limit: int = 20,
                    ) -> Tuple[List[Worker], int]:
        """Returns (workers, total_count) filtered by skill + city"""
        base_query = (
            select(Worker)
            .where(Worker.skills.contains([skill]))
            .where(Worker.city == city)
            .where(Worker.availability == Availability.AVAILABLE)
        )
        count_query = (
            select(func.count(Worker.id))
            .where(Worker.skills.contains([skill]))
            .where(Worker.city == city)
            .where(Worker.availability == Availability.AVAILABLE)
        )

        result = self._db.execute(
            base_query
            .order_by(Worker.avg_rating.desc())
            .offset(offset)
            .limit(limit)
        )
        count = self._db.execute(count_query)

        return list(result.scalars().all()), count.scalar_one()
    
    # Get worker by area 
    
    def get_by_area(
        self,
        city: str,
        area: Optional[str],
        offset: int = 0,
        limit: int = 20
            )  -> Tuple[List[Worker], int]:

        filters = [
            Worker.city == city,
            Worker.availability == Availability.AVAILABLE
            ]

        if area:
            filters.append(Worker.area == area)

        base_query = select(Worker).where(*filters)

        count_query = select(func.count(Worker.id)).where(*filters)

        result = self._db.execute(
           base_query
           .order_by(Worker.avg_rating.desc())
           .offset(offset)
           .limit(limit)
           )

        count = self._db.execute(count_query)

        return result.scalars().all(), count.scalar_one()
    
    
    def get_trusted(self ,  city : str  ,skills : Optional[str] = None ,  offset :int =0 , limit : int = 20) -> Tuple[List[Worker], int]:
        
        filters = [Worker.city == city , 
                   Worker.is_trusted == True , 
                   Worker.availability == Availability.AVAILABLE]
        
        if skills:
            filters.append(Worker.skills == skills)
            
        base_query = select(Worker).where(**filter)
        
        count_query = select(func.count(Worker.id)).where(**filters)
        
        result = self._db.execute(base_query.order_by(Worker.avg_rating.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return List(result.scalars().all() , count.scalar_one())
    
    
    def update_stats(self, worker_id: int, new_rating: float) -> None:
        worker = self.get_by_id(worker_id)
        if not worker:
           return

        if not 0 <= new_rating <= 5:
           raise ValueError("Rating must be between 0 and 5")

        total = worker.total_jobs + 1
        avg = ((worker.avg_rating * worker.total_jobs) + new_rating) / total
        avg = round(avg, 2)

        self.update(
        worker_id,
        total_jobs=total,
        avg_rating=avg,
       )

        logger.debug(
            f"Worker stats updated | id={worker_id} "
            f"total_jobs={total} avg_rating={avg}"
            )
    
    def award_trusted_badge(self, worker_id: int) -> None:
        self.update(worker_id, is_trusted=True)
        logger.info(f"Trusted badge awarded | worker_id={worker_id}")    
            
        
        
    

    
    
    
        
            
    
    