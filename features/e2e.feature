
Feature: end-to-end

  Scenario: E2E003-1 add MongoDB group should succeed
    When I found a valid port, or I skip the test
    And I add MongoDB group
    Then the response is ok
    And the MongoDB group list should contains the MongoDB group

  Scenario: E2E003-2 add MongoDB instance should succeed
    When I found a server with components ustats,udeploy,uguard-agent,urman-agent, or I skip the test
    And I found a MongoDB group without MongoDB instance, or I skip the test
    When I add MongoDB instance
    Then the response is ok
    And MongoDB instance should add succeed in 1m

    When I found a server with components ustats,udeploy,uguard-agent,urman-agent, or I skip the test
    When I add MongoDB instance
    Then the response is ok
    And the MongoDB group should have 1 running MongoDB master and 1 running MongoDB slave in 1m

  Scenario: E2E003-3 stop and start MongoDB instance should succeed
    When I found a running MongoDB instance slave, or I skip the test
    And I action stop MongoDB instance
    Then the response is ok
    And MongoDB instance should stopped in 2m

    When I action start MongoDB instance
    Then the response is ok
    And MongoDB instance should started in 2m

  Scenario: E2E003-4 remove MongoDB instance should succeed
    When I found a running MongoDB instance slave, or I skip the test
    And I remove MongoDB instance
    Then the response is ok
    And the MongoDB instance list should not contains the MongoDB instance in 2m

  Scenario: E2E011-1 add Uproxy group should succeed
    When I found a valid port, or I skip the test
    And I add Uproxy group
    Then the response is ok
    And the Uproxy group list should contains the Uproxy group

  Scenario: E2E011-2 add Uproxy m-s instances should succeed
    When I found a Uproxy group without Uproxy instance, or I skip the test
    And I found a server without uproxy








