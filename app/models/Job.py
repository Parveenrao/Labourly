from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin
from app.utils.constants import JobStatus, JobType, JobUrgency

if TYPE_CHECKING:
    from app.models.Employer import Employer
    from app.models.Job_Application import JobApplication
    from app.models.Rating import Rating


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    # ---------------------- Primary Key --------------------------------------------
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # --------------------- Foreign Key ------------------------------------------
    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employers.id", ondelete="CASCADE"),
        nullable=False
    )

    # --------------------------- Core Info -----------------------------------------------
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    skill_required: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    workers_needed: Mapped[int] = mapped_column(
        Integer,
        server_default="1",
        nullable=False
    )

    #-------------------------------------- Job Attributes ----------------------------------------
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type_enum"),
        nullable=False
    )

    urgency: Mapped[JobUrgency] = mapped_column(
        Enum(JobUrgency, name="job_urgency_enum"),
        nullable=False
    )

    # -------------------------------------------- Location ----------------------------------------------
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    # ----------------------------------------------- Status ----------------------------------------------
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum"),
        nullable=False,
        index=True
    )

    # ----------------------------------------------------- Relationships -------------------------------------------
    employer: Mapped["Employer"] = relationship(
        "Employer",
        back_populates="jobs"
    )

    applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="job"
    )

    ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="job"
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} status={self.status}>"