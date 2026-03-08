from sqlalchemy.orm import mapped_column , Mapped , relationship
from sqlalchemy import Integer , Float , Boolean , String 
from sqlalchemy import Enum as SQLEnum
from app.utils.constants import UserRole
from app.core.database import Base , TimestampMixin
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Worker import Worker
    from app.models.Employer import Employer


class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key= True , nullable=False , autoincrement= True)
    phone : Mapped[str] = mapped_column(String(15) , nullable = False , unique = True , index=True)
    role : Mapped[UserRole] = mapped_column(SQLEnum(UserRole , name="user_role" ) , nullable=False)
    is_active: Mapped[bool] = mapped_column( Boolean, server_default="true" ,nullable=False )
    is_verified: Mapped[bool] = mapped_column( Boolean, server_default="false" ,nullable=False )
    
    # Relationship 
    worker_profile: Mapped["Worker"] = relationship("Worker", back_populates="user", uselist=False)        # uselist = False -> one to one
    employer_profile: Mapped["Employer"] = relationship("Employer", back_populates="user", uselist=False)  # basically uslist return list of python   sql assume one to many so it false mean one to one
    
    
    def __repr__(self) -> str:
        return f"<User id={self.id} role={self.role}>"