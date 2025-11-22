from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from typing import List

from app.services.user_service import UserService
from app.dependencies.custom import get_user_service
from app.dependencies.feature_flags import require_user_registration
from app.middleware.rate_limiting import default_rate_limit, strict_rate_limit
from app.schemas.user_schemas import UserResponse, UserCreate, UserUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
@default_rate_limit
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_service: UserService = Depends(get_user_service)
):
    """Get all users with pagination."""
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
@strict_rate_limit
async def get_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/telegram/{telegram_chat_id}", response_model=UserResponse)
@strict_rate_limit
async def get_user_by_telegram_id(
    request: Request,
    telegram_chat_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by Telegram chat ID."""
    user = await user_service.get_user_by_telegram_id(telegram_chat_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@strict_rate_limit
async def create_user(
        request: Request,
        user_data: UserCreate,
        user_service: UserService = Depends(get_user_service),
        _: bool = Depends(require_user_registration)
):
    """Create a new user."""
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"User created successfully: {user.username} (ID: {user.id})")
        return user

    except ValueError as e:
        logger.warning(f"User creation failed - validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"User creation failed - server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user creation"
        )

@router.put("/{user_id}", response_model=UserResponse)
@strict_rate_limit
async def update_user(
        request: Request,
        user_id: int,
        user_data: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        _: bool = Depends(require_user_registration)
):
    """Update user information."""
    try:
        user = await user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"User updated successfully: {user.username} (ID: {user.id})")
        return user

    except ValueError as e:
        logger.warning(f"User update failed - validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"User update failed - server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user update"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@strict_rate_limit
async def delete_user(
        request: Request,
        user_id: int,
        user_service: UserService = Depends(get_user_service),
        _: bool = Depends(require_user_registration)
):
    """Delete user by ID."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User deleted successfully: ID {user_id}")

@router.post("/{user_id}/deactivate", response_model=UserResponse)
@strict_rate_limit
async def deactivate_user(
        request: Request,
        user_id: int,
        user_service: UserService = Depends(get_user_service),
        _: bool = Depends(require_user_registration)
):
    """Deactivate user."""
    user = await user_service.deactivate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User deactivated: {user.username} (ID: {user.id})")
    return user

@router.post("/{user_id}/activate", response_model=UserResponse)
@strict_rate_limit
async def activate_user(
        request: Request,
        user_id: int,
        user_service: UserService = Depends(get_user_service),
        _: bool = Depends(require_user_registration)
):
    """Activate user."""
    user = await user_service.activate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User activated: {user.username} (ID: {user.id})")
    return user
