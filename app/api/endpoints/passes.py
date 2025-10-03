from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...db.mongodb import MongoDB
from ...db.models.passes import PassCreate, PassInDB, Pass, PassUpdate
from ...db.models.user import UserInDB
from ..endpoints.auth import get_current_user
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Pass])
async def list_passes():
    db = MongoDB.get_db()
    passes = await db["passes"].find({"is_active": True}).to_list(None)
    return passes

@router.get("/{pass_id}", response_model=Pass)
async def get_pass(pass_id: str):
    db = MongoDB.get_db()
    pass_ = await db["passes"].find_one({"_id": ObjectId(pass_id)})
    if not pass_:
        raise HTTPException(status_code=404, detail="Pass not found")
    return pass_

@router.post("/", response_model=Pass)
async def create_pass(
    pass_: PassCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    pass_dict = pass_.dict()
    pass_dict["_id"] = ObjectId()
    
    await db["passes"].insert_one(pass_dict)
    return Pass(**pass_dict)

@router.post("/group", response_model=Pass)
async def create_group_pass(
    pass_: PassCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not pass_.group_size or pass_.group_size < 2:
        raise HTTPException(
            status_code=400,
            detail="Group size must be at least 2"
        )
    
    pass_.type = "group"
    db = MongoDB.get_db()
    pass_dict = pass_.dict()
    pass_dict["_id"] = ObjectId()
    
    await db["passes"].insert_one(pass_dict)
    return Pass(**pass_dict)

@router.put("/{pass_id}", response_model=Pass)
async def update_pass(
    pass_id: str,
    pass_update: PassUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = MongoDB.get_db()
    update_data = pass_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db["passes"].update_one(
        {"_id": ObjectId(pass_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pass not found")
    
    updated_pass = await db["passes"].find_one({"_id": ObjectId(pass_id)})
    return Pass(**updated_pass)
