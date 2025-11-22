from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.services.base_service import BaseService
from app.models.user import User

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

    async def create_user(self, telegram_chat_id: int, username: str,
                         first_name: Optional[str] = None,
                         last_name: Optional[str] = None) -> User:
        # В реальном приложении здесь была бы валидация и бизнес-логика
        from app.schemas.user_schemas import UserCreate
        user_data = UserCreate(
            telegram_chat_id=telegram_chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        return await self.repository.create(user_data)