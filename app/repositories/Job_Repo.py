from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Job import Job
from app.models.Job_Application import JobApplication
from app.utils.constants import JobStatus, ApplicationStatus

class JobRepository(BaseRepository[Job]):
    def __init__(self , db : Session):
        super().__init__(Job , db)
        
        
    # Get jon with employer 
    
    def get_job_with_employer(self , job_id :int) -> None:
        
        # Fetch job + employer 
        
        result = self._db.execute(select(Job).options(joinedload(Job.employer)).where(Job.id == job_id))
        
        return result.scalar_one_or_none()
    
    # Get open jobs by skills
    
    def get_job_Open_by_skills(self, skill :str , offset: int , limit : int) -> Tuple[List[Job] , int]:
        
        # Return jobs filter by skills and open 
        
        filters = [Job.skill_required == skill,
                   Job.status == JobStatus.OPEN]
        
        base_query = (select(Job).where(*filters))
        
        count_query = (select(func.count(Job.id)).where(*filters))
        
        result = self._db.execute(base_query.order_by(Job.created_at.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return list(result.scalars().all()), count.scalar_one()
        
        
    # Get Neaby open jobs 
    
    def get_job_nearby(self, skill :str , city : str , offset: int , limit : int) -> Tuple[List[Job] , int]:
        
        filters = [Job.skill_required == skill,
                   Job.city == city,
                   Job.status == JobStatus.OPEN]
        
        
        base_query = (select(Job).where(*filters))
        
        count_query = (select(func.count(Job.id)).where(*filters))
        
        result = self._db.execute(base_query.order_by(Job.created_at.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return list(result.scalars().all()), count.scalar_one()
    
    # Get jobs by employer 
    
    def get_job_employer(self , employer_id : int , offset : int = 0 , limit : int = 20) -> Tuple[List[int] , int]:
        
        # Return all job posted by an employer 
        
        return self.get_paginated(field="employer_id" , value=employer_id , offset=offset , limit=limit)
    
    
    # Update job status
    
    def update_job_status(self , job_id : int , status : JobStatus) -> Optional[Job]:
        
        updated = self.update(job_id, status = status)
        
        logger.info(f"Job status updated | JOb {job_id} | status {status}")
        
        return updated
    
    # Check is worker already applied to this job 
    
    def get_application(self , job_id : int , worker_id : int) -> Optional[JobApplication]:
        
        filters = [
                    JobApplication.job_id == job_id, 
                    JobApplication.worker_id == worker_id]
        
        result = self._db.execute(select(JobApplication).where(and_(*filters)))
        
        return result.scalar_one_or_none()
    
    
    # Return all application of a job 
    
    def get_application_job(self , job_id : int , offset : int = 0 , limit : int = 20)-> Tuple[List[JobApplication] , int]:
        
        base_query = (select(JobApplication).where(JobApplication.job_id == job_id))
        
        count_query = (select(func.count(JobApplication.id)).where(JobApplication.job_id == job_id))
        
        result = self._db.execute(base_query.options(joinedload(JobApplication.worker)).order_by(JobApplication.created_at.desc())
                                  .offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return List(result.scalar_one_or_none() , count.scalar_one())
    
    # Returns all jobs a worker has applied to 
    
    def get_applications_by_worker(
        self,
        worker_id: int,
        offset: int = 0,
        limit: int = 20,
                          ) -> Tuple[List[JobApplication], int]:
       
        base_query = (
            select(JobApplication)
            .where(JobApplication.worker_id == worker_id)
        )
        count_query = (
            select(func.count(JobApplication.id))
            .where(JobApplication.worker_id == worker_id)
        )

        result = self._db.execute(
            base_query
            .options(joinedload(JobApplication.job))
            .order_by(JobApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count = self._db.execute(count_query)

        return List(result.scalars().all()), count.scalar_one()
    
    
    # Create application 
    
    def create_application(self , job_id : int , worker_id : int , cover_note : Optional[str] = None) -> JobApplication:
        
        application = JobApplication(
             
             job_id = job_id,
             worker_id = worker_id,
             cover_note = cover_note,
             status = ApplicationStatus.PENDING
        )
        
        self._db.add(application)
        self._db.commit()
        self._db.refresh(application)
        logger.info(f"Application created | job_id={job_id} worker_id={worker_id}")
        return application
    
    # update application status 
    
    def update_appication_status(self , application_id : int , status : ApplicationStatus) -> Optional[JobApplication]:
        
        application = self.update(application_id , status = status)
        
        if application:
            logger.info(
               f"Application status updated | "
               f"application_id={application_id} status={status}"
              )

        return application
    
    # Get hired 
    
    def get_hired_application(self , job_id : int) -> Optional[JobApplication]:
        
        # Return the hired application for job
        
        filters = [JobApplication.job_id == job_id , 
                   JobApplication.status == ApplicationStatus.HIRED]
        
        
        result = self._db.execute(select(JobApplication).where(*filters))
        
        return result.scalar_one_or_none()
    
    
    
    
    
        
        
        
    
            