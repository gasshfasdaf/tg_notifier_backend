from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from app.models.types import URLStringType, PositiveIntType


class MonitoredResource(SQLModel, table=True):
    __tablename__ = "monitored_resources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    url: URLStringType = Field(nullable=False)
    check_interval: PositiveIntType = Field(default=300)  # seconds
    is_active: bool = Field(default=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: "User" = Relationship(back_populates="resources")