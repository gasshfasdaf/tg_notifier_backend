Feature: Health Check
  As an API client
  I want to check the health status of the service
  So that I can ensure it's running properly

  Scenario: Check service health when everything is working
    Given the database is available
    When I request the health endpoint
    Then the response status should be 200
    And the response should indicate healthy status

  Scenario: Check service health when database is unavailable
    Given the database is unavailable
    When I request the health endpoint
    Then the response status should be 503
    And the response should indicate unhealthy database