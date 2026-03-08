from fastapi import HTTPException , status

# --------------- Auth Exception-------------------------

class InvalidOTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail="Invalid OTP. Please try again later")

class OTPExpiredExceptipn(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail="OTP has expired. Please request a new OTP")

class OTPTooManyRequest(HTTPException):
    def __init___(self):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS , detail="Too many wrongs attempt. Please request a new otp")
                        

class OTPCollDownException(HTTPException):
    def __init__(self , seconds : int = 60):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS , detail=f"Please wait {seconds} before requesting new otp")
        

class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})   

class UnauthorizedException(HTTPException):
    def __inti__(self , detail : str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN , detail=detail)
        

# ---- User / Worker / Employer Exceptions -----------------------------------  

class UserNotFoundException(HTTPException):
    def __init__(self, identifier: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found{': ' + identifier if identifier else ''}"
        )

class UserAlreadyExistException(HTTPException):
    def __init__(self , phone : str = ""):
        super().__init__(status_code=status.HTTP_409_CONFLICT , detail=f"User with phone {phone} is already exist")
        
class WorkerNotFoundException(HTTPException):
    def __int__(self , worker_id : int = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND , detail=f"Worker not found{': id=' + str(worker_id) if worker_id else ''}")  
        
        
class EmployerNotFoundException(HTTPException):
    def __inti__(self , employer_id : int = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND ,detail=f"Employer not found{': id=' + str(employer_id) if employer_id else ''}")      
        
        
# --------------- Jobs Exception --------------------------------------

class JobNotFoundException(HTTPException):
    def __init__(self, job_id : int = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND , detail=f"Employer not found{': id=' + str(job_id) if job_id else ''}")      
        

class JobAlreadyClosedException(HTTPException):
    def __inti__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail="This job is already closed or filled") 

class AlreadyAppliedException(HTTPException):
    def __int__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT , detail="You have already applied to this job")    
        

class CannotApplyOwnJobPosting(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail="You cannot apply to your own job posting")   
        

#---------------- Rating Exceptions---------------------------------------------

class RatingNotFoundException(HTTPException):
    def __int__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND , detail="Rating not found")

class AlreadyRatedException(HTTPException):
    def __int__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT , detail="You have already rated this person for this job")
        
class CannotRateWithoutJobCompletion(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail="You can only rate this person after job is completed")
        
 
# ----------------- Chat Exception ---------------------------------------------

class ChatRoomNotFoundException(HTTPException):
    def __inti__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND , detail="Chat Room  Not Found") 


class ChatNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat is only allowed after a worker is hired"
        )


# -------------- File / Upload Exceptions ----------------------------------------
class InvalidFileTypeException(HTTPException):
    def __init__(self, allowed: str = "jpg, png, webp"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {allowed}"
        )

class FileTooLargeException(HTTPException):
    def __init__(self, max_mb: int = 5):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {max_mb}MB"
        )


# ---------------- Notification Exceptions ------------------------------------------
class NotificationNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )


# --------------------------- Generic Exceptions ------------------------------------
class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ServiceUnavailableException(HTTPException):
    def __init__(self, service: str = ""):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable{': ' + service if service else ''}"
        )
                                                      