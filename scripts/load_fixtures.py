#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.feature_flags import FeatureFlagService, FeatureFlags, FlagType
from app.models.user import User
from app.models.resource import MonitoredResource
from tests.fixtures.test_data import TEST_USERS, TEST_RESOURCES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_feature_flags(feature_service: FeatureFlagService):
    """Load default feature flags."""
    default_flags = [
        {
            "flag_name": FeatureFlags.USER_REGISTRATION,
            "description": "Enable user registration via API and Telegram",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        },
        {
            "flag_name": FeatureFlags.TELEGRAM_WEBHOOK,
            "description": "Enable Telegram webhook processing",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        },
        {
            "flag_name": FeatureFlags.RESOURCE_MONITORING,
            "description": "Enable resource monitoring functionality",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        },
        {
            "flag_name": FeatureFlags.NOTIFICATIONS,
            "description": "Enable sending notifications",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        },
        {
            "flag_name": FeatureFlags.RATE_LIMITING,
            "description": "Enable rate limiting",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        },
        {
            "flag_name": FeatureFlags.ADMIN_API,
            "description": "Enable admin API endpoints",
            "flag_type": FlagType.BOOLEAN,
            "is_enabled": True
        }
    ]

    for flag_data in default_flags:
        await feature_service.set_flag(**flag_data)
        logger.info(f"Loaded feature flag: {flag_data['flag_name']}")


async def load_test_data(db_session):
    """Load test users and resources."""
    # Check if users already exist
    from sqlmodel import select

    result = await db_session.execute(select(User))
    existing_users = result.scalars().all()

    if existing_users:
        logger.info("Test data already exists, skipping")
        return

    # Create test users
    users = []
    for user_data in TEST_USERS:
        user = User(**user_data.model_dump())
        db_session.add(user)
        users.append(user)

    await db_session.commit()

    # Refresh to get IDs
    for user in users:
        await db_session.refresh(user)

    # Create test resources
    for resource_data in TEST_RESOURCES:
        resource = MonitoredResource(
            **resource_data.model_dump(),
        )
        db_session.add(resource)

    await db_session.commit()
    logger.info("Test data loaded successfully")


async def main():
    """Load all fixtures."""
    print("Loading fixtures...")

    async with AsyncSessionLocal() as session:
        try:
            # Load feature flags
            feature_service = FeatureFlagService(session)
            await load_feature_flags(feature_service)

            # Load test data
            await load_test_data(session)

            print("All fixtures loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading fixtures: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())