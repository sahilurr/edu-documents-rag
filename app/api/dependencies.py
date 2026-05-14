from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import db
from app.models.user import UserResponse
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# This tells FastAPI where the client should go to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency that extracts the JWT token from the Authorization header,
    decodes it, and retrieves the corresponding user from MongoDB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        logger.warning("Failed to decode JWT token.")
        raise credentials_exception
        
    # Fetch user from MongoDB
    user = await db.db.users.find_one({"email": email})
    if user is None:
        logger.warning(f"Valid token presented, but user {email} no longer exists in DB.")
        raise credentials_exception
        
    return user

async def get_current_active_admin_or_teacher(current_user: dict = Depends(get_current_user)):
    """
    Dependency to restrict access to Admins or Teachers only (e.g., for uploading PDFs).
    """
    if current_user.get("role") not in ["admin", "teacher"]:
        logger.warning(f"Access denied for user {current_user.get('email')}. Insufficient permissions.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have enough privileges. Only teachers or admins can perform this action."
        )
    return current_user
