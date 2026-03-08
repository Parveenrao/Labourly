import re
import random
import string
from geopy.distance import geodesic
from loguru import logger
import secrets
from typing import Optional
from fastapi import HTTPException , status

import re

def format_phone(phone: str) -> str:
    phone = re.sub(r"\D", "", phone)

    if phone.startswith("91") and len(phone) == 12:
        return f"+{phone}"

    elif len(phone) == 10:
        return f"+91{phone}"

    else:
        raise ValueError("Invalid phone number length")

def is_valid_indian_phone(phone: str) -> bool:
    pattern = r'^\+91[6-9]\d{9}$'
    return bool(re.match(pattern, format_phone(phone)))




def generate_otp(length: int = 6) -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(length))        



from fastapi import HTTPException, status


def get_pagination_offset(page: int, page_size: int) -> int:
    """
    Convert page number to database offset.
    """

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Page must be greater than or equal to 1."
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Page size must be between 1 and 100."
        )

    return (page - 1) * page_size




import secrets
from fastapi import HTTPException, status


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}


def get_file_extension(filename: str) -> str:
    if "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="File must have an extension."
        )
    return filename.rsplit(".", 1)[-1].lower()


def build_upload_path(user_id: int, filename: str) -> str:
    ext = get_file_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported file type."
        )

    random_name = secrets.token_hex(8)  # 16-character secure string

    return f"uploads/users/{user_id}/{random_name}.{ext}"





# ---------------------- Raidus ------------------------------------------------

def _validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validates latitude and longitude ranges.
    Latitude:  -90 to 90
    Longitude: -180 to 180
    """
    return (
        isinstance(lat, (int, float)) and
        isinstance(lon, (int, float)) and
        -90 <= lat <= 90 and
        -180 <= lon <= 180
    )


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> Optional[float]:
    """
    Calculates geodesic distance in kilometers
    between two latitude/longitude coordinates.

    Returns:
        float: Distance in km (rounded to 2 decimals)
        None: If validation or calculation fails
    """
    try:
        if not _validate_coordinates(lat1, lon1):
            logger.error("Invalid worker coordinates")
            return None

        if not _validate_coordinates(lat2, lon2):
            logger.error("Invalid job coordinates")
            return None

        distance = geodesic((lat1, lon1), (lat2, lon2)).km
        return round(distance, 2)

    except Exception as e:
        logger.exception(f"Distance calculation failed: {e}")
        return None


def is_within_radius(
    worker_lat: float,
    worker_lon: float,
    job_lat: float,
    job_lon: float,
    radius_km: float
) -> bool:
    """
    Checks if a job location is within
    the worker's travel radius.

    Returns:
        True  -> Job is within radius
        False -> Outside radius or error occurred
    """
    if radius_km < 0:
        logger.error("Radius cannot be negative")
        return False

    distance = calculate_distance_km(
        worker_lat,
        worker_lon,
        job_lat,
        job_lon
    )

    if distance is None:
        return False

    return distance <= radius_km