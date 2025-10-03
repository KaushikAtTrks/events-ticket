from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str = Field(..., alias="_id")
    role: UserRole = UserRole.USER
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    purchased_passes: List[str] = []
    otp_verified: bool = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class User(UserBase):
    id: str = Field(..., alias="_id")
    role: UserRole
    created_at: datetime
