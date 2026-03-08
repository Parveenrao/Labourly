from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Rating import Rating


class RatingRepository(BaseRepository[Rating]):
    def __init__(self , db : Session):
        super().__init__(Rating , db)
        
        
    # Check if user already rated for this job 
    
    def user_already_rated(self , job_id : int , rated_by_used_id : int) -> bool:
        
        filters = [Rating.job_id == job_id , 
                   Rating.rated_by_user_id == rated_by_used_id]
        
        result = self._db.execute(select(Rating.id).where(and_(*filter)))
        
        return result.scalar_one_or_none() is not None
    
    # Create rating 
    
    def create_rating(self , job_id : int , rated_by_user_id :int , 
                       stars : float , review : Optional[str] = None , 
                       worker_id : Optional[int] = None ,
                       employer_id : Optional[int] = None ,) -> Rating:
        
        # worker_id is set when employer give rating to worker 
        # employer_id is set when worker give rating to employer
        
        rating = Rating(
            
            job_id = job_id , 
            rated_by_user_id  = rated_by_user_id , 
            stars = stars , 
            review = review , 
            worker_id = worker_id , 
            employer_id = employer_id
        )
        
        self._db.add(rating)
        self._db.commit()
        self._db.refresh(rating)
        logger.info(
            f"Rating created | job_id={job_id} stars={stars} "
            f"worker_id={worker_id} employer_id={employer_id}"
        )
        return rating
    
    
    # Get ratings of worker (pagination )
    
    def get_ratings_workser(self , worker_id : int , offset : int , limit : int) -> Tuple[List[Rating] , int]:
        
        base_query = (select(Rating).where(Rating.worker_id == worker_id))
        
        count_query = (select(func.count(Rating.id)).where(Rating.worker_id == worker_id))
        
        result = self._db.execute(base_query.order_by(Rating.created_at.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return List(result.scalar_one_or_none() , count.scalar_one())
    
    # Get ratings of employer (pagination )
    
    def get_ratings_workser(self , employer_id : int , offset : int , limit : int) -> Tuple[List[Rating] , int]:
        
        base_query = (select(Rating).where(Rating.employer_id == employer_id))
        
        count_query = (select(func.count(Rating.id)).where(Rating.employer_id == employer_id))
        
        result = self._db.execute(base_query.order_by(Rating.created_at.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return List(result.scalar_one_or_none() , count.scalar_one())
    
    
    def get_worker_summary(self, worker_id: int) -> dict:
        
        
        """Returns avg rating + star breakdown for a worker"""
        
        result = self.db.execute(
            select(
                func.count(Rating.id).label("total"),
                func.avg(Rating.stars).label("avg"),
                func.sum(func.cast(Rating.stars == 5, int)).label("five"),
                func.sum(func.cast(Rating.stars == 4, int)).label("four"),
                func.sum(func.cast(Rating.stars == 3, int)).label("three"),
                func.sum(func.cast(Rating.stars == 2, int)).label("two"),
                func.sum(func.cast(Rating.stars == 1, int)).label("one"),
            )
            .where(Rating.worker_id == worker_id)
        )
        row = result.one()
        return {
            "total_ratings": row.total or 0,
            "avg_rating": round(float(row.avg or 0), 2),
            "five_star": row.five or 0,
            "four_star": row.four or 0,
            "three_star": row.three or 0,
            "two_star": row.two or 0,
            "one_star": row.one or 0,
        }
    
    def get_employer_summary(self, employer_id: int) -> dict:
        
        """Returns avg rating + star breakdown for an employer"""
        
        result = self._db.execute(
            select(
                func.count(Rating.id).label("total"),
                func.avg(Rating.stars).label("avg"),
                func.sum(func.cast(Rating.stars == 5, int)).label("five"),
                func.sum(func.cast(Rating.stars == 4, int)).label("four"),
                func.sum(func.cast(Rating.stars == 3, int)).label("three"),
                func.sum(func.cast(Rating.stars == 2, int)).label("two"),
                func.sum(func.cast(Rating.stars == 1, int)).label("one"),
            )
            .where(Rating.employer_id == employer_id)
        )
        row = result.one()
        return {
            "total_ratings": row.total or 0,
            "avg_rating": round(float(row.avg or 0), 2),
            "five_star": row.five or 0,
            "four_star": row.four or 0,
            "three_star": row.three or 0,
            "two_star": row.two or 0,
            "one_star": row.one or 0,
        }
        
        
    # Get Rating by Job 
    
    def get_by_job(self, job_id: int) -> List[Rating]:
        
        """Returns all ratings for a specific job (both directions)"""
        
        result = self._db.execute(
            select(Rating)
            .where(Rating.job_id == job_id)
            .order_by(Rating.created_at.desc())
        )
        return list(result.scalars().all())    
