from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_db
from app.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.post("/check-all")
async def check_all_resources(db: AsyncSession = Depends(get_db)):
    """Manually check all resources."""
    try:
        await monitoring_service.check_all_resources(db)
        return {"status": "success", "message": "Resources checked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking resources: {e}")

@router.post("/start")
async def start_continuous_monitoring(db: AsyncSession = Depends(get_db)):
    """Start continuous monitoring."""
    try:
        await monitoring_service.start_continuous_monitoring(db)
        return {"status": "success", "message": "Continuous monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting monitoring: {e}")

@router.post("/stop")
async def stop_continuous_monitoring():
    """Stop continuous monitoring."""
    try:
        await monitoring_service.stop_continuous_monitoring()
        return {"status": "success", "message": "Continuous monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring: {e}")