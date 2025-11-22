from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Инициализируем лимитер
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # Для начала используем in-memory storage
)

def get_rate_limits():
    """Get rate limits based on environment."""
    if settings.app_env == "production":
        return {
            "default": "100/minute",
            "strict": "10/minute",
            "auth": "5/minute",
            "telegram": "30/minute",
        }
    else:
        return {
            "default": "1000/minute",  # Более либеральные лимиты для разработки
            "strict": "100/minute",
            "auth": "50/minute",
            "telegram": "300/minute",
        }

RATE_LIMITS = get_rate_limits()

# Создаем декораторы с явным указанием request
def default_rate_limit(func):
    """Default rate limit for most endpoints."""
    return limiter.limit(RATE_LIMITS["default"])(func)

def strict_rate_limit(func):
    """Strict rate limit for sensitive endpoints."""
    return limiter.limit(RATE_LIMITS["strict"])(func)

def auth_rate_limit(func):
    """Rate limit for authentication endpoints."""
    return limiter.limit(RATE_LIMITS["auth"])(func)

def telegram_rate_limit(func):
    """Rate limit for Telegram webhook endpoints."""
    return limiter.limit(RATE_LIMITS["telegram"])(func)

def custom_rate_limit(rate: str):
    """Custom rate limit decorator factory."""
    def decorator(func):
        return limiter.limit(rate)(func)
    return decorator