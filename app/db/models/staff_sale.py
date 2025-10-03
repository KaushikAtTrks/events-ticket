from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentMode(str, Enum):
    CASH = "cash"
    UPI = "upi"

class StaffSaleBase(BaseModel):
    staff_id: str
    booking_id: str
    discount_applied: float = 0
    payment_mode: PaymentMode

class StaffSaleCreate(StaffSaleBase):
    pass

class StaffSaleInDB(StaffSaleBase):
    id: str = Field(..., alias="_id")
    sale_time: datetime = Field(default_factory=datetime.utcnow)
    commission: Optional[float] = None

class StaffSale(StaffSaleBase):
    id: str = Field(..., alias="_id")
    sale_time: datetime
    commission: Optional[float]
