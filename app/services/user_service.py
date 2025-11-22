from typing import List, Optional
from sqlmodel import select
from app.repositories.user_repository import UserRepository
from app.services.base_service import BaseService
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserUpdate
import logging

logger = logging.getLogger(__name__)


class UserService(BaseService[UserRepository]):
    def __init__(self, user_repository: UserRepository):
        super().__init__(user_repository)

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.repository.get(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.repository.get_all(skip, limit)

    async def get_user_by_telegram_id(self, telegram_chat_id: int) -> Optional[User]:
        return await self.repository.get_by_telegram_id(telegram_chat_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return await self.repository.get_by_username(username)

    async def get_active_users(self) -> List[User]:
        return await self.repository.get_active_users()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with validation."""
        # Check if user with telegram_chat_id already exists
        existing_user = await self.repository.get_by_telegram_id(user_data.telegram_chat_id)
        if existing_user:
            raise ValueError(f"User with Telegram Chat ID {user_data.telegram_chat_id} already exists")

        # Check if username is taken
        existing_username = await self.repository.get_by_username(user_data.username)
        if existing_username:
            raise ValueError(f"Username '{user_data.username}' is already taken")

        # Create user
        user_dict = user_data.model_dump()
        user = User(**user_dict)

        return await self.repository.create(user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = await self.repository.get(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        # If updating username, check if it's taken
        if 'username' in update_data and update_data['username'] != user.username:
            existing_user = await self.repository.get_by_username(update_data['username'])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"Username '{update_data['username']}' is already taken")

        for field, value in update_data.items():
            setattr(user, field, value)

        return await self.repository.update(user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete user by ID with cascade deletion of resources."""
        user = await self.repository.get(user_id)
        if not user:
            return False

        # Сначала удаляем все ресурсы пользователя
        from app.repositories.resource_repository import ResourceRepository
        resource_repo = ResourceRepository(self.repository.db)
        user_resources = await resource_repo.get_by_user_id(user_id)

        for resource in user_resources:
            await resource_repo.delete(resource.id)
            logger.info(f"Deleted resource {resource.name} (ID: {resource.id}) for user {user_id}")

        # Затем удаляем пользователя
        success = await self.repository.delete(user_id)
        if success:
            logger.info(f"Deleted user {user.username} (ID: {user_id})")

        return success

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user."""
        user = await self.repository.get(user_id)
        if not user:
            return None

        user.is_active = False
        return await self.repository.update(user)

    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user."""
        user = await self.repository.get(user_id)
        if not user:
            return None

        user.is_active = True
        return await self.repository.update(user)