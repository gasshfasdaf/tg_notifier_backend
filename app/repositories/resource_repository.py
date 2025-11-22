from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.resource import MonitoredResource
from app.repositories.base_repository import BaseRepository

class ResourceRepository(BaseRepository[MonitoredResource, None, None]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(MonitoredResource, db_session)

    async def get_by_user_id(self, user_id: int) -> List[MonitoredResource]:
        result = await self.db.execute(
            select(MonitoredResource).where(MonitoredResource.user_id == user_id)
        )
        return result.scalars().all()

    async def get_active_resources(self) -> List[MonitoredResource]:
        result = await self.db.execute(
            select(MonitoredResource).where(MonitoredResource.is_active == True)
        )
        return result.scalars().all()

    async def get_resources_for_check(self) -> List[MonitoredResource]:
        """Get active resources that need to be checked."""
        result = await self.db.execute(
            select(MonitoredResource).where(MonitoredResource.is_active == True)
        )
        return result.scalars().all()