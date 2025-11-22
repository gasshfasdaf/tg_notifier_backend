from typing import List, Optional
from app.repositories.resource_repository import ResourceRepository
from app.services.base_service import BaseService
from app.models.resource import MonitoredResource

class ResourceService(BaseService[ResourceRepository]):
    def __init__(self, resource_repository: ResourceRepository):
        super().__init__(resource_repository)

    async def get_resource(self, resource_id: int) -> Optional[MonitoredResource]:
        return await self.repository.get(resource_id)

    async def get_all_resources(self, skip: int = 0, limit: int = 100) -> List[MonitoredResource]:
        return await self.repository.get_all(skip, limit)

    async def get_user_resources(self, user_id: int) -> List[MonitoredResource]:
        return await self.repository.get_by_user_id(user_id)

    async def get_active_resources(self) -> List[MonitoredResource]:
        return await self.repository.get_active_resources()

    async def get_resources_for_monitoring(self) -> List[MonitoredResource]:
        return await self.repository.get_resources_for_check()

    async def create_resource(self, name: str, url: str, user_id: int,
                            check_interval: int = 300) -> MonitoredResource:
        # Бизнес-логика создания ресурса
        from app.schemas.resource_schemas import ResourceCreate
        resource_data = ResourceCreate(
            name=name,
            url=url,
            user_id=user_id,
            check_interval=check_interval
        )
        return await self.repository.create(resource_data)