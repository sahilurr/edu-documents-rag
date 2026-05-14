from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.document import PyObjectId

# Base schema for shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = Field(default="student", description="Can be 'student', 'teacher', or 'admin'")

# Schema for User Registration requests
class UserCreate(UserBase):
    password: str = Field(..., max_length=72, description="Bcrypt has a maximum password length of 72 bytes.")

# Schema for returning User data (strips out the password)
class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Schema for the MongoDB Database document
class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Schema for JWT Authentication Token
class Token(BaseModel):
    access_token: str
    token_type: str
