from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User

def get_current_user(user_id: int = Header(...), db: Session = Depends(get_db)):
    """
    Simulate logged-in user via user_id header.
    """
    user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
