from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class ResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1)
    check_interval: int = Field(default=300, ge=60, le=86400)  # 1 minute to 1 day
    is_active: bool = Field(default=True)

class ResourceCreate(ResourceBase):
    """Schema for creating a new resource."""
    user_id: int = Field(..., description="User ID who owns this resource")

class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1)
    check_interval: Optional[int] = Field(None, ge=60, le=86400)
    is_active: Optional[bool] = None
    user_id: Optional[int] = Field(None, description="User ID who owns this resource")

class ResourceResponse(ResourceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)