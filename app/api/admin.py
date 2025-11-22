from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.services.feature_flags import FeatureFlagService, FeatureFlag, FlagType
from app.dependencies.feature_flags import get_feature_flag_service, require_admin_api
from app.middleware.rate_limiting import strict_rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class FeatureFlagCreate(BaseModel):
    flag_name: str
    description: Optional[str] = None
    flag_type: FlagType = FlagType.BOOLEAN
    is_enabled: bool = False
    percentage: int = 0
    value: Optional[str] = None
    target_users: Optional[str] = None


class FeatureFlagUpdate(BaseModel):
    description: Optional[str] = None
    flag_type: Optional[FlagType] = None
    is_enabled: Optional[bool] = None
    percentage: Optional[int] = None
    value: Optional[str] = None
    target_users: Optional[str] = None


class FeatureFlagResponse(BaseModel):
    id: int
    flag_name: str
    description: Optional[str]
    flag_type: FlagType
    is_enabled: bool
    percentage: int
    value: Optional[str]
    target_users: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/feature_flags", response_model=List[FeatureFlagResponse])
@strict_rate_limit
async def get_all_feature_flags(
        request: Request,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Get all feature flags."""
    from sqlmodel import select
    result = await feature_service.db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    return flags


@router.get("/feature_flags/{flag_name}", response_model=FeatureFlagResponse)
@strict_rate_limit
async def get_feature_flag(
        request: Request,
        flag_name: str,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Get specific feature flag."""
    flag = await feature_service.get_flag(flag_name)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


@router.post("/feature_lags", response_model=FeatureFlagResponse)
@strict_rate_limit
async def create_feature_flag(
        request: Request,
        flag_data: FeatureFlagCreate,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Create new feature flag."""
    try:
        flag = await feature_service.set_flag(
            flag_name=flag_data.flag_name,
            is_enabled=flag_data.is_enabled,
            description=flag_data.description,
            flag_type=flag_data.flag_type,
            percentage=flag_data.percentage,
            value=flag_data.value,
            target_users=flag_data.target_users
        )
        return flag
    except Exception as e:
        logger.error(f"Error creating feature flag: {e}")
        raise HTTPException(status_code=500, detail="Error creating feature flag")


@router.put("/feature-flags/{flag_name}", response_model=FeatureFlagResponse)
@strict_rate_limit
async def update_feature_flag(
        request: Request,
        flag_name: str,
        flag_data: FeatureFlagUpdate,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Update feature flag."""
    flag = await feature_service.get_flag(flag_name)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    try:
        updated_flag = await feature_service.set_flag(
            flag_name=flag_name,
            is_enabled=flag_data.is_enabled if flag_data.is_enabled is not None else flag.is_enabled,
            description=flag_data.description or flag.description,
            flag_type=flag_data.flag_type or flag.flag_type,
            percentage=flag_data.percentage if flag_data.percentage is not None else flag.percentage,
            value=flag_data.value if flag_data.value is not None else flag.value,
            target_users=flag_data.target_users if flag_data.target_users is not None else flag.target_users
        )
        return updated_flag
    except Exception as e:
        logger.error(f"Error updating feature flag: {e}")
        raise HTTPException(status_code=500, detail="Error updating feature flag")


@router.delete("/feature-flags/{flag_name}")
@strict_rate_limit
async def delete_feature_flag(
        request: Request,
        flag_name: str,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Delete feature flag."""
    from sqlmodel import delete
    try:
        await feature_service.db.execute(
            delete(FeatureFlag).where(FeatureFlag.flag_name == flag_name)
        )
        await feature_service.db.commit()
        await feature_service.clear_cache()

        return {"status": "success", "message": f"Feature flag '{flag_name}' deleted"}
    except Exception as e:
        logger.error(f"Error deleting feature flag: {e}")
        raise HTTPException(status_code=500, detail="Error deleting feature flag")


@router.post("/feature-flags/cache/clear")
@strict_rate_limit
async def clear_feature_flag_cache(
        request: Request,
        feature_service: FeatureFlagService = Depends(get_feature_flag_service),
        _: bool = Depends(require_admin_api)
):
    """Clear feature flag cache."""
    await feature_service.clear_cache()
    return {"status": "success", "message": "Feature flag cache cleared"}