from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import timedelta
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.config import get_settings
from ...db.mongodb import MongoDB
from ...db.models.user import UserCreate, UserInDB, User
from bson import ObjectId

router = APIRouter()
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await MongoDB.get_db()["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    return UserInDB(**user)

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    db = MongoDB.get_db()
    
    # Check if user already exists
    if await db["users"].find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user.dict()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_dict["_id"] = ObjectId()
    
    await db["users"].insert_one(user_dict)
    return User(**user_dict)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = MongoDB.get_db()
    user = await db["users"].find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-otp")
async def verify_otp(phone: str, otp: str):
    # Implement OTP verification logic here
    # This is a placeholder that always returns success
    return {"status": "success", "message": "OTP verified successfully"}
