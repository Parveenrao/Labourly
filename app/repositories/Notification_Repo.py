from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from typing import List, Tuple
from loguru import logger

from app.repositories.Base_repo import BaseRepository
from app.models.Notification import Notification

class NotificationRepository(BaseRepository[Notification]):

    def __init__(self, db: Session):
        super().__init__(Notification, db)
        
        
        
    # Get notification 
    
    def get_notification(self , user_id , offset : int , limit : int) -> Tuple[List[Notification], int]:
        
        base_query =  (select(Notification).where(Notification.user_id == user_id))
        
        count_query = (select(func.count(Notification.id)).where(Notification.user_id == user_id))
        
        result = self._db.execute(base_query.order_by(Notification.created_at.desc()).offset(offset).limit(limit))
        
        count = self._db.execute(count_query)
        
        return List(result.scalar_one_or_none() , count.scalar_one())
    
    
    # Get unread notification for user 
    
    def get_unread_notifications(self , user_id : int , offset : int , limit : int) -> Tuple[List[Notification], int]:
        
        filters = [Notification.user_id == user_id ,
                   Notification.is_read == False]
        
        # Return only unread notification 
        
        base_query = (select(Notification).where(*filters))
        
        count_query = (select(func.count(Notification.id)).where(*filters))
        
        result = self._db.execute(base_query.order_by(Notification.created_at.desc()).offset(offset).limit(limit))
        
        notifications = result.scalars().all()

        total = self._db.execute(count_query).scalar_one()

        return notifications, total
    
    # Get count of unread notifications 
    
    
    def get_unread_count(self, user_id : int) -> int:      
        
        result = self._db.execute(func.count(Notification.id)).where(Notification.user_id == user_id , 
                                                                     Notification.is_read == False)
        
        return result.scalar_one()
    
    # Create Notification 
    
    def create_notification(self , user_id : int ,title : str , body : str , data : dict = {}) -> Notification:
        
        notifications  = Notification(user_id = user_id , 
                                      title = title,
                                      body = body ,
                                      data = data ,
                                      is_read = False)
        
        self._db.execute(notifications)
        
        self._db.commit()
        
        self._db.refresh(notifications)
        
        logger.debug(f"Notification created | user_id={user_id} title={title}")
        return notifications
        
        
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
     
        """Mark single notification as read — verifies ownership"""

        result = self._db.execute(
           update(Notification)
            .where(
               Notification.id == notification_id,
               Notification.user_id == user_id,
               Notification.is_read.is_(False)
             )
             .values(is_read=True)
    )

        self._db.flush()

        return result.rowcount > 0
    
    
    def mark_many_as_read(self, notification_ids: List[int], user_id: int) -> int:
       
        """Mark multiple notifications as read — verifies ownership"""
       
        result = self._db.execute(
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .where(Notification.user_id == user_id)  # ownership check
            .values(is_read=True)
        )
        self._db.flush()
        logger.debug(
            f"Notifications marked read | user_id={user_id} "
            f"count={result.rowcount}"
        )
        return result.rowcount

    def mark_all_as_read(self, user_id: int) -> int:
        
        """Mark all notifications as read for a user"""
        
        result = self._db.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
            .values(is_read=True)
        )
        
        self._db.flush()
        logger.info(f"All notifications marked read | user_id={user_id}")
        return result.rowcount
    
    
    def delete_all_for_user(self, user_id: int) -> int:
        
        """Delete all notifications for a user — used on account deletion"""
        
        from sqlalchemy import delete
        
        result = self._db.execute(
            delete(Notification).where(Notification.user_id == user_id)
        )
        logger.info(f"All notifications deleted | user_id={user_id}")
        return result.rowcount
