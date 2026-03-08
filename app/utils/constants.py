from enum import Enum

# ------------ User Role ----------------------------

class UserRole(str , Enum):
    WORKER = "worker"
    EMPLOYER = 'employer'
    
# ----------------- Skills----------------------------

class Skill(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    CARPENTER = "carpenter"
    PAINTER = "painter"
    MASON = "mason"
    WELDER = "welder"
    DRIVER = "driver"
    COOK = "cook"
    CLEANER = "cleaner"
    HELPER = "helper"
    GARDENER = "gardener"
    SECURITY = "security"
    
# -------------------------- Job Status ------------------------

class JobStatus(str , Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILLED = "filled"
    COMPLETED = "completed"


# ----------------------------- Job Type --------------------------------------
class JobType(str, Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    
# -----------------------------Job Urgency --------------------------------------
class JobUrgency(str, Enum):
    TODAY = "today"
    THIS_WEEK = "this_week"
    FLEXIBLE = "flexible"
    
# -------------------------------- Application Status -------------------------------
class ApplicationStatus(str, Enum):
    PENDING = "pending"
    HIRED = "hired"
    REJECTED = "rejected"   
    

# ------------------------------------ Worker Availability ----------------------------
class Availability(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    ON_LEAVE = "on_leave"    
        
# ---------------------------------------- Experience ----------------------------------
class Experience(str, Enum):
    BEGINNER = "beginner"
    ONE_TO_TWO = "1_2_years"
    THREE_TO_FIVE = "3_5_years"
    FIVE_PLUS = "5_plus_years"        
    
# ---------------------------------------- Travel Distance  ----------------------------------
class TravelDistance(int, Enum):
    TWO_KM = 2
    FIVE_KM = 5
    TEN_KM = 10
    TWENTY_KM = 20
    ANY = 50
    
# --------------------------------------------- Badge --------------------------------------------
class Badge(str, Enum):
    TRUSTED_WORKER = "trusted_worker"
    TOP_RATED = "top_rated"


# ------------------------------------------------ Notification Type  -------------------------------
class NotificationType(str, Enum):
    NEW_JOB_NEARBY = "new_job_nearby"
    APPLICATION_RECEIVED = "application_received"
    APPLICATION_HIRED = "application_hired"
    APPLICATION_REJECTED = "application_rejected"
    JOB_COMPLETED = "job_completed"
    NEW_RATING = "new_rating"
    NEW_MESSAGE = "new_message"    
    
        