from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.User import User


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    data: Mapped[dict] = mapped_column(
        JSON,
        server_default="{}",
        nullable=False
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
        nullable=False
    )

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user={self.user_id} read={self.is_read}>"