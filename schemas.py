from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

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

class ApplicationBase(BaseModel):
    company: str = Field(..., min_length=1, description="Company name")
    position: str = Field(..., min_length=1, description="Job title")
    status: str = Field(..., min_length=1, description="Status of application")

# schema for creating new application
class ApplicationCreate(ApplicationBase):
    pass # inherits everything from ApplicationBase

# schema for updating an application
class ApplicationUpdate(ApplicationBase):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None

# schema for application in responses
class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# schema for list of applications
class ApplicationListResponse(ApplicationBase):
    count: int
    application: list[ApplicationResponse]
    