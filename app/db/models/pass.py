from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PassType(str, Enum):
    DAILY = "daily"
    SEASONAL = "seasonal"
    VIP = "vip"
    GROUP = "group"
    STUDENT = "student"

class PassBase(BaseModel):
    name: str
    type: PassType
    price: float
    validity_start: datetime
    validity_end: datetime
    max_entries: int = 1
    group_size: Optional[int] = None
    description: Optional[str] = None

class PassCreate(PassBase):
    created_by: str

class PassInDB(PassBase):
    id: str = Field(..., alias="_id")
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class PassUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    validity_end: Optional[datetime] = None
    max_entries: Optional[int] = None
    is_active: Optional[bool] = None

class Pass(PassBase):
    id: str = Field(..., alias="_id")
    created_by: str
    created_at: datetime
    is_active: bool
