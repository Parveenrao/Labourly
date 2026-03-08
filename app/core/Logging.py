import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""

    # ----------------------------------------
    # Remove default Loguru handler
    # ------------------------------------------
    logger.remove()

    # --------------------------------------
    # Ensure logs directory exists
    # --------------------------------------
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)

    # -----------------------------------------
    # Console Logging (for development)
    # -------------------------------------------
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # ---------------------------------------------
    # Application Logs (INFO and above)
    # Rotates daily and keeps limited history
    # --------------------------------------------
    logger.add(
        LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        level="INFO",
        rotation="00:00",
        retention=f"{settings.LOG_RETENTION_DAYS} days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
    )

    # --------------------------------------------
    # Error Logs (ERROR and above)
    # Stored separately for easier debugging
    # --------------------------------------------
    logger.add(
        LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
        level="ERROR",
        rotation="00:00",
        retention=f"{settings.LOG_ERROR_RETENTION_DAYS} days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
    )

    logger.info(
        "Logging initialized | ENV=%s | LEVEL=%s | DIR=%s",
        settings.APP_ENV,
        settings.LOG_LEVEL,
        LOG_DIR,
    )

