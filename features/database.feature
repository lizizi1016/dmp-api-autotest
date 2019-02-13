Feature: database

  @test @case.272
  Scenario: database/add_group with SIP should succeed
    When I found a valid SIP, or I skip the test
    And I add a MySQL group with the SIP
    Then the response is ok
    And the MySQL group list should contains the MySQL group

  @test @case.272
  Scenario: database/add_group should succeed
    When I add a MySQL group
    Then the response is ok
    And the MySQL group list should contains the MySQL group

  @test @case.272
  Scenario: database/remove_group should succeed
    When I found a MySQL group without MySQL instance, or I skip the test
    And I remove the MySQL group
    Then the response is ok
    And the MySQL group list should not contains the MySQL group

  @test @case.272 @slow
  Scenario: add database instances of m-s should succeed
    When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
    And I found a server with components ustats,udeploy,uguard-agent,urman-agent, or I skip the test
    And I found a valid MySQL port, or I skip the test
    And I add MySQL instance in the MySQL group
    Then the response is ok
    And the MySQL group should have 1 running MySQL instance in 11s

    When I found a MySQL master in the MySQL group
    And I make a manual backup on the MySQL instance
    Then the response is ok

    When I add MySQL slave in the MySQL group
    Then the response is ok
    And the MySQL group should have 2 running MySQL instance in 11s

    When I enable HA on all MySQL instance in the MySQL group
    Then the response is ok
    And the MySQL group should have 1 running MySQL master and 1 running MySQL slave in 30s


  @test @case.272
  Scenario: database/remove instance should succeed
    When I found a running MySQL instance, or I skip the test
    And I remove MySQL instance
    Then the response is ok
    And the MySQL instance list should not contains the MySQL instance

  @test @case.272
  Scenario: database/start MySQL instance ha enable should succeed
    When I found a running MySQL instance, or I skip the test
    And start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started

  @test @case.272
  Scenario: database/configure group SIP
    When I found a running MySQL instance, or I skip the test
    And I found a MySQL group without MySQL instance, or I skip the test
    And I configure MySQL group SIP
    Then the response is ok
    And update MySQL group SIP successful in 1m