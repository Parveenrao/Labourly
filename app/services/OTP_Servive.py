from app.utils.exception import OTPCollDownException , OTPExpiredExceptipn , OTPTooManyRequest , InvalidOTPException
from app.utils.Helpers import generate_otp
from loguru import logger
from app.core.redis import OTPRedis
from app.core.config import settings

class OTPService:
    
    def send_OTP(self, phone:str) -> str:   
        
        if OTPRedis.is_on_cooldown_period(phone):
            remaining = OTPRedis.get_cooldown_remaining(phone)
            raise OTPCollDownException(seconds=remaining)
        
    
        # Generat otp  and store otp 
    
        otp = generate_otp(settings.OTP_LENGTH)
    
        OTPRedis.save_otp(phone ,  otp)
        OTPRedis.set_cooldown(phone)
        
        # send otp 
        
        self._send(phone , otp)
        return otp
    
            
    def verify_OTP(self, phone : str , otp : str) -> bool:   
        
        # check max attempts 
        
        attemts = OTPRedis.get_attempts(phone)
        
        if attemts > settings.OTP_MAX_ATTEMPTS:
            raise OTPTooManyRequest()
        
        # Get stored otp 
        
        stored_otp = OTPRedis.get_otp(phone)
        
        if not stored_otp:
            raise OTPExpiredExceptipn()   
        
        # Verify   
        
        if stored_otp != otp:
            OTPRedis.increment_attempts(phone)
            raise InvalidOTPException() 
        
        # On success 
        
        OTPRedis.delete_otp(phone)
        OTPRedis.clear_attempts(phone)
        logger.info(f"OTP verified successfully for {phone}")
        return True
        
    
    def _send(self, phone: str, otp: str) -> None:
        
        # Send OTP via configured provider"""
        
        if settings.SMS_PROVIDER == "MOCK":
            # Development — just log it
            logger.info(f"[MOCK OTP] Phone: {phone} | OTP: {otp}")
            return

        if settings.SMS_PROVIDER == "MSG91":
            self._send_msg91(phone, otp)
        elif settings.SMS_PROVIDER == "FAST2SMS":
            self._send_fast2sms(phone, otp)

    def _send_msg91(self, phone: str, otp: str) -> None:
        # TODO: implement when ready for production
        pass

    async def _send_fast2sms(self, phone: str, otp: str) -> None:
        # TODO: implement when ready for production
        pass    
         