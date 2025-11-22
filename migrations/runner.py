import asyncio
import os
import importlib
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, text
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MigrationRunner:
    def __init__(self):
        self.database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.engine = create_async_engine(self.database_url, echo=False)
        self.migrations_table = "migration_history"

    async def init_migration_table(self):
        """Create migration history table if not exists."""
        async with self.engine.begin() as conn:
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("Migration history table initialized")

    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        async with self.engine.begin() as conn:
            result = await conn.execute(text(f"""
                SELECT version FROM {self.migrations_table} ORDER BY id
            """))
            return [row[0] for row in result]

    async def mark_migration_applied(self, version: str, name: str):
        """Mark migration as applied."""
        async with self.engine.begin() as conn:
            await conn.execute(text(f"""
                INSERT INTO {self.migrations_table} (version, name) 
                VALUES (:version, :name)
            """), {"version": version, "name": name})
            logger.info(f"Migration {version} marked as applied")

    async def run_migrations(self):
        """Run all pending migrations."""
        await self.init_migration_table()
        applied_migrations = await self.get_applied_migrations()

        # Get all migration files
        migration_files = []
        migrations_dir = os.path.join(os.path.dirname(__file__), "versions")

        for filename in sorted(os.listdir(migrations_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                migration_files.append(filename)

        # Run migrations in order
        for filename in migration_files:
            version = filename.split("_")[0]
            if version in applied_migrations:
                logger.info(f"⏩ Migration {version} already applied, skipping")
                continue

            # Import and run migration
            module_name = f"migrations.versions.{filename[:-3]}"
            migration_module = importlib.import_module(module_name)

            logger.info(f"Running migration {filename}...")
            try:
                await migration_module.upgrade(self.engine)
                await self.mark_migration_applied(version, migration_module.__name__)
                logger.info(f"Migration {filename} completed successfully")
            except Exception as e:
                logger.error(f"Migration {filename} failed: {e}")
                raise

        logger.info("🎉 All migrations completed successfully!")

    async def create_migration(self, name: str):
        """Create a new migration template."""
        migrations_dir = os.path.join(os.path.dirname(__file__), "versions")

        # Get next version number
        existing_versions = []
        for filename in os.listdir(migrations_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                existing_versions.append(filename.split("_")[0])

        next_version = f"{len(existing_versions) + 1:03d}"
        migration_filename = f"{next_version}_{name}.py"
        migration_path = os.path.join(migrations_dir, migration_filename)

        # Create migration template
        template = f'''"""
Migration {next_version}: {name}
"""

import sqlmodel
from sqlalchemy.ext.asyncio import AsyncEngine


async def upgrade(engine: AsyncEngine):
    """Upgrade database schema."""
    async with engine.begin() as conn:
        # Add your upgrade operations here
        pass


async def downgrade(engine: AsyncEngine):
    """Downgrade database schema."""
    async with engine.begin() as conn:
        # Add your downgrade operations here
        pass
'''

        with open(migration_path, 'w') as f:
            f.write(template)

        logger.info(f"Created migration: {migration_filename}")


async def run_migrations():
    """Run all pending migrations."""
    runner = MigrationRunner()
    await runner.run_migrations()


async def create_migration(name: str):
    """Create a new migration."""
    runner = MigrationRunner()
    await runner.create_migration(name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("command", choices=["migrate", "create"], help="Command to execute")
    parser.add_argument("--name", help="Migration name (for create command)")

    args = parser.parse_args()

    if args.command == "migrate":
        asyncio.run(run_migrations())
    elif args.command == "create" and args.name:
        asyncio.run(create_migration(args.name))
    else:
        print("Usage: python runner.py migrate | create --name <migration_name>")