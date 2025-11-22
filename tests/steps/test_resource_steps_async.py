import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pathlib import Path

from app.models.user import User
from app.models.resource import MonitoredResource
from tests.fixtures.test_data import TEST_USERS, TEST_RESOURCES

scenarios("../features/resource_management.feature")

@pytest.fixture
def context():
    return {}


@given("there is a user with ID 1")
async def create_user_with_id_1(test_session):
    """Create user with ID 1."""
    user_data = TEST_USERS[0]
    user = User(**user_data.dict())
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)


@given("there are resources for user 1")
async def create_resources_for_user(test_session):
    """Create test resources for user 1."""
    # Сначала создаем пользователя
    user_data = TEST_USERS[0]
    user = User(**user_data.dict())
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Затем создаем ресурсы для этого пользователя
    for resource_data in TEST_RESOURCES:
        resource = MonitoredResource(
            **resource_data.dict(),
            user_id=user.id
        )
        test_session.add(resource)
    await test_session.commit()


@given("there is a resource with ID 1")
async def create_resource_with_id_1(test_session):
    """Create resource with ID 1."""
    # Сначала пользователь
    user_data = TEST_USERS[0]
    user = User(**user_data.dict())
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Затем ресурс
    resource_data = TEST_RESOURCES[0]
    resource = MonitoredResource(
        **resource_data.dict(),
        user_id=user.id
    )
    test_session.add(resource)
    await test_session.commit()
    await test_session.refresh(resource)


@when("I request to get all resources")
def request_all_resources(test_client, context):
    """Request all resources."""
    response = test_client.get("/resources")
    context["response"] = response


@when(parsers.parse('I request resource with ID {resource_id:d}'))
def request_resource_by_id(test_client, context, resource_id):
    """Request resource by ID."""
    response = test_client.get(f"/resources/{resource_id}")
    context["response"] = response


@when(parsers.parse('I request resources for user {user_id:d}'))
def request_resources_for_user(test_client, context, user_id):
    """Request resources for specific user."""
    response = test_client.get(f"/resources/user/{user_id}")
    context["response"] = response


@then("the response should contain a list of resources")
def check_resources_list_response(context):
    """Check response contains resources list."""
    response_data = context["response"].json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
    assert "id" in response_data[0]
    assert "name" in response_data[0]
    assert "url" in response_data[0]


@then("the response should contain resource details")
def check_resource_details_response(context):
    """Check response contains resource details."""
    response_data = context["response"].json()
    assert "id" in response_data
    assert "name" in response_data
    assert "url" in response_data
    assert "user_id" in response_data


@then("the response should contain user's resources")
def check_user_resources_response(context):
    """Check response contains user's resources."""
    response_data = context["response"].json()
    assert isinstance(response_data, list)
    # Все ресурсы должны принадлежать одному пользователю
    user_ids = set(resource["user_id"] for resource in response_data)
    assert len(user_ids) == 1