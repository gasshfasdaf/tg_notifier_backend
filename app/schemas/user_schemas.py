from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    telegram_chat_id: int = Field(..., description="Telegram Chat ID")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """Schema for creating a new user."""

    @validator('telegram_chat_id')
    def validate_telegram_chat_id(cls, v):
        if v == 0:
            raise ValueError('Telegram Chat ID cannot be zero')
        return v

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)