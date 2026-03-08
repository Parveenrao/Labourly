from sqlalchemy.orm import Session
from loguru import logger

from app.repositories.Rating_Repo import RatingRepository
from app.repositories.Worker_Repo import WorkerRepository
from app.repositories.Employer_Repo import EmployerRepository
from app.repositories.Job_Repo import JobRepository
from app.repositories.User_Repo import UserRepository
from app.services.Notification_Service import NotificationService
from app.schemas.Rating import RatingCreate, RatingResponse, RatingSummary
from app.utils.constants import UserRole, JobStatus
from app.utils.exception import (
    AlreadyRatedException,
    CannotRateWithoutJobCompletion,
    JobNotFoundException,
    WorkerNotFoundException,
    EmployerNotFoundException,
)


class RatingService:
    def __init__(self , db : Session):
        self.db = db
        self.rating_repo = RatingRepository(db)
        self.worker_repo = WorkerRepository(db)
        self.employer_repo = EmployerRepository(db)
        self.job_repo = JobRepository(db)
        self.user_repo = UserRepository(db)
        self.notification_service = NotificationService(db)
        
    
    def submit_rating(self, user_id : int , role : str , data : RatingCreate) -> RatingResponse:
        
        # validate job exist and competed 
        
        job = self.job_repo.get_by_id(user_id)
        
        if not job:
            raise JobNotFoundException(data.jod_id)
        
        if job.status != JobStatus.COMPLETED:
            raise CannotRateWithoutJobCompletion()
        
        # check already rated 
        
        if self.rating_repo.user_already_rated(data.job_id , user_id):
            raise AlreadyRatedException()
        
        
        if role == UserRole.EMPLOYER:
            # Employer rates worker
            application = self.job_repo.get_hired_application(data.job_id)
            if not application:
                raise WorkerNotFoundException()
        
            rating = self.rating_repo.create_rating(
                job_id=data.job_id,
                rated_by_user_id=user_id,
                stars=data.stars,
                review=data.review,
                worker_id=  application.worker_id,
            )
        
    
             # Update worker stats + check badge
            self.worker_repo.update_stats(application.worker_id, data.stars)
        
            worker = self.worker_repo.get_by_id(application.worker_id)
        
            self.notification_service.notify_new_rating(
                    worker.user_id, data.stars, data.job_id
                 )

        else:
            # Worker rates employer
            employer = self.employer_repo.get_by_user_id(job.employer_id)
            if not employer:
                raise EmployerNotFoundException()

            rating = self.rating_repo.create_rating(
                job_id=data.job_id,
                rated_by_user_id=user_id,
                stars=data.stars,
                review=data.review,
                employer_id=employer.id,
            )

            self.employer_repo.update_ratings(employer.id, data.stars)
            self.notification_service.notify_new_rating(
                employer.user_id, data.stars, data.job_id
            )

        logger.info(f"Rating submitted | job_id={data.job_id} stars={data.stars} by role={role}")
        return RatingResponse.model_validate(rating)

    def get_worker_summary(self, worker_id: int) -> RatingSummary:
        worker = self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)

        summary = self.rating_repo.get_worker_summary(worker_id)
        ratings, _ = self.rating_repo.get_by_worker(worker_id, limit=5)

        return RatingSummary(
            **summary,
            recent_ratings=[],
        )

    def get_employer_summary(self, employer_id: int) -> RatingSummary:
        employer = self.employer_repo.get_by_id(employer_id)
        if not employer:
            raise EmployerNotFoundException(employer_id)

        summary = self.rating_repo.get_employer_summary(employer_id)
        return RatingSummary(**summary, recent_ratings=[])    
        
        