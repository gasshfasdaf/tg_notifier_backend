#!/usr/bin/env python3
import asyncio
import os
import sys

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import create_db_and_tables
from app.config import settings


async def setup_test_db():
    """Setup test database."""
    # Используем тестовую БД
    test_db_url = settings.database_url.replace("notifier_db", "test_db")

    print(f"🔄 Setting up test database: {test_db_url}")

    # Импортируем здесь чтобы избежать циклических импортов
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlmodel import SQLModel

    engine = create_async_engine(
        test_db_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("Test database setup completed!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_test_db())