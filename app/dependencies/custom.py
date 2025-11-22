from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.resource_repository import ResourceRepository
from app.services.user_service import UserService
from app.services.resource_service import ResourceService

# Repository dependencies
async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_resource_repository(db: AsyncSession = Depends(get_db)) -> ResourceRepository:
    return ResourceRepository(db)

# Service dependencies
async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repo)

async def get_resource_service(
    resource_repo: ResourceRepository = Depends(get_resource_repository)
) -> ResourceService:
    return ResourceService(resource_repo)