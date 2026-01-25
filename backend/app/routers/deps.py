from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from .session import current_user as session_user  # import in-memory current user

def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Returns the current user stored in session.py.
    Raises 401 if no user is selected.
    """
    if not session_user:
        raise HTTPException(status_code=401, detail="No user logged in")
    
    user = db.query(User).filter(User.user_id == session_user["user_id"], User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
