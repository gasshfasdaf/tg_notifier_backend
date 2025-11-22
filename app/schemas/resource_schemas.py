from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ResourceBase(BaseModel):
    name: str
    url: str
    check_interval: int = 300
    is_active: bool = True
    user_id: int

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    check_interval: Optional[int] = None
    is_active: Optional[bool] = None

class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)