import pytest
import asyncio
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi import status
from sqlmodel import select

from app.models.user import User
from tests.fixtures.test_data import TEST_USERS

scenarios("../features/user_management.feature")

@pytest.fixture
def context():
    return {}

# АСИНХРОННЫЕ Given шаги с правильным event loop
@given("the database is clean")
async def clean_db(test_session):
    """Database is already cleaned in test_session fixture."""
    pass

@given("there are users in the database")
async def create_test_users(test_session):
    """Create test users in database."""
    for user_data in TEST_USERS:
        user = User(**user_data.model_dump())
        test_session.add(user)
    await test_session.commit()

@given("there is a user with ID 1")
async def create_user_with_id_1(test_session):
    """Create specific user with ID 1."""
    user_data = TEST_USERS[0]
    user = User(**user_data.model_dump())
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

@given(parsers.parse('there are no users with ID {user_id:d}'))
async def no_user_with_id(test_session, user_id):
    """Ensure no user exists with given ID."""
    result = await test_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    assert user is None

@given("there is a user with Telegram chat ID 111111111")
async def create_user_with_telegram_id(test_session):
    """Create user with specific Telegram chat ID."""
    user_data = TEST_USERS[0]
    user = User(**user_data.model_dump())
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

@when("I request to get all users")
def request_all_users(test_client, context):
    """Request all users."""
    response = test_client.get("/users")
    context["response"] = response

@when(parsers.parse('I request user with ID {user_id:d}'))
def request_user_by_id(test_client, context, user_id):
    """Request user by ID."""
    response = test_client.get(f"/users/{user_id}")
    context["response"] = response

@when(parsers.parse('I request user by Telegram chat ID {chat_id:d}'))
def request_user_by_telegram_id(test_client, context, chat_id):
    """Request user by Telegram chat ID."""
    response = test_client.get(f"/users/telegram/{chat_id}")
    context["response"] = response

@then("the response should be an empty list")
def check_empty_list_response(context):
    """Check response is empty list."""
    response_data = context["response"].json()
    assert response_data == []

@then("the response should contain a list of users")
def check_users_list_response(context):
    """Check response contains users list."""
    response_data = context["response"].json()
    assert isinstance(response_data, list)
    if len(response_data) > 0:
        assert "id" in response_data[0]
        assert "username" in response_data[0]

@then("the response should contain user details")
def check_user_details_response(context):
    """Check response contains user details."""
    response_data = context["response"].json()
    assert "id" in response_data
    assert "username" in response_data
    assert "telegram_chat_id" in response_data

@then(parsers.parse('the response status should be {status_code:d}'))
def check_response_status(context, status_code):
    """Check response status code."""
    assert context["response"].status_code == status_code