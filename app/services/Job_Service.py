from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.repositories.Job_Repo import JobRepository
from app.repositories.Worker_Repo import WorkerRepository
from app.repositories.Employer_Repo import EmployerRepository
from app.repositories.User_Repo import UserRepository
from app.services.Notification_Service import NotificationService
from app.services.Worker_Service import WorkerService
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobSummary, JobApplicationResponse
from app.schemas.Common import PaginatedResponse
from app.utils.constants import JobStatus, ApplicationStatus, UserRole
from app.utils.exception import (
    JobNotFoundException,
    JobAlreadyClosedException,
    AlreadyAppliedException,
    CannotApplyOwnJobPosting,
    WorkerNotFoundException,
    EmployerNotFoundException,
    UnauthorizedException,
)
from app.utils.Helpers import get_pagination_offset


class JobService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.worker_repo = WorkerRepository(db)
        self.employer_repo = EmployerRepository(db)
        self.user_repo = UserRepository(db)
        self.notification_service = NotificationService(db)
        self.worker_service = WorkerService(db)

    # ---------------- Post Job ------------------------------------------
    def post_job(self, user_id: int, data: JobCreate) -> JobResponse:
        employer = self.employer_repo.get_by_user_id(user_id)
        if not employer:
            raise EmployerNotFoundException()

        job = self.job_repo.create_application(
            employer_id=employer.id,
            title=data.title,
            description=data.description,
            skill_required=data.skill_required,
            workers_needed=data.workers_needed,
            job_type=data.job_type,
            urgency=data.urgency,
            city=data.city,
            area=data.area,
            latitude=data.latitude,
            longitude=data.longitude,
            status=JobStatus.OPEN,
        )

        self.employer_repo.increment_jobs_posted(employer.id)
        logger.info(f"Job posted | job_id={job.id} employer_id={employer.id}")
        return JobResponse.model_validate(self.job_repo.get_job_with_employer(job.id))

    # ─── Get Job ─────────────────────────────────────────────────
    def get_job(self, job_id: int) -> JobResponse:
        job = self.job_repo.get_job_employer(job_id)
        if not job:
            raise JobNotFoundException(job_id)
        return JobResponse.model_validate(job)

    # ─── Get Nearby Jobs ─────────────────────────────────────────
    def get_nearby_jobs(
        self, skill: str, city: str, page: int = 1, page_size: int = 20
                                                                      ) -> PaginatedResponse:
        offset = get_pagination_offset(page, page_size)
        jobs, total = self.job_repo.get_job_nearby(skill, city, offset=offset, limit=page_size)
        return PaginatedResponse(
            data=[JobSummary.model_validate(j) for j in jobs],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=-(-total // page_size),
        )

    # ─── Apply to Job ─────────────────────────────────────────────
    def apply_to_job(
        self, user_id: int, job_id: int, cover_note: str = None
                                                                    ) -> JobApplicationResponse:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundException(job_id)
        if job.status != JobStatus.OPEN:
            raise JobAlreadyClosedException()

        worker = self.worker_repo.get_by_user_id(user_id)
        if not worker:
            raise WorkerNotFoundException()

        # Cannot apply to own job
        employer = self.employer_repo.get_by_id(job.employer_id)
        if employer.user_id == user_id:
            raise CannotApplyOwnJobPosting()

        # Check already applied
        existing = self.job_repo.get_application(job_id, worker.id)
        if existing:
            raise AlreadyAppliedException()

        application = self.job_repo.create_application(job_id, worker.id, cover_note)

        # Notify employer
        self.notification_service.notify_application_received(
            employer.user_id, worker.name, job_id
        )

        logger.info(f"Worker applied | job_id={job_id} worker_id={worker.id}")
        return JobApplicationResponse.model_validate(application)

    # ─── Hire Worker ─────────────────────────────────────────────
    def hire_worker(
        self, user_id: int, job_id: int, application_id: int
    ) -> JobApplicationResponse:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundException(job_id)

        employer = self.employer_repo.get_by_user_id(user_id)
        if not employer or employer.id != job.employer_id:
            raise UnauthorizedException("You can only hire for your own jobs")

        application = self.job_repo.update_appication_status(
            application_id, ApplicationStatus.HIRED
        )
        
        self.job_repo.update_job_status(job_id, JobStatus.FILLED)

        # Notify worker
        worker = self.worker_repo.get_by_id(application.worker_id)
        
        self.notification_service.notify_hired(worker.user_id, job.title, job_id)

        logger.info(f"Worker hired | job_id={job_id} worker_id={worker.id}")
        return JobApplicationResponse.model_validate(application)

    # ─── Complete Job ─────────────────────────────────────────────
    def complete_job(self, user_id: int, job_id: int) -> JobResponse:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundException(job_id)

        employer = self.employer_repo.get_by_user_id(user_id)
        if not employer or employer.id != job.employer_id:
            raise UnauthorizedException("Only the employer can mark a job as complete")

        updated = self.job_repo.update_job_status(job_id, JobStatus.COMPLETED)

        # Notify both worker and employer to rate
        application = self.job_repo.get_hired_application(job_id)
        if application:
            worker = self.worker_repo.get_by_id(application.worker_id)
            self.notification_service.notify_job_completed(worker.user_id, job.title, job_id)
            self.notification_service.notify_job_completed(employer.user_id, job.title, job_id)
            # Check and award trusted badge to worker
            self.worker_service.check_and_award_badge(worker.id)

        logger.info(f"Job completed | job_id={job_id}")
        return JobResponse.model_validate(self.job_repo.get_job_with_employer(job_id))