from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import database, models, security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    return next(database.get_db())

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_manager(user: models.User = Depends(get_current_user)):
    if user.role != models.UserRole.manager:
        raise HTTPException(status_code=403, detail="Manager privileges required")
    return user

def require_employee_or_manager(user: models.User = Depends(get_current_user)):
    if user.role not in [models.UserRole.employee, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return user
