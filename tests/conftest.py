import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.main import app
from app.database import get_db
from app.config import settings

# Используем ТЕСТОВУЮ БД
TEST_DATABASE_URL = settings.database_url.replace("notifier_db", "test_db")


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables after all tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session."""
    async with SQLModelAsyncSession(test_engine, expire_on_commit=False) as session:
        # Clean up before each test
        for table in reversed(SQLModel.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

        yield session


@pytest.fixture(scope="function")
def test_client(test_session):
    """Create FastAPI test client with overridden database dependency."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()