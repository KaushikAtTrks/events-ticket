from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CASH = "cash"
    FAILED = "failed"

class BookingStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"

class GroupMember(BaseModel):
    name: str
    phone: str
    entry_status: bool = False

class BookingBase(BaseModel):
    user_id: str
    pass_id: str
    is_group: bool = False
    group_members: Optional[List[GroupMember]] = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    discount_applied: Optional[float] = None
    sold_by: Optional[str] = None  # staff_id or "online"

class BookingCreate(BookingBase):
    pass

class BookingInDB(BookingBase):
    id: str = Field(..., alias="_id")
    qr_code: str
    status: BookingStatus = BookingStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_id: Optional[str] = None
    amount_paid: float

class BookingUpdate(BaseModel):
    payment_status: Optional[PaymentStatus] = None
    status: Optional[BookingStatus] = None
    group_members: Optional[List[GroupMember]] = None

class Booking(BookingBase):
    id: str = Field(..., alias="_id")
    qr_code: str
    status: BookingStatus
    created_at: datetime
    payment_id: Optional[str]
    amount_paid: float
