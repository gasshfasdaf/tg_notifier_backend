"""
Migration 001: Initial schema
Create users and monitored_resources tables
"""

import sqlmodel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text


async def upgrade(engine: AsyncEngine):
    """Upgrade database schema."""
    async with engine.begin() as conn:
        # Create users table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_chat_id BIGINT NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create monitored_resources table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS monitored_resources (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                check_interval INTEGER DEFAULT 300,
                is_active BOOLEAN DEFAULT TRUE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create indexes
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_telegram_chat_id ON users(telegram_chat_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_resources_name ON monitored_resources(name)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_resources_user_id ON monitored_resources(user_id)"))


async def downgrade(engine: AsyncEngine):
    """Downgrade database schema."""
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS monitored_resources"))
        await conn.execute(text("DROP TABLE IF EXISTS users"))