from fastapi import APIRouter, Depends, HTTPException, status
from ...db.mongodb import MongoDB
from ...db.models.user import UserInDB
from ...db.models.booking import BookingStatus
from ..endpoints.auth import get_current_user
from bson import ObjectId

router = APIRouter()

@router.post("/validate-qr")
async def validate_qr_code(
    qr_code: str,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    booking = await db["bookings"].find_one({"_id": ObjectId(qr_code)})
    
    if not booking:
        raise HTTPException(status_code=404, detail="Invalid QR code")
    
    if booking["status"] != "active":
        return {
            "valid": False,
            "message": f"Pass is {booking['status']}"
        }
    
    # For group passes
    if booking["is_group"]:
        available_entries = sum(
            1 for member in booking["group_members"]
            if not member["entry_status"]
        )
        if available_entries == 0:
            return {
                "valid": False,
                "message": "All members have already entered"
            }
        
        # Return group details
        return {
            "valid": True,
            "is_group": True,
            "available_entries": available_entries,
            "group_members": [
                {
                    "name": member["name"],
                    "phone": member["phone"],
                    "entered": member["entry_status"]
                }
                for member in booking["group_members"]
            ]
        }
    
    # For individual passes
    # Mark the booking as used
    await db["bookings"].update_one(
        {"_id": ObjectId(qr_code)},
        {"$set": {"status": "used"}}
    )
    
    return {
        "valid": True,
        "is_group": False,
        "message": "Entry validated successfully"
    }

@router.post("/validate-group-entry/{booking_id}/{member_index}")
async def validate_group_member_entry(
    booking_id: str,
    member_index: int,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})
    
    if not booking or not booking["is_group"]:
        raise HTTPException(status_code=404, detail="Invalid booking")
    
    if booking["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Booking is {booking['status']}"
        )
    
    if member_index >= len(booking["group_members"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid member index"
        )
    
    if booking["group_members"][member_index]["entry_status"]:
        raise HTTPException(
            status_code=400,
            detail="Member has already entered"
        )
    
    # Mark the member as entered
    update_path = f"group_members.{member_index}.entry_status"
    await db["bookings"].update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {update_path: True}}
    )
    
    # Check if all members have entered
    booking["group_members"][member_index]["entry_status"] = True
    all_entered = all(
        member["entry_status"]
        for member in booking["group_members"]
    )
    
    if all_entered:
        await db["bookings"].update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": "used"}}
        )
    
    return {
        "success": True,
        "message": "Entry validated successfully",
        "all_entered": all_entered
    }
