import pytest
from pytest_bdd import scenarios, given, when, then
from fastapi import status
from pathlib import Path

# Import feature files
feature_dir = Path(__file__).parent.parent / "features"
scenarios(feature_dir / "health_check.feature")


@pytest.fixture
def context():
    """Shared context for steps."""
    return {}


@given("the database is available")
async def database_available(test_session):
    """Ensure database is available."""
    # В реальных тестах здесь может быть проверка подключения
    pass


@given("the database is unavailable")
def database_unavailable(test_client, monkeypatch):
    """Simulate database unavailability."""

    async def mock_wait_for_db():
        return False

    monkeypatch.setattr("app.main.wait_for_db", mock_wait_for_db)


@when("I request the health endpoint")
def request_health_endpoint(test_client, context):
    """Make request to health endpoint."""
    response = test_client.get("/health")
    context["response"] = response


@then("the response status should be 200")
def check_response_status_200(context):
    """Check response status is 200."""
    assert context["response"].status_code == status.HTTP_200_OK


@then("the response status should be 503")
def check_response_status_503(context):
    """Check response status is 503."""
    assert context["response"].status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@then("the response should indicate healthy status")
def check_healthy_status(context):
    """Check response indicates healthy status."""
    response_data = context["response"].json()
    assert response_data["status"] == "ok"
    assert response_data["database"] == "healthy"


@then("the response should indicate unhealthy database")
def check_unhealthy_database(context):
    """Check response indicates unhealthy database."""
    response_data = context["response"].json()
    assert "unhealthy" in response_data["database"].lower()