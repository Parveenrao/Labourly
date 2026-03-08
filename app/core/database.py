from sqlalchemy import func , Text ,create_engine , DateTime , text
from sqlalchemy.orm import DeclarativeBase , mapped_column , Mapped , Session , sessionmaker
from datetime import datetime
from loguru import logger
from app.core.config import settings
from typing import Generator

#-----------------Engine-------------------------------

engine = create_engine(
           settings.DATABASE_URL,
           echo = settings.DEBUG,
           pool_pre_ping=True,
           pool_size=settings.DB_POOL_SIZE,
           max_overflow=settings.DB_MAX_OVERFLOW,
           pool_timeout=30,
           pool_recycle=1800,
)

# ─── Session Factory ────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ─── Base ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass



# ─── Timestamp Mixin ───────────────────────────────────
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    
# ─── DB Dependency (FastAPI) ───────────────────────────
def get_db() -> Generator[Session , None , None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        

# ─── Health Check ──────────────────────────────────────
def check_db_connection() -> bool:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection healthy")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ─── Create / Drop (tests only) ────────────────────────
def create_all_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created")


def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")            