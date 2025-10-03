from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ...db.mongodb import MongoDB
from ...db.models.user import UserInDB
from ...db.models.discount import DiscountCreate, Discount
from ..endpoints.auth import get_current_user
from bson import ObjectId

router = APIRouter()

@router.get("/users", response_model=List[UserInDB])
async def list_users(
    current_user: UserInDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    users = await db["users"].find().skip(skip).limit(limit).to_list(None)
    return users

@router.get("/staff-sales")
async def get_staff_sales_report(
    current_user: UserInDB = Depends(get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    
    # Build query
    query = {}
    if start_date or end_date:
        query["sale_time"] = {}
        if start_date:
            query["sale_time"]["$gte"] = start_date
        if end_date:
            query["sale_time"]["$lte"] = end_date
    
    # Aggregate sales by staff
    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$staff_id",
                "total_sales": {"$sum": 1},
                "total_amount": {"$sum": "$amount_paid"},
                "total_discount": {
                    "$sum": {
                        "$multiply": ["$amount_paid", "$discount_applied"]
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "staff_info"
            }
        }
    ]
    
    staff_sales = await db["staff_sales"].aggregate(pipeline).to_list(None)
    return staff_sales

@router.get("/stats")
async def get_stats(
    current_user: UserInDB = Depends(get_current_user),
    period: str = "today"  # today, week, month, all
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "today":
        start_date = end_date - timedelta(days=1)
    elif period == "week":
        start_date = end_date - timedelta(weeks=1)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    else:  # all time
        start_date = datetime.min
    
    # Build aggregation pipeline
    pipeline = [
        {
            "$match": {
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total_bookings": {"$sum": 1},
                "total_revenue": {"$sum": "$amount_paid"},
                "total_attendance": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "used"]},
                            1,
                            0
                        ]
                    }
                },
                "online_bookings": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$sold_by", "online"]},
                            1,
                            0
                        ]
                    }
                },
                "offline_bookings": {
                    "$sum": {
                        "$cond": [
                            {"$ne": ["$sold_by", "online"]},
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]
    
    stats = await db["bookings"].aggregate(pipeline).to_list(None)
    return stats[0] if stats else {
        "total_bookings": 0,
        "total_revenue": 0,
        "total_attendance": 0,
        "online_bookings": 0,
        "offline_bookings": 0
    }

@router.post("/discounts", response_model=Discount)
async def create_discount(
    discount: DiscountCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    
    # Check if discount code already exists
    if await db["discounts"].find_one({"code": discount.code}):
        raise HTTPException(
            status_code=400,
            detail="Discount code already exists"
        )
    
    # If assigned to staff, verify staff exists
    if discount.assigned_to:
        staff = await db["users"].find_one({
            "_id": ObjectId(discount.assigned_to),
            "role": "staff"
        })
        if not staff:
            raise HTTPException(
                status_code=404,
                detail="Staff member not found"
            )
    
    discount_dict = discount.dict()
    discount_dict["_id"] = ObjectId()
    
    await db["discounts"].insert_one(discount_dict)
    return Discount(**discount_dict)

@router.get("/group-bookings")
async def get_group_bookings(
    current_user: UserInDB = Depends(get_current_user),
    status: Optional[str] = None
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    query = {"is_group": True}
    
    if status:
        query["status"] = status
    
    group_bookings = await db["bookings"].find(query).to_list(None)
    return group_bookings
