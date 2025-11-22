#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations.runner import run_migrations

async def main():
    """Run database migrations."""
    print("Starting database migrations...")
    try:
        await run_migrations()
        print("Database migrations completed successfully!")
    except Exception as e:
        print(f"Database migrations failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())