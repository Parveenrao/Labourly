from sqlalchemy.orm import Session
from loguru import logger

from app.repositories.Notification_Repo import NotificationRepository
from app.schemas.Notifications import NotificationListResponse, NotificationResponse, UnreadCountResponse
from app.utils.constants import NotificationType
from app.utils.Helpers import get_pagination_offset
from app.core.config import settings


class NotificationService:
    
    def __init__(self  ,db : Session):
        self.db = db 
        self.notification_repo = NotificationRepository(db)
    
    
    # get notifications 
    
    def get_notifications(self , user_id : int , page : int , page_size : int = 20) -> NotificationListResponse:
        
        offset = get_pagination_offset(page , page_size)
        
        notifications , total = self.notification_repo.get_notification(user_id ,  offset=offset , limit = page_size)
        
        unread_count = self.notification_repo.get_unread_count(user_id)
        total_pages = -(-total // page_size)
        
        
        return NotificationListResponse(
            notifications=[NotificationResponse.model_validate(n) for n in notifications],
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    
    def get_unread_count(self, user_id : int) -> UnreadCountResponse:
        
        count = self.notification_repo.get_unread_count(user_id)
        
        return UnreadCountResponse(unread_count=count)
    
    def mark_as_read(self, notification_id : int , user_id : int) -> bool:
        
        return self.notification_repo.mark_as_read(notification_id , user_id)
    
    def mark_many_as_read(self , notification_id : int , user_id : int) -> bool: 
        
        return self.notification_repo.mark_many_as_read(notification_id , user_id)
    
    def mark_all_as_read(self, user_id: int) -> int:
        return self.notification_repo.mark_all_as_read(user_id)
    
    def notify_new_job_nearby(self, worker_user_id : int , job_id : int , job_title :int) -> None:
        
        self.notification_repo.create_notification(user_id=worker_user_id,
            title="New Job Nearby!",
            body=f"A new {job_title} job is available near you",
            data={"type": NotificationType.NEW_JOB_NEARBY, "job_id": job_id},
        )
    
    def notify_application_received(self, employer_user_id: int, worker_name: str, job_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=employer_user_id,
            title="New Application!",
            body=f"{worker_name} applied to your job",
            data={"type": NotificationType.APPLICATION_RECEIVED, "job_id": job_id},
        )
    
    
    def notify_hired(self, worker_user_id: int, job_title: str, job_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=worker_user_id,
            title="You got hired!",
            body=f"You were hired for {job_title}",
            data={"type": NotificationType.APPLICATION_HIRED, "job_id": job_id},
        )

    def notify_rejected(self, worker_user_id: int, job_title: str, job_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=worker_user_id,
            title="Application Update",
            body=f"Your application for {job_title} was not selected",
            data={"type": NotificationType.APPLICATION_REJECTED, "job_id": job_id},
        )
        
        
    def notify_job_completed(self, user_id: int, job_title: str, job_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=user_id,
            title="Job Completed!",
            body=f"{job_title} has been marked as completed. Please leave a rating.",
            data={"type": NotificationType.JOB_COMPLETED, "job_id": job_id},
        )

    def notify_new_rating(self, user_id: int, stars: float, job_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=user_id,
            title="New Rating!",
            body=f"You received a {stars}★ rating",
            data={"type": NotificationType.NEW_RATING, "job_id": job_id},
        )

    def notify_new_message(self, user_id: int, sender_name: str, room_id: int) -> None:
        self.notification_repo.create_notification(
            user_id=user_id,
            title=f"New message from {sender_name}",
            body="Tap to view your conversation",
            data={"type": NotificationType.NEW_MESSAGE, "room_id": room_id},
        )
    