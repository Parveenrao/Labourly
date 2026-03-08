import redis 
from loguru import logger
from  app.core.config import settings

# ----------------- Redis client  ---------------------------

# Separate Redis dbs for otp and cache 

otp_redis = redis.Redis.from_url(
           url= settings.REDIS_URL,
           db = settings.REDIS_OTP_DB,
            encoding="utf-8",
            decode_responses=True,
)


cache_redis = redis.Redis.from_url(
    settings.REDIS_URL,
    db=settings.REDIS_CACHE_DB,
    encoding="utf-8",
    decode_responses=True,
)

class OTPRedis:
    
    OTP_KEY = "otp:{phone}"
    ATTMEPTS_KEY = "opt_attempts:{phone}"
    COOLDOWN_KEY = "otp_cooldown:{phone}"
    
    
    @staticmethod
    def save_otp(phone : str , otp:str) -> None:
        
        # Save otp with expiry 
        
        key = OTPRedis.OTP_KEY.format(phone = phone)
        
        otp_redis.setex(key , settings.OTP_EXPIRE_MINUTES * 60 , otp)
        
        logger.debug(f"OTP saved for {phone} | expire in {settings.OTP_EXPIRE_MINUTES}")
        
    @staticmethod
    def get_otp(phone : str) -> str | None:
        
        key = OTPRedis.OTP_KEY.format(phone = phone)
        
        return otp_redis.get(key)    
    
    @staticmethod
    def delete_otp(phone : str) -> None:
        
        # Delete opt after verification 
        
        key = OTPRedis.OTP_KEY.format(phone = phone)
        
        otp_redis.delete(key)
        
        logger.debug(f"OTP deleted for {phone} after successful verification")
        
    @staticmethod
    def increment_attempts( phone : str) -> int:
        
        # track wrong opt 
        
        key = OTPRedis.ATTMEPTS_KEY.format(phone = phone)
        
        attempts = otp_redis.incr(key)
        
        # expire counter after otp expire 
        
        otp_redis.expire(key , settings.OTP_EXPIRE_MINUTES * 60)
        
        logger.warning(f"Wrong OTP attempt {attempts}/{settings.OTP_MAX_ATTEMPTS} for {phone}")
        return attempts
    
    @staticmethod
    def get_attempts(phone : str) -> int:      
        
        
        # get current wrong attempts 
        
        key = OTPRedis.ATTMEPTS_KEY.format(phone= phone)
        
        val = otp_redis.get(key)
        
        return int(val) if val else 0
    
    @staticmethod
    def clear_attempts(phone : str) -> None:
        
        "Clear attempts afer successful verification "
        
        key = OTPRedis.ATTMEPTS_KEY.format(phone = phone)
        
        otp_redis.delete(key)
        
    @staticmethod
    def set_cooldown(phone : str) -> int:   
        
        # set otp cooldown to avoid spam 
        
        key = OTPRedis.COOLDOWN_KEY.format(phone = phone)
        
        otp_redis.setex(key , settings.OTP_RESEND_COOLDOWN_SECONDS , "1")
        
        logger.debug(f"OTP cooldown set for {phone} | {settings.OTP_RESEND_COOLDOWN_SECONDS}s")
        
    @staticmethod
    def is_on_cooldown_period(phone : str) -> bool:         
        
        key = OTPRedis.COOLDOWN_KEY.format(phone = phone)
        
        return otp_redis.exists(key) > 0
    
    @staticmethod
    def get_cooldown_remaining(phone : str) -> int:              
        
        # get remaining cooldown seconds 
        
        key = OTPRedis.COOLDOWN_KEY.format(phone = phone)
        
        otp_redis.ttl(key)
        
        
    
             
           
        
#--------------------- Health Check -------------------------------------------
def check_redis_connection() -> bool:
    try:
        otp_redis.ping()
        logger.info("Redis connection healthy")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False