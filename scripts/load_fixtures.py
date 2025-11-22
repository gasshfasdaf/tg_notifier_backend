#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, AsyncSessionLocal, create_db_and_tables
from app.repositories.user_repository import UserRepository
from app.repositories.resource_repository import ResourceRepository
from app.services.user_service import UserService
from app.services.resource_service import ResourceService


async def load_fixtures():
    """Load test data into the database using the new architecture."""
    print("Creating database tables...")
    await create_db_and_tables()

    print("Loading fixtures...")
    async with AsyncSessionLocal() as session:
        # Используем новую архитектуру
        user_repo = UserRepository(session)
        resource_repo = ResourceRepository(session)
        user_service = UserService(user_repo)
        resource_service = ResourceService(resource_repo)

        # Create test users через сервис
        user1 = await user_service.create_user(
            telegram_chat_id=123456789,
            username="test_user_1",
            first_name="Test",
            last_name="User 1"
        )

        user2 = await user_service.create_user(
            telegram_chat_id=987654321,
            username="test_user_2",
            first_name="Test",
            last_name="User 2"
        )

        # Create monitored resources через сервис
        await resource_service.create_resource(
            name="Google",
            url="https://google.com",
            user_id=user1.id,
            check_interval=300
        )

        await resource_service.create_resource(
            name="GitHub",
            url="https://github.com",
            user_id=user1.id,
            check_interval=600
        )

        await resource_service.create_resource(
            name="FastAPI Docs",
            url="https://fastapi.tiangolo.com",
            user_id=user2.id,
            check_interval=900
        )

    print("Fixtures loaded successfully using new architecture!")


if __name__ == "__main__":
    asyncio.run(load_fixtures())