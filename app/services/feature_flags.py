from typing import Dict, Any, Optional
from enum import Enum
import json
from sqlmodel import SQLModel, Field, select, Column, String
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FlagType(str, Enum):
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    STRING = "string"
    JSON = "json"


class FeatureFlag(SQLModel, table=True):
    __tablename__ = "feature_flags"

    id: Optional[int] = Field(default=None, primary_key=True)
    flag_name: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    flag_type: str = Field(
        default=FlagType.BOOLEAN,
        sa_column=Column(String(50), nullable=False)
    )
    is_enabled: bool = Field(default=False)
    percentage: int = Field(default=0, ge=0, le=100)  # For percentage-based flags
    value: Optional[str] = Field(default=None)  # For string/JSON flags
    target_users: Optional[str] = Field(default=None)  # JSON array of user IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FeatureFlagService:
    """Service for managing feature flags."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self._cache: Dict[str, Any] = {}

    async def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        # Check cache first
        if flag_name in self._cache:
            return self._cache[flag_name]

        # Query database
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.flag_name == flag_name)
        )
        flag = result.scalar_one_or_none()

        # Cache the result
        if flag:
            self._cache[flag_name] = flag

        return flag

    async def is_enabled(self, flag_name: str, user_id: Optional[int] = None) -> bool:
        """Check if feature flag is enabled for user."""
        flag = await self.get_flag(flag_name)

        if not flag:
            logger.warning(f"Feature flag '{flag_name}' not found")
            return False

        if not flag.is_enabled:
            return False

        # Percentage-based rollout
        if flag.flag_type == FlagType.PERCENTAGE and user_id:
            return (user_id % 100) < flag.percentage

        # User-specific targeting
        if flag.target_users and user_id:
            try:
                target_users = json.loads(flag.target_users)
                return user_id in target_users
            except json.JSONDecodeError:
                logger.error(f"Invalid target_users JSON for flag '{flag_name}'")

        return flag.is_enabled

    async def get_value(self, flag_name: str, default: Any = None) -> Any:
        """Get feature flag value."""
        flag = await self.get_flag(flag_name)

        if not flag or not flag.is_enabled:
            return default

        if flag.flag_type == FlagType.JSON and flag.value:
            try:
                return json.loads(flag.value)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON value for flag '{flag_name}'")
                return default

        return flag.value if flag.value else default

    async def set_flag(
            self,
            flag_name: str,
            is_enabled: bool,
            description: Optional[str] = None,
            flag_type: FlagType = FlagType.BOOLEAN,
            percentage: int = 0,
            value: Optional[str] = None,
            target_users: Optional[str] = None
    ) -> FeatureFlag:
        """Create or update feature flag."""
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.flag_name == flag_name)
        )
        existing_flag = result.scalar_one_or_none()

        if existing_flag:
            # Update existing flag
            existing_flag.description = description or existing_flag.description
            existing_flag.flag_type = flag_type
            existing_flag.is_enabled = is_enabled
            existing_flag.percentage = percentage
            existing_flag.value = value
            existing_flag.target_users = target_users
            existing_flag.updated_at = datetime.utcnow()
        else:
            # Create new flag
            existing_flag = FeatureFlag(
                flag_name=flag_name,
                description=description,
                flag_type=flag_type,
                is_enabled=is_enabled,
                percentage=percentage,
                value=value,
                target_users=target_users
            )
            self.db.add(existing_flag)

        await self.db.commit()
        await self.db.refresh(existing_flag)

        # Update cache
        self._cache[flag_name] = existing_flag

        return existing_flag


# Pre-defined feature flags
class FeatureFlags:
    USER_REGISTRATION = "user_registration"
    TELEGRAM_WEBHOOK = "telegram_webhook"
    RESOURCE_MONITORING = "resource_monitoring"
    NOTIFICATIONS = "notifications"
    RATE_LIMITING = "rate_limiting"
    ADMIN_API = "admin_api"