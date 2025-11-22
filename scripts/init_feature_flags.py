#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.feature_flags import FeatureFlagService, FeatureFlags, FlagType


async def init_feature_flags():
    """Initialize default feature flags."""
    async with AsyncSessionLocal() as session:
        feature_service = FeatureFlagService(session)

        # Default feature flags
        default_flags = [
            {
                "name": FeatureFlags.USER_REGISTRATION,
                "description": "Enable user registration via API and Telegram",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": True
            },
            {
                "name": FeatureFlags.TELEGRAM_WEBHOOK,
                "description": "Enable Telegram webhook processing",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": True
            },
            {
                "name": FeatureFlags.RESOURCE_MONITORING,
                "description": "Enable resource monitoring functionality",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": True
            },
            {
                "name": FeatureFlags.NOTIFICATIONS,
                "description": "Enable sending notifications",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": True
            },
            {
                "name": FeatureFlags.RATE_LIMITING,
                "description": "Enable rate limiting",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": True
            },
            {
                "name": FeatureFlags.ADMIN_API,
                "description": "Enable admin API endpoints",
                "flag_type": FlagType.BOOLEAN,
                "is_enabled": False  # Disabled by default for security
            }
        ]

        for flag_data in default_flags:
            await feature_service.set_flag(**flag_data)
            print(f"Initialized feature flag: {flag_data['name']}")

        print("All feature flags initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_feature_flags())