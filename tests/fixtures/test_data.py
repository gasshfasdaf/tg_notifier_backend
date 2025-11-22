from app.schemas.user_schemas import UserCreate
from app.schemas.resource_schemas import ResourceCreate

TEST_USERS = [
    UserCreate(
        telegram_chat_id=111111111,
        username="test_user_1",
        first_name="Test",
        last_name="User 1"
    ),
    UserCreate(
        telegram_chat_id=222222222,
        username="test_user_2",
        first_name="Test",
        last_name="User 2"
    )
]

TEST_RESOURCES = [
    ResourceCreate(
        name="Test Website",
        url="https://example.com",
        user_id=1,
        check_interval=300
    ),
    ResourceCreate(
        name="API Endpoint",
        url="https://api.example.com/health",
        user_id=1,
        check_interval=600
    )
]