from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.Auth_Services import AuthService
from app.schemas.Auth import SendOTPRequest, VerifyOTPRequest, RefereshToken, TokenResponse, OTPResponse
from app.schemas.Common import APIResponse, SuccessResponse

router = APIRouter()

# send otp 

@router.post("/send-otp" , response_model= APIResponse[OTPResponse])

def send_otp(data : SendOTPRequest , db : Session = Depends(get_db)):
    
    result = AuthService(db).send_otp(data.phone , data.role)
    
    return APIResponse(message="OTP Sent Successfully" )


# verify otp

@router.post("/verify-otp", response_model=APIResponse[TokenResponse])

def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    tokens = AuthService(db).verify_otp(
        phone=data.phone,
        otp=data.OTP,
        role=data.role
    )

    return APIResponse(
        message="Login successful",
        data=tokens
    )
    
# Refersh token


@router.post("/refresh-token", response_model=APIResponse[TokenResponse])
def refresh_token(
    data: RefereshToken,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    tokens = auth_service.refresh_token(data.referesh_token)

    return APIResponse(
        message="Token refreshed",
        data=tokens
    )    
    
    
# ─── Logout (client side — just a convention endpoint) ───────────

@router.post("/logout", response_model=SuccessResponse)

def logout(
    current_user: dict = Depends(get_current_user),
):
    # JWT is stateless — actual logout handled on client by deleting token
    # This endpoint exists so frontend has a clean logout call
    return SuccessResponse(message="Logged out successfully")


# ─── Me (get current user info from token) ───────────────────────
@router.get("/me", response_model=APIResponse[dict])
def me(
    current_user: dict = Depends(get_current_user),
):
    return APIResponse(data={
        "user_id": current_user.get("sub"),
        "role": current_user.get("role"),
        "phone": current_user.get("phone"),
    })
    
    