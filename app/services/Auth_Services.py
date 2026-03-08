from sqlalchemy.orm import Session
from loguru import logger

from app.repositories.User_Repo import UserRepository
from app.services.OTP_Servive import OTPService
from app.core.security import (
    create_jwt_token,
    create_referesh_jwt_token,
    decode_refresh_token,
    decode_jwt_token,
    decode_access_token,
    create_token_payload
)
from app.schemas.Auth import TokenResponse, OTPResponse
from app.utils.constants import UserRole
from app.utils.exception import InvalidTokenException, UserNotFoundException

class AuthService:
    
    def __init__(self, db : Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_service = OTPService()
        
    def send_otp(self, phone : str , role : str) -> OTPResponse:
        
        self.otp_service.send_OTP(phone) 
        
        logger.info(f"OTP sent to {phone} | role : {role}")
        
        return OTPResponse(phone=phone,
                           expires_in_minutes=10)
    
    
    # Verify OTP & Login & Register 
    
    def verify_otp(self , phone :str , otp : str , role : str) -> TokenResponse:           
        
        self.otp_service.verify_OTP(phone , otp) 
        
        # Get user by phone 
        
        user = self.user_repo.get_by_phone(phone)
        
        is_new_user = False
        
        if not user:
            
            # First time login  , create 
            
            user = self.user_repo.Create(phone = phone,
                                         role = role ,
                                         is_active = True ,
                                         is_verified = True)
            
            is_new_user = True
            
            logger.info(f"New user Registerd | phone = {phone} | role = {role}")
            
        else:
            
            # if existing user , mark verified 
            
            self.user_repo.mark_verified(user.id) 
            
            logger.info(f"User logged in | phone={phone} role={role}")
            
        #--------------- Issue tokens -------------------------------- 
        
        payload = create_token_payload(user_id = user.id ,
                                       role = user.role,
                                       phone= user.phone)
        
        access_token = create_jwt_token(payload)
        refersh_token = create_referesh_jwt_token(payload)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refersh_token,
            role=user.role,
            is_new_user=is_new_user
        )
        
    #---------------------- Refresh Token -----------------------------------------
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise InvalidTokenException()

        
        user_id = int(payload.get("sub"))
        
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundException()

        new_payload = create_token_payload(
            user_id=user.id,
            role=user.role,
            phone=user.phone,
        )
        access_token = create_jwt_token(new_payload)
        new_refresh_token = create_referesh_jwt_token(new_payload)

        logger.info(f"Tokens refreshed for user id={user_id}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            role=user.role,
            is_new_user=False,
        )      
  
            
            