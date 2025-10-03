from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DiscountBase(BaseModel):
    code: str
    percentage: float
    max_limit: Optional[float] = None
    assigned_to: Optional[str] = None  # staff_id if assigned to specific staff
    expiry: datetime

class DiscountCreate(DiscountBase):
    pass

class DiscountInDB(DiscountBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    times_used: int = 0

class DiscountUpdate(BaseModel):
    percentage: Optional[float] = None
    max_limit: Optional[float] = None
    assigned_to: Optional[str] = None
    expiry: Optional[datetime] = None
    is_active: Optional[bool] = None

class Discount(DiscountBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    is_active: bool
    times_used: int
