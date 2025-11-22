"""
Migration 002: Add feature flags table
Create feature_flags table for feature management
"""

import sqlmodel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text


async def upgrade(engine: AsyncEngine):
    """Upgrade database schema."""
    async with engine.begin() as conn:
        # Create feature_flags table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feature_flags (
                id SERIAL PRIMARY KEY,
                flag_name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                flag_type VARCHAR(50) NOT NULL DEFAULT 'boolean',
                is_enabled BOOLEAN DEFAULT FALSE,
                percentage INTEGER DEFAULT 0 CHECK (percentage >= 0 AND percentage <= 100),
                value TEXT,
                target_users TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create indexes
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(flag_name)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(is_enabled)"))


async def downgrade(engine: AsyncEngine):
    """Downgrade database schema."""
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS feature_flags"))