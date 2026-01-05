# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import SkillLevel, OAuthProvider


# User Registration [file:21]
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


# User Login [file:21]
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User Response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    skill_level: SkillLevel
    is_active: bool
    is_admin: bool
    oauth_provider: Optional[OAuthProvider]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# Token Response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# Token Payload
class TokenPayload(BaseModel):
    sub: int  # user_id
    exp: int
    type: str  # "access" or "refresh"


# User Update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    skill_level: Optional[SkillLevel] = None
