from typing import TYPE_CHECKING
from sqlalchemy import (
    Float,
    Integer,
    ForeignKey,
    Text,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.Job import Job
    from app.models.Worker import Worker
    from app.models.Employer import Employer


class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    rated_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=True
    )

    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employers.id", ondelete="CASCADE"),
        nullable=True
    )

    stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    review: Mapped[str] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("stars BETWEEN 1 AND 5", name="valid_stars"),
        CheckConstraint(
            "(worker_id IS NOT NULL AND employer_id IS NULL) OR "
            "(worker_id IS NULL AND employer_id IS NOT NULL)",
            name="valid_rating_target"
        ),
        UniqueConstraint(
            "job_id",
            "rated_by_user_id",
            name="uq_rating_per_job_per_user"
        ),
    )

    job: Mapped["Job"] = relationship("Job", back_populates="ratings")

    worker: Mapped["Worker"] = relationship(
        "Worker",
        foreign_keys=[worker_id],
        back_populates="ratings_received"
    )

    employer: Mapped["Employer"] = relationship(
        "Employer",
        foreign_keys=[employer_id],
        back_populates="ratings_received"
    )

    def __repr__(self) -> str:
        return f"<Rating id={self.id} stars={self.stars} job={self.job_id}>"