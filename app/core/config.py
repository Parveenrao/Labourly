from  pydantic_settings import BaseSettings , SettingsConfigDict
from functools import lru_cache
from typing import List

# All Env variables via pydantic-setting

class Settings(BaseSettings):
    
    APP_NAME : str = "Labourly"
    APP_ENV : str  = "development"
    DEBUG : bool  = True
    API_V1_PREFIX : str = "/api/v1"
    ALLOWED_HOST : List[str] = ["*"]
    
    #---- DATABASE ------------------------------
    
    DATABASE_URL  : str    
    DB_POOL_SIZE  : int    =  10  # how many connection sqlalchemy open when user hit db 
    DB_MAX_OVERFLOW  : int =  50  # Max pooling connection = 50 (10 Permanent + 50 Temoporary -> what if 1000 user will come (System Desing))
    
    
    #----- REDIS----------------------------------------------------------------
     
    REDIS_URL: str                               # Redis have 16 db 
    REDIS_OTP_DB: int = 1                        # Otp in db1
    REDIS_CACHE_DB: int = 2                      # otp in db2
    
    #------- JWT -----------------------------------------------------------------
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    #------- OTP --------------------------------------------------------------------
    
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    
    
    
    # ─── SMS Provider ────────────────────────────────────────────
    SMS_PROVIDER: str = "MOCK"          # MOCK | MSG91 | FAST2SMS
    MSG91_API_KEY: str = ""
    MSG91_SENDER_ID: str = "NAKKA"
    FAST2SMS_API_KEY: str = ""
    
    
    
    # ─── File Storage (local for now, S3 later) ──────────────────
    LOCAL_UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    
    #----- Geolocation -----------------------------------------------------
    DEFAULT_SEARCH_RADIUS_KM: int = 10
    MAX_SEARCH_RADIUS_KM: int = 50
    
    
    # ----- Ratings / Badges -----------------------------------------------
    TRUSTED_WORKER_MIN_JOBS: int = 10
    TRUSTED_WORKER_MIN_RATING: float = 4.0
    
    
    # ---- Chat / WebSocket ---------------------------------------------------
    WS_MAX_CONNECTIONS_PER_USER: int = 5
    WS_MESSAGE_MAX_LENGTH: int = 1000
    
    # --------------------- Logging -------------------------------------------------------------
    LOG_LEVEL: str = "DEBUG"
    LOG_RETENTION_DAYS: int = 30
    LOG_ERROR_RETENTION_DAYS: int = 90
    
    
    
    
    # ---- Security -------------------------------
    CORS_ORIGINS: List[str] = ["*"]
    
    
    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True
             )
        
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"
    
    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024    
    


@lru_cache                                # lru_cache = instead of open db session for every new request , we precompute db
def get_settings() -> Settings:           # if 1000 request will come , db(session) will open for once
    return Settings()  



settings = get_settings()