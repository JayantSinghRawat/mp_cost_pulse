from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginStep1Response(BaseModel):
    """Response after password verification - requires OTP"""
    session_token: str
    message: str = "OTP sent to your email. Please verify to complete login."

class OTPVerify(BaseModel):
    """Schema for OTP verification"""
    session_token: str
    otp_code: str

