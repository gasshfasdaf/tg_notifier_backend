Feature: Resource Management
  As an API client
  I want to manage monitored resources
  So that I can track website availability

  Background:
    Given the database is clean
    And there is a user with ID 1

  Scenario: Get all resources when no resources exist
    When I request to get all resources
    Then the response status should be 200
    And the response should be an empty list

  Scenario: Get all resources when resources exist
    Given there are resources for user 1
    When I request to get all resources
    Then the response status should be 200
    And the response should contain a list of resources

  Scenario: Get resource by existing ID
    Given there is a resource with ID 1
    When I request resource with ID 1
    Then the response status should be 200
    And the response should contain resource details

  Scenario: Get resources for specific user
    Given there are resources for user 1
    When I request resources for user 1
    Then the response status should be 200
    And the response should contain user's resources