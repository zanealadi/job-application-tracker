from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# valid statuses, only these are allowed
class ApplicationStatus(str, Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    PHONE_SCREEN = "phone screen"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


# USER SCHEMAS

# schema for creating a new user
class UserCreate(BaseModel):
    email: EmailStr # validates email format automatically
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

# schema for user data in responses
class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True # allows creating from SQLAlchemy models


# schema for login response
class Token(BaseModel):
    access_token: str
    token_type: str

# APPLICATION SCHEMAS

# schema for creating new application
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, description="Company name")
    position: str = Field(..., min_length=1, description="Name of job position")
    status: ApplicationStatus = ApplicationStatus.WISHLIST # will default to wishlist
    job_url: Optional[str] = Field(None, description="Link to job posting")
    notes: Optional[str] = Field(None, description="Your notes about this job")
    applied_date: Optional[datetime] = Field(None, description="When you applied")

# schema for updating an application
class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None

# schema for application in responses
class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    company: str
    position: str
    status: ApplicationStatus
    job_url: Optional[str]
    notes: Optional[str]
    applied_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# schema for list of applications
class ApplicationListResponse(BaseModel):
    count: int
    applications: list[ApplicationResponse]
    