from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...db.mongodb import MongoDB
from ...db.models.booking import BookingCreate, BookingInDB, Booking, BookingUpdate
from ...db.models.user import UserInDB
from ..endpoints.auth import get_current_user
from ...services.qr_service import generate_qr_code
from bson import ObjectId
import qrcode
import base64
from io import BytesIO

router = APIRouter()

@router.post("/", response_model=Booking)
async def create_booking(
    booking: BookingCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = MongoDB.get_db()
    
    # Verify pass exists and is active
    pass_ = await db["passes"].find_one({"_id": ObjectId(booking.pass_id)})
    if not pass_ or not pass_["is_active"]:
        raise HTTPException(status_code=404, detail="Pass not found or inactive")
    
    # Calculate amount after discount
    amount = pass_["price"]
    if booking.discount_applied:
        amount = amount * (1 - booking.discount_applied/100)
    
    # Generate QR code
    booking_dict = booking.dict()
    booking_dict["_id"] = ObjectId()
    qr_data = f"{booking_dict['_id']}"
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")
    booking_dict["qr_code"] = base64.b64encode(buffered.getvalue()).decode()
    
    # Add amount paid
    booking_dict["amount_paid"] = amount
    
    await db["bookings"].insert_one(booking_dict)
    return Booking(**booking_dict)

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    db = MongoDB.get_db()
    booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user owns the booking or is staff/admin
    if (str(booking["user_id"]) != str(current_user.id) and 
        current_user.role not in ["staff", "admin"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return Booking(**booking)

@router.post("/{booking_id}/cancel", response_model=Booking)
async def cancel_booking(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    db = MongoDB.get_db()
    booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user owns the booking or is admin
    if (str(booking["user_id"]) != str(current_user.id) and 
        current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if booking can be cancelled
    if booking["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail="Only active bookings can be cancelled"
        )
    
    result = await db["bookings"].update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "cancelled"}}
    )
    
    booking["status"] = "cancelled"
    return Booking(**booking)

@router.get("/user/{user_id}", response_model=List[Booking])
async def get_user_bookings(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    # Check if user is requesting their own bookings or is staff/admin
    if user_id != str(current_user.id) and current_user.role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    bookings = await db["bookings"].find(
        {"user_id": user_id}
    ).to_list(None)
    
    return bookings
