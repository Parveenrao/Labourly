from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:                              # Circular import error a loads b  and b loads a
    from app.models.User import User
    from app.models.Job import Job
    from app.models.Rating import Rating


class Employer(Base, TimestampMixin):
    __tablename__ = "employers"

    # ------------------- Primary Key ---------------------------------------
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # -------------------- One-to-One with User ---------------------------------------
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,   # Enforces true 1:1
        nullable=False
    )

    # --------------------------- Personal Info ---------------------------------------------
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    # ---------------------------------- Location --------------------------------------------
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

   
    total_jobs_posted: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        nullable=False
    )

    avg_rating: Mapped[float] = mapped_column(
        Float,
        server_default="0.0",
        nullable=False
    )

    # -------------------------------- Relationships -----------------------------------------
    user: Mapped["User"] = relationship(
        "User",
        back_populates="employer_profile"
    )

    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="employer"
    )

    ratings_received: Mapped[list["Rating"]] = relationship(
        "Rating",
        foreign_keys="Rating.employer_id",
        back_populates="employer"
    )

    def __repr__(self) -> str:
        return f"<Employer id={self.id} name={self.name}>"