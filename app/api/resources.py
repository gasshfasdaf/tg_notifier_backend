from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List

from app.middleware.rate_limiting import default_rate_limit, strict_rate_limit
from app.services.resource_service import ResourceService
from app.dependencies.custom import get_resource_service
from app.schemas.resource_schemas import ResourceResponse

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("/", response_model=List[ResourceResponse])
@default_rate_limit
async def get_resources(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get all monitored resources with pagination."""
    resources = await resource_service.get_all_resources(skip=skip, limit=limit)
    return resources

@router.get("/{resource_id}", response_model=ResourceResponse)
@strict_rate_limit
async def get_resource(
    request: Request,
    resource_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get resource by ID."""
    resource = await resource_service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.get("/user/{user_id}", response_model=List[ResourceResponse])
@default_rate_limit
async def get_user_resources(
    request: Request,
    user_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get all resources for a specific user."""
    resources = await resource_service.get_user_resources(user_id)
    return resources