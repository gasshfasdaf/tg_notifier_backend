import httpx
import asyncio
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.resource import MonitoredResource
from app.services.telegram_service import telegram_service
import logging

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring resources."""

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None

    async def start(self):
        """Initialize the monitoring service."""
        self.client = httpx.AsyncClient(timeout=10.0)
        logger.info("Monitoring service started")

    async def check_resource(self, resource: MonitoredResource) -> bool:
        """Check if resource is available."""
        if not self.client:
            raise RuntimeError("Monitoring service not started")

        try:
            response = await self.client.get(resource.url, follow_redirects=True)
            return response.status_code < 400
        except Exception as e:
            logger.error(f"Error checking resource {resource.name}: {e}")
            return False

    async def check_all_resources(self, db: AsyncSession):
        """Check all active resources."""
        if not self.client:
            return

        result = await db.execute(
            select(MonitoredResource).where(MonitoredResource.is_active == True)
        )
        resources = result.scalars().all()

        for resource in resources:
            is_available = await self.check_resource(resource)

            # Здесь можно добавить логику отслеживания изменения статуса
            # и отправки уведомлений

            status = "available" if is_available else "unavailable"
            logger.info(f"Resource {resource.name} is {status}")

    async def start_continuous_monitoring(self, db: AsyncSession):
        """Start background monitoring (for future use)."""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(db))
        logger.info("Continuous monitoring started")

    async def _monitoring_loop(self, db: AsyncSession):
        """Background monitoring loop."""
        while self.is_monitoring:
            try:
                await self.check_all_resources(db)
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def stop_continuous_monitoring(self):
        """Stop background monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        logger.info("Continuous monitoring stopped")

    async def close(self):
        """Close the monitoring service."""
        await self.stop_continuous_monitoring()
        if self.client:
            await self.client.aclose()
            self.client = None
        logger.info("Monitoring service closed")


# Global instance
monitoring_service = MonitoringService()