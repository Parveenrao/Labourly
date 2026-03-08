from sqlalchemy import (String, Text, Float, Integer, Boolean, ForeignKey, JSON, Enum)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin
from app.utils.constants import Experience, Availability , Skill ,TravelDistance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.User import User
    from app.models.Job_Application import JobApplication
    from app.models.Rating import Rating



class Worker(Base, TimestampMixin):
    __tablename__ = "workers"

   
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

  
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True,    nullable=False) # unique  1 : 1 relation

    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    languages: Mapped[list] = mapped_column(
        JSON,
        server_default="[]"
    )

    skills: Mapped[Skill] = mapped_column(
        Enum(Skill , name = "user_skills"),
        nullable=False
    )

    experience: Mapped[Experience] = mapped_column(Enum(Experience, name="experience_level"),
        nullable=False
    )

    rates: Mapped[dict] = mapped_column(
        JSON,
        server_default="{}",
        nullable=False
    )

    
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    travel_distance_km: Mapped[TravelDistance] = mapped_column(
        Enum(TravelDistance, name = "travel_distance"),
        server_default="5",
        nullable=False
    )

  
    availability: Mapped[Availability] = mapped_column(
        Enum(Availability, name="availability_status"),
        nullable=False
    )

    work_photos: Mapped[list] = mapped_column(
        JSON,
        server_default="[]"
    )

   
    total_jobs: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        nullable=False
    )

    avg_rating: Mapped[float] = mapped_column(
        Float,
        server_default="0.0",
        nullable=False
    )

    is_trusted: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
        nullable=False
    )

   
    user: Mapped["User"] = relationship(
        "User",
        back_populates="worker_profile"
    )

    applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="worker"
    )

    ratings_received: Mapped[list["Rating"]] = relationship(
        "Rating",
        foreign_keys="Rating.worker_id",
        back_populates="worker"
    )

    def __repr__(self) -> str:
        return f"<Worker id={self.id} name={self.name}>"