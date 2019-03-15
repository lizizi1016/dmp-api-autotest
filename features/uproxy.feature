Feature: uproxy

  Scenario: Proxy-001-add Uproxy group should succeed
    When I found a valid port, or I skip the test
    And I add Uproxy group
    Then the response is ok
    And the Uproxy group list should contains the Uproxy group

  Scenario: Proxy-002-add Uproxy m-s instances should succeed
    When I found a Uproxy group without Uproxy instance, or I skip the test
    And I found a valid port, or I skip the test
    And I found a server without Uproxy instance
    And I add Uproxy instance
    Then the response is ok
    And the Uproxy group should have 1 running Uproxy instance in 1m

    When I found a valid port, or I skip the test
    And I found a server without Uproxy instance
    And I add Uproxy instance
    Then the response is ok
    And the Uproxy group should have 2 running Uproxy instance in 1m

  Scenario: Proxy-003-add Uproxy router should succeed
    When I found 1 Uproxy group with Uproxy instance, or I skip the test
    And I add Uproxy router
    Then the response is ok
    And the Uproxy router list should contains the Uproxy router

  Scenario: Proxy-004-add Uproxy router backend should succeed
    When I found 1 Uproxy router, or I skip the test
    And I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add Uproxy router backend
    Then the response is ok
    And the Uproxy router backend list should contains the backend

  Scenario: Proxy-005-remove Uproxy router should succeed
    When I found 1 Uproxy router without backend instance, or I skip the test
    And I remove the Uproxy router
    Then the response is ok
    And Uproxy router should not contains the Uproxy router in 1m

  Scenario: Proxy-006-remove Uproxy group should succeed
    When I found a Uproxy group without Uproxy instance, or I skip the test
    And I remove the Uproxy group
    Then the response is ok
    And the Uproxy group list should not contain the Uproxy group