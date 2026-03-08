from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin
from app.utils.constants import ApplicationStatus

if TYPE_CHECKING:
    from app.models.Job_Application import JobApplication
    from app.models.Worker import Worker
    from app.models.Job import Job


class JobApplication(Base, TimestampMixin):
    __tablename__ = "job_applications"

    __table_args__ = (
        UniqueConstraint("job_id", "worker_id", name="uq_job_worker_application"),
    )

    # ─── Primary Key ─────────────────────────────────────────────
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ─── Foreign Keys ─────────────────────────────────────────────
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False
    )

    # ─── Application Status ───────────────────────────────────────
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status_enum"),
        server_default=ApplicationStatus.HIRED,
        nullable=False,
        index=True
    )

    # ─── Relationships ───────────────────────────────────────────
    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="applications"
    )

    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="applications"
    )

    def __repr__(self) -> str:
        return f"<JobApplication id={self.id} job_id={self.job_id} worker_id={self.worker_id} status={self.status}>"