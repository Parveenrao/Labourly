from pydantic import BaseModel , field_validator
from app.utils.Helpers import format_phone , is_valid_indian_phone
from app.utils.constants import UserRole


# ------------- Request Schema---------------------------

class  SendOTPRequest(BaseModel):
    phone : str
    role : str  # worker | employer 
    
    
    @field_validator("phone")
    def validate_phone(cls , v):
        formatted = format_phone(v)
        
        if not is_valid_indian_phone(formatted):
            raise ValueError("Invalid mobile phone number")
        
        return formatted
    
    @field_validator("role")
    def validate_role(cls , v):
        if v not in [UserRole.WORKER  , UserRole.EMPLOYER]:
            raise ValueError("Role must be worker or employer")
        
        return v

class VerifyOTPRequest(BaseModel):
    phone : str
    OTP : str
    role : str
    
    @ field_validator("phone")
    def validate_phone(cls , v):
        return format_phone(v) 
    
    @field_validator("OTP")
    def validate_otp(v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be 6 digit") 
        
        return v
    
    @field_validator("role")
    def validate_role(cls , v):
        if v not in [UserRole.WORKER  , UserRole.EMPLOYER]:
            raise ValueError("Role must be worker or employer")
        
        return v

class RefereshToken(BaseModel):
    referesh_token :str
    
# ------------- Response Schema ------------------------------------------------

class OTPResponse(BaseModel):
    phone : str       
    message : str = "OTP sent successfully"
    expires_in_minutes : int = 10
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    is_new_user: bool   # True = first time login, frontend shows registration form              
    

class TokenPayload(BaseModel):
    sub: int
    role: str
    exp: int        