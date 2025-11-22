Feature: User Management
  As an API client
  I want to manage users
  So that I can work with user data

  Background:
    Given the database is clean

  Scenario: Get all users when no users exist
    When I request to get all users
    Then the response status should be 200
    And the response should be an empty list

  Scenario: Get all users when users exist
    Given there are users in the database
    When I request to get all users
    Then the response status should be 200
    And the response should contain a list of users

  Scenario: Get user by existing ID
    Given there is a user with ID 1
    When I request user with ID 1
    Then the response status should be 200
    And the response should contain user details

  Scenario: Get user by non-existing ID
    Given there are no users with ID 999
    When I request user with ID 999
    Then the response status should be 404

  Scenario: Get user by Telegram chat ID
    Given there is a user with Telegram chat ID 111111111
    When I request user by Telegram chat ID 111111111
    Then the response status should be 200
    And the response should contain user details