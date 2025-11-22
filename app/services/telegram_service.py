from typing import Optional
import httpx
from app.config import settings


class TelegramService:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send message to specific chat_id"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )
            return response.status_code == 200

    async def get_chat_info(self, chat_id: int) -> Optional[dict]:
        """Get information about chat"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/getChat",
                json={"chat_id": chat_id}
            )
            if response.status_code == 200:
                return response.json()["result"]
            return None