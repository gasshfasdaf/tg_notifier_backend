from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import wait_for_db
from app.services.telegram_service import telegram_service
from app.services.monitoring_service import monitoring_service
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown events."""
    # Startup logic
    print("Starting application...")
    print(f"Environment: {settings.app_env}")
    print(f"Debug mode: {settings.debug}")

    # Wait for database connection
    success = await wait_for_db()
    if not success:
        print("Failed to connect to database on startup")
        if not settings.debug:
            exit(1)

    # Initialize services
    await monitoring_service.start()

    # Check Telegram bot
    if settings.telegram_bot_token:
        bot_info = await telegram_service.get_bot_info()
        if bot_info:
            print(f"Telegram Bot: @{bot_info['username']} ({bot_info['first_name']})")
        else:
            print("Telegram Bot token is invalid or bot is not accessible")
    else:
        print("⚠Telegram Bot token not set")

    print("All services initialized successfully")

    yield  # The application runs here

    # Shutdown logic
    print("Shutting down application...")
    await telegram_service.close()
    await monitoring_service.close()
    print("All services closed successfully")