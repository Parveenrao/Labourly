from sqlalchemy.orm import Session
from loguru import logger
from typing import Optional

from app.repositories.Worker_Repo import WorkerRepository
from app.repositories.User_Repo import UserRepository
from app.schemas.Worker import WorkerCreate, WorkerUpdate, WorkerResponse, WorkerSummary
from app.schemas.Common import PaginatedResponse
from app.utils.constants import Availability, Badge
from app.utils.exception import (
    WorkerNotFoundException,
    UserNotFoundException,
)
from app.core.config import settings
from app.utils.Helpers import get_pagination_offset


class WorkerService:
    
    def __init__(self , db : Session):
        self.db = db 
        self.worker_repo = WorkerRepository(db)
        self.user_repo = UserRepository(db)
        
    # Rgister Worker Profile 
    
    def register_worker(self , user_id: int , data:WorkerCreate) -> WorkerResponse:  
        
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException()
        
        # check existing worker 
        
        existing = self.worker_repo.get_by_id(user_id)  
        
        if existing:
            logger.warning(f"Worker profile already exists for user_id={user_id}")
            return WorkerResponse.model_validate(existing)
        
        
        worker = WorkerCreate(
            user_id=user_id,
            name=data.name,
            bio=data.bio,
            languages=data.languages,
            skills=data.skills,
            experience=data.experience,
            rates=data.rates,
            city=data.city,
            area=data.area,
            latitude=data.latitude,
            longitude=data.longitude,
            travel_distance_km=data.travel_distance_km,
            availability=Availability.AVAILABLE,
            work_photos=[],
            total_jobs=0,
            avg_rating=0.0,
            is_trusted=False,
                     )

        logger.info(f"Worker profile created | user_id={user_id} name={data.name}")
        return WorkerResponse.model_validate(worker)
    
     # Get worker profile 
   
    def get_worker_profile(self , worker_id :int) -> WorkerResponse:   
        
        worker = self.worker_repo.get_by_user_id(worker_id)
        
        if not worker:
            raise WorkerNotFoundException()
        
        return WorkerResponse.model_validate(worker)
    
    # Get profile by user_id 
    
    def get_profile_by_user_id(self , user_id : int) -> WorkerResponse:
        
        worker = self.worker_repo.get_by_user_id(user_id)
        
        if not worker:
            raise WorkerNotFoundException()
        
        return WorkerResponse.model_validate(worker)
    
    # update worker profile 
    
    def update_worker_profile(self, user_id : int , data : WorkerUpdate) -> WorkerResponse:   
        
        worker = self.worker_repo.get_by_user_id(user_id)
        
        if not worker:
            raise WorkerNotFoundException()
        
        #update only fileds that was sent actually
        updated_data = data.model_dump(exclude_unset=True)
        
        if not updated_data:
            return WorkerResponse.model_validate(worker)
        
        updated = self.worker_repo.update(worker.id , **updated_data)
        
        logger.info(f"Worker profile updated | worker_id={worker.id} fields={list(updated_data.keys())}")
        return WorkerResponse.model_validate(updated)
    
    
    # update availability of worker
    
    def update_availiability(self , user_id : int , availability : Availability) -> WorkerResponse:    
        
        worker = self.worker_repo.get_by_user_id(user_id)
        
        if not worker:
            raise WorkerNotFoundException()
        
        updated = self.worker_repo.update(worker.id, availability = availability)
        
        logger.info(
        f"Worker availability updated | worker_id={worker.id} status={availability}"
                )

        return WorkerResponse.model_validate(updated)
    
    # Search worker by skills 
    
    def search_worker(self , skills : str , page : int = 1 , page_size : int  = 20) -> PaginatedResponse:  
        
        offset  = get_pagination_offset(page , page_size)
        
        workers = self.worker_repo.get_by_skills(skills , offset = offset , limit=page_size)
        
        total = len(workers)
        
        
        return PaginatedResponse(
            data=[WorkerSummary.model_validate(w) for w in workers],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=-(-total // page_size),  # ceiling division
        )

    
    
    # --------------------- Get Nearby Workers -------------------------------------------------
    
    def get_nearby(
        self, skill: str, city: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse:
        offset = get_pagination_offset(page, page_size)
        workers = self.worker_repo.get_nearby(skill, city, offset=offset, limit=page_size)
        total = len(workers)

        return PaginatedResponse(
            data=[WorkerSummary.model_validate(w) for w in workers],
            page=page,
            page_size=page_size,
            total=total,
            total_pages = -(-total // page_size),
        )
        
    
    # Add work photos 
    
    def add_work_photots(self , user_id : int , photo_url : str) -> WorkerResponse:   
        
        worker = self.worker_repo.get_by_user_id(user_id)
        
        if not worker:
            raise WorkerNotFoundException()
        
        photos = worker.work_photos or []
        
        photos.append(photo_url)
        
        if photo_url not in photos:
            photos.append(photo_url)

        updated = self.worker_repo.update(
                   worker.id,
                   work_photos=photos
          )

        logger.info(f"Work photo added | worker_id={worker.id}")

        return WorkerResponse.model_validate(updated)
        
    
    # Remove work photos     
    
    def remove_work_photo(self, user_id: int, photo_url: str) -> WorkerResponse:
        worker = self.worker_repo.get_by_user_id(user_id)

        if not worker:
            raise WorkerNotFoundException()

        photos = worker.work_photos or []

      

        photos = [p for p in photos if p != photo_url]

        updated = self.worker_repo.update(worker.id, work_photos=photos)

        logger.info(f"Work photo removed | worker_id={worker.id}")

        return WorkerResponse.model_validate(updated)
    
    
    # Check Badge and update 
    
    def check_and_award_badge(self, worker_id: int) -> None:
       
        worker = self.worker_repo.get_by_id(worker_id)
        
        if not worker or worker.is_trusted:
            return

        if (
            worker.total_jobs >= settings.TRUSTED_WORKER_MIN_JOBS
            and worker.avg_rating >= settings.TRUSTED_WORKER_MIN_RATING  ):
                                                                       
            self.worker_repo.update(worker_id, is_trusted=True)
            logger.info(f"Trusted badge awarded to worker_id={worker_id}")

        

    
     
   
    
    
        
        
    
    