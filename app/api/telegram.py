from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.telegram_service import telegram_service
from app.dependencies.feature_flags import require_telegram_webhook
from app.middleware.rate_limiting import auth_rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/telegram", tags=["telegram"])


@router.post("")
@auth_rate_limit
async def handle_telegram_webhook(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """Handle incoming Telegram webhook updates."""
    try:
        update = await request.json()
        logger.info(f"Received Telegram update: {update}")

        # Process the update
        await process_telegram_update(update, db)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


async def process_telegram_update(update: dict, db: AsyncSession):
    """Process incoming Telegram update."""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        # Handle different commands
        if text.startswith("/start"):
            await handle_start_command(chat_id, message, db)
        elif text.startswith("/register"):
            await handle_register_command(chat_id, message, db)
        elif text.startswith("/help"):
            await handle_help_command(chat_id)
        else:
            await handle_unknown_command(chat_id)


async def handle_start_command(chat_id: int, message: dict, db: AsyncSession):
    """Handle /start command."""
    user_info = message["from"]
    welcome_text = f"""
👋 Привет, {user_info.get('first_name', 'друг')}!

Я - бот для мониторинга веб-ресурсов. Я могу отслеживать доступность ваших сайтов и API.

🤖 <b>Доступные команды:</b>
/register - Зарегистрироваться в системе
/help - Получить справку

🆔 <b>Ваш Chat ID:</b> <code>{chat_id}</code>
Сохраните этот ID, он понадобится для регистрации на сайте.

📋 Для начала работы зарегистрируйтесь на нашем сайте с вашим Chat ID.
"""

    await telegram_service.send_message(chat_id, welcome_text)


async def handle_register_command(chat_id: int, message: dict, db: AsyncSession):
    """Handle /register command."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        response_text = f"""
✅ Вы уже зарегистрированы в системе!

👤 <b>Ваши данные:</b>
Username: {existing_user.username}
Chat ID: <code>{existing_user.telegram_chat_id}</code>

💡 Для управления ресурсами перейдите на сайт.
"""
    else:
        user_info = message["from"]
        username = user_info.get("username", f"user_{chat_id}")
        first_name = user_info.get("first_name")
        last_name = user_info.get("last_name")

        # Create new user
        new_user = User(
            telegram_chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        response_text = f"""
🎉 Регистрация успешно завершена!

👤 <b>Ваши данные:</b>
Username: {username}
Chat ID: <code>{chat_id}</code>
Имя: {first_name or 'Не указано'}

💡 Теперь вы можете добавлять ресурсы для мониторинга на нашем сайте.
"""

    await telegram_service.send_message(chat_id, response_text)


async def handle_help_command(chat_id: int):
    """Handle /help command."""
    help_text = """
📖 <b>Справка по боту мониторинга</b>

🤖 <b>Основные команды:</b>
/start - Начать работу с ботом
/register - Зарегистрироваться в системе
/help - Показать эту справку

🔍 <b>Как это работает:</b>
1. Зарегистрируйтесь с помощью команды /register
2. Сохраните ваш Chat ID
3. На сайте добавьте ресурсы для мониторинга
4. Получайте уведомления о статусе ресурсов

🌐 <b>Поддерживаемые ресурсы:</b>
- Веб-сайты (HTTP/HTTPS)
- API endpoints
- Любые доступные по URL ресурсы

⚡ <b>Уведомления:</b>
✅ Ресурс доступен
🔴 Ресурс недоступен
⚡ Изменение статуса

💡 <b>Ваш Chat ID:</b> <code>{chat_id}</code>
"""

    await telegram_service.send_message(chat_id, help_text)


async def handle_unknown_command(chat_id: int):
    """Handle unknown commands."""
    response_text = """
❌ Неизвестная команда.

🤖 Доступные команды:
/start - Начать работу
/register - Зарегистрироваться  
/help - Получить справку

💡 Используйте /help для получения полной справки.
"""

    await telegram_service.send_message(chat_id, response_text)