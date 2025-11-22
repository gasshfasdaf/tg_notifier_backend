import httpx
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for interacting with Telegram Bot API."""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: str = "HTML",
            disable_web_page_preview: bool = True
    ) -> bool:
        """Send message to Telegram chat."""
        try:
            response = await self.client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": disable_web_page_preview
                }
            )

            if response.status_code == 200:
                logger.info(f"Message sent to chat_id {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_notification(
            self,
            chat_id: int,
            resource_name: str,
            status: str,
            url: str,
            error_message: Optional[str] = None
    ) -> bool:
        """Send monitoring notification to user."""
        if status == "up":
            emoji = "✅"
            status_text = "ВЕРНУЛСЯ В СЕТЬ"
            message = f"{emoji} <b>{resource_name}</b> {status_text}\n\n🌐 <code>{url}</code>"
        elif status == "down":
            emoji = "🔴"
            status_text = "НЕДОСТУПЕН"
            message = f"{emoji} <b>{resource_name}</b> {status_text}\n\n🌐 <code>{url}</code>"
            if error_message:
                message += f"\n\n❌ Ошибка: {error_message}"
        else:
            emoji = "⚡"
            status_text = "СТАТУС ИЗМЕНИЛСЯ"
            message = f"{emoji} <b>{resource_name}</b> {status_text}\n\n🌐 <code>{url}</code>"

        return await self.send_message(chat_id, message)

    async def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Get bot information."""
        try:
            response = await self.client.get(f"{self.base_url}/getMe")
            if response.status_code == 200:
                return response.json()["result"]
            return None
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    async def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook for Telegram bot."""
        try:
            response = await self.client.post(
                f"{self.base_url}/setWebhook",
                json={"url": webhook_url}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global instance
telegram_service = TelegramService()