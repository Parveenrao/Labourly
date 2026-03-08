from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm  import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.Notification_Service import NotificationService
from app.schemas.Notifications import NotificationListResponse, UnreadCountResponse, MarkAsReadRequest
from app.schemas.Common import APIResponse, SuccessResponse

router = APIRouter()


# Get Notifications 
@router.get("/", response_model=NotificationListResponse)

def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return NotificationService(db).get_notifications(user_id, page, page_size)


# Get Unread Count 
@router.get("/unread-count", response_model=APIResponse[UnreadCountResponse])
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    count = await NotificationService(db).get_unread_count(user_id)
    return APIResponse(data=count)


#  Mark as Read 
@router.patch("/read", response_model=SuccessResponse)

def mark_as_read(
    data: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    NotificationService(db).mark_many_as_read(data.notification_ids, user_id)
    return SuccessResponse(message="Notifications marked as read")


#  Mark All as Read 
@router.patch("/read-all", response_model=SuccessResponse)

def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    NotificationService(db).mark_all_as_read(user_id)
    return SuccessResponse(message="All notifications marked as read")