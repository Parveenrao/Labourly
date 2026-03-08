from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.Job import Job
    from app.models.User import User


class ChatRoom(Base, TimestampMixin):
    __tablename__ = "chat_rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False
    )

    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employers.id", ondelete="CASCADE"),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
        nullable=False
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChatRoom id={self.id} worker={self.worker_id} employer={self.employer_id}>"


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    __table_args__ = (
        Index("ix_chat_room_created", "room_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    room_id: Mapped[int] = mapped_column(
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
        nullable=False
    )

    room: Mapped["ChatRoom"] = relationship(
        "ChatRoom",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} room={self.room_id} sender={self.sender_id}>"