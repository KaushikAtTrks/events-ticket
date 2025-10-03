from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...db.mongodb import MongoDB
from ...db.models.user import UserInDB
from ...db.models.staff_sale import StaffSaleCreate, StaffSale
from ...db.models.booking import BookingCreate, Booking
from ..endpoints.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/sell", response_model=Booking)
async def staff_sell_pass(
    booking: BookingCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    
    # Create booking
    booking_dict = booking.dict()
    booking_dict["sold_by"] = str(current_user.id)
    booking_dict["_id"] = ObjectId()
    
    # Get pass details
    pass_ = await db["passes"].find_one({"_id": ObjectId(booking.pass_id)})
    if not pass_:
        raise HTTPException(status_code=404, detail="Pass not found")
    
    # Calculate amount after discount
    amount = pass_["price"]
    if booking.discount_applied:
        # Verify staff's discount permission
        discount = await db["discounts"].find_one({
            "assigned_to": str(current_user.id),
            "is_active": True,
            "expiry": {"$gt": datetime.utcnow()}
        })
        if not discount or discount["percentage"] < booking.discount_applied:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized discount amount"
            )
        amount = amount * (1 - booking.discount_applied/100)
    
    booking_dict["amount_paid"] = amount
    
    # Create staff sale record
    staff_sale = StaffSaleCreate(
        staff_id=str(current_user.id),
        booking_id=str(booking_dict["_id"]),
        discount_applied=booking.discount_applied or 0,
        payment_mode=booking.payment_status
    )
    
    await db["staff_sales"].insert_one(staff_sale.dict())
    await db["bookings"].insert_one(booking_dict)
    
    return Booking(**booking_dict)

@router.get("/sales", response_model=List[StaffSale])
async def get_staff_sales(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    sales = await db["staff_sales"].find(
        {"staff_id": str(current_user.id)}
    ).to_list(None)
    
    return sales

@router.get("/active-discounts")
async def get_staff_discounts(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "staff":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    discounts = await db["discounts"].find({
        "assigned_to": str(current_user.id),
        "is_active": True,
        "expiry": {"$gt": datetime.utcnow()}
    }).to_list(None)
    
    return discounts
