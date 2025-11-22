from typing import List, Optional, Any, Coroutine, Sequence

from sqlalchemy import Row, RowMapping
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User, None, None]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_telegram_id(self, telegram_chat_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.telegram_chat_id == telegram_chat_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self) -> Sequence[Row[Any] | RowMapping | Any]:
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user