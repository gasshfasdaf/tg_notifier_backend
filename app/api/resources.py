from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.services.resource_service import ResourceService
from app.dependencies import get_resource_service
from app.schemas.resource_schemas import ResourceResponse

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get all monitored resources with pagination."""
    resources = await resource_service.get_all_resources(skip=skip, limit=limit)
    return resources

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get resource by ID."""
    resource = await resource_service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.get("/user/{user_id}", response_model=List[ResourceResponse])
async def get_user_resources(
    user_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """Get all resources for a specific user."""
    resources = await resource_service.get_user_resources(user_id)
    return resources