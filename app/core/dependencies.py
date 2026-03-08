from fastapi import Depends , Header
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from loguru import logger
from app.schemas.Auth import TokenPayload
from app.core.database import get_db

from app.core.security import decode_access_token

from app.utils.exception import InvalidTokenException , UnauthorizedException

# ---- HTTP Bearer Scheme  ------------------------------
bearer_scheme = HTTPBearer()   # this is security scheme used for extract token from authorization header 

# Get Db session 

def get_db_session(db : Session = Depends(get_db)) -> Session:
    return db

# Get current_user (Any current logged user )

def get_current_user(credentials : HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> TokenPayload:
    
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
    except Exception:  
        raise InvalidTokenException
    
    logger.debug(
          "Authenticated User",
          extra = {"user_id" : payload.get("sub") ,  "role" : payload.get("role")}
    )
    
    return payload


# get current worker 

def get_current_worker(current_user : dict = Depends(get_current_user)) -> TokenPayload:
    
    if current_user.role != "worker":
        logger.warning(
            f"Worker route accessed by role: {current_user.role}"
        )
        raise UnauthorizedException("Only workers can access this")

    return current_user

# get current employer

def get_current_employer(current_user : dict = Depends(get_current_user)) -> TokenPayload:
    
    if current_user.role != "employerr":
        logger.warning(
            f"Emloyer route accessed by role: {current_user.role}"
        )
        raise UnauthorizedException("Only employer can access this")

    return current_user


# ─── Get Current User ID (shortcut) ─────────────────────────────
# Usage in routes: user_id: int = Depends(get_current_user_id)


def get_current_user_id(
    current_user: TokenPayload = Depends(get_current_user),
) -> int:

    user_id = current_user.sub

    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    return int(user_id)