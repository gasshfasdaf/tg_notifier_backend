from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.user_service import UserService
from app.dependencies import get_user_service
from app.schemas.user_schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_service: UserService = Depends(get_user_service)
):
    """Get all users with pagination."""
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/telegram/{telegram_chat_id}", response_model=UserResponse)
async def get_user_by_telegram_id(
    telegram_chat_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by Telegram chat ID."""
    user = await user_service.get_user_by_telegram_id(telegram_chat_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user