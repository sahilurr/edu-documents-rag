from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import UserCreate, UserInDB, UserResponse, Token
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Registers a new user in MongoDB.
    """
    logger.info(f"Attempting to register user: {user.email}")
    
    # Check if user already exists
    existing_user = await db.db.users.find_one({"email": user.email})
    if existing_user:
        logger.warning(f"Registration failed: Email {user.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the user document
    user_doc = UserInDB(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=get_password_hash(user.password)
    )
    
    # Insert into MongoDB
    # model_dump(by_alias=True, exclude_none=True) drops the empty _id so Mongo auto-generates it
    new_user = await db.db.users.insert_one(user_doc.model_dump(by_alias=True, exclude_none=True))
    
    # Fetch and return the created user
    created_user = await db.db.users.find_one({"_id": new_user.inserted_id})
    # Convert MongoDB ObjectId to string so Pydantic can serialize it
    created_user["_id"] = str(created_user["_id"])
    logger.info(f"User successfully registered: {user.email}")
    return created_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT token.
    Uses standard OAuth2 password flow (username = email).
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # Find user by email (form_data.username is mapped to email in our system)
    user_dict = await db.db.users.find_one({"email": form_data.username})
    if not user_dict:
        logger.warning("Login failed: User not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user_dict["hashed_password"]):
        logger.warning("Login failed: Incorrect password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate JWT
    access_token = create_access_token(
        data={"sub": user_dict["email"], "role": user_dict["role"]}
    )
    
    logger.info(f"User successfully logged in: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
