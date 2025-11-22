from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_db
from app.services.feature_flags import FeatureFlagService, FeatureFlags


async def get_feature_flag_service(db: AsyncSession = Depends(get_db)) -> FeatureFlagService:
    """Dependency for FeatureFlagService."""
    return FeatureFlagService(db)


async def check_feature_flag(
        flag_name: str,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        user_id: Optional[int] = None
):
    """Dependency to check if feature flag is enabled."""
    is_enabled = await feature_service.is_enabled(flag_name, user_id)

    if not is_enabled:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Feature '{flag_name}' is currently disabled"
        )

    return True


# Convenience dependencies for common flags
async def require_user_registration(
        feature_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Require user registration feature to be enabled."""
    return await check_feature_flag(FeatureFlags.USER_REGISTRATION, feature_service)


async def require_telegram_webhook(
        feature_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Require telegram webhook feature to be enabled."""
    return await check_feature_flag(FeatureFlags.TELEGRAM_WEBHOOK, feature_service)


async def require_admin_api(
        feature_service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Require admin API feature to be enabled."""
    return await check_feature_flag(FeatureFlags.ADMIN_API, feature_service)