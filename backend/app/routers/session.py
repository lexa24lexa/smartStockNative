from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..database import SessionLocal

router = APIRouter(prefix="/session", tags=["Session"])

# In-memory current user (for demo; can switch to DB/Redis for persistence)
current_user: Optional[dict] = None

# Request model
class CurrentUserIn(BaseModel):
    user_id: int

# Response model
class CurrentUserOut(BaseModel):
    user_id: int
    username: str
    role_id: int
    store_id: int
    is_active: bool

    class Config:
        from_attributes = True

# Set current user
@router.post("/user", response_model=CurrentUserOut)
def set_current_user(user_in: CurrentUserIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_in.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    global current_user
    current_user = {
        "user_id": user.user_id,
        "username": user.username,
        "role_id": user.role_id,
        "store_id": user.store_id,
        "is_active": user.is_active
    }
    return current_user

# Get current user
@router.get("/user", response_model=CurrentUserOut)
def get_current_user():
    if not current_user:
        raise HTTPException(status_code=404, detail="No user selected")
    return current_user

with SessionLocal() as db:
    user = db.query(User).filter(User.user_id == 1, User.is_active == True).first()
    if user:
        current_user = {
            "user_id": user.user_id,
            "username": user.username,
            "role_id": user.role_id,
            "store_id": user.store_id,
            "is_active": user.is_active
        }
