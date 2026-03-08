from datetime import datetime , timedelta , timezone
from typing import Optional
from jose import jwt , JWTError
from passlib.context import CryptContext
from loguru import logger

from app.core.config import settings

pwd_context = CryptContext(schemes= ["bcrypt"] , deprecated = "auto")

# Password hashing 

def hash_passowrd(passowrd : str) -> str:
    return pwd_context.hash(passowrd)

# Verify password 

def verify_password(plain_password :str , hash_password : str) -> bool:
    return pwd_context.verify(plain_password , hash_passowrd)


#----- JWT Token-----------------------------------

def create_jwt_token(payload : dict , expire_delta : Optional[timedelta] = None) -> str:
    """ Create s short lived  that default (60 mins)
        Payload shoudl contain {sub : user_id , role : "worker" | "employer"}
    """
    data = payload.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    data.update({"exp" : expire , "type" : "access"})
    
    token  = jwt.encode(data , key= settings.JWT_SECRET_KEY , algorithm=[settings.JWT_ALGORITHM])
    
    
    logger.debug(f"Access token created for : {payload.get("sub")}")
    
    return token


# -------------- Refersh JWT Token--------------------


def create_referesh_jwt_token(payload : dict , expire_delta : Optional[timedelta] = None) -> str:
    """Creates a long-lived refresh token (default 30 days)
    Used to get a new access token without re-login 
    """
    data = payload.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    data.update({"exp" : expire , "type" : "refersh"})
    
    token  = jwt.encode(data , key= settings.JWT_SECRET_KEY , algorithm=[settings.JWT_ALGORITHM])
    
    
    logger.debug(f"Access token created for : {payload.get("sub")}")
    
    return token
   
#------------------- Decode JWt TOken --------------

def decode_jwt_token(token : str) -> Optional[dict]:
    
    """Decode and validate jwt token 
       Return a payload dict if valid  , None if invlaid of expire
    """
       
    try:
           
        payload = jwt.decode(token ,  key = settings.JWT_SECRET_KEY , algorithms=[settings.JWT_ALGORITHM])
        
        return payload
    
    except JWTError as e:
        logger.debug(f"JWT decode failed {e}")    
        
        return None
       
           
    
def decode_access_token(token : str) -> Optional[dict]:
    """ Decode and ensure that the token is access not refersh"""
    
    
        
    payload = decode_access_token(token)
        
    if  not payload or payload.get("type")  != "access":
        return None
        
    return payload  



def decode_refresh_token(token: str) -> Optional[dict]:
    """Decodes and ensures token is a refresh token (not access)"""
    payload = decode_jwt_token(token)
    if not payload or payload.get("type") != "refresh":
        return None
    return payload



# ─── Token Payload Helper ────────────────────────────────────────
def create_token_payload(user_id: int, role: str, phone: str) -> dict:
    """
    Builds the standard payload for both access and refresh tokens
    role: "worker" | "employer"
    """
    return {
        "sub": str(user_id),    # subject = user id
        "role": role,
        "phone": phone,
    }