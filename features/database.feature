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
    And I found a valid port, or I skip the test
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
    And the MySQL instance list should not contains the MySQL instance in 1m

  @test @case.272
  Scenario: database/start MySQL instance ha enable should succeed
    When I found a running MySQL instance, or I skip the test
    And start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started

  @test @case.272
  Scenario: database/stop MySQL instance ha enable should succeed
    When I found a running MySQL instance and uguard enable,or I skip the test
    And stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped

  @test @case.272
  Scenario: database/configure group SIP
    When I found a running MySQL instance, or I skip the test
    And I found a MySQL group without MySQL instance, or I skip the test
    And I configure MySQL group SIP
    Then the response is ok
    And update MySQL group SIP successful in 1m

  @test @case.272
  Scenario: database/stop MySQL service
    When I found a running MySQL instance, or I skip the test
    And stop MySQL service
    Then the response is ok
    And stop MySQL service should succeed in 1m

  @test @case.272
  Scenario: database/reset database instance
    When I found a running MySQL instance, or I skip the test
    And I make a manual backup on the MySQL instance
    Then the response is ok

    When stop MySQL service
    Then the response is ok
    And stop MySQL service should succeed in 1m

    When reset database instance
    Then the response is ok
    And reset database instance should succeed in 2m

  @test @case.272
  Scenario: database/promote to master
    When I found one group high availability instance
    And promote slave instance to master
    Then the response is ok
    And promote slave instance to master should succeed in 1m

  @test @case.272
  Scenario Outline: view slave staus
    When I found one group high availability instance
    And I query the slave instance "SELECT SERVICE_STATE FROM performance_schema.<option>"
    Then the MySQL response should be
      |SERVICE_STATE|
      |ON           |
  Examples:
        | option                        |
        | replication_connection_status |
        | replication_applier_status    |

  @test @case.272
  Scenario: create table in instance
    When I found a running MySQL instance, or I skip the test
    And I Execution action the MySQL instance "use mysql;create table testcase(id int auto_increment not null primary key ,uname char(8),gender char(2),birthday date );"
    And I query the MySQL instance "select table_name from information_schema.tables where table_name="testcase";"
    Then the MySQL response should be
      | table_name |
      | testcase   |
    When I Execution action the MySQL instance "use mysql;DROP TABLE testcase;"

  @test
  Scenario: database/add sla protocol and start
    When I found a running MySQL instance, or I skip the test
    And I add sla protocol
    Then the response is ok
    And sla protocol should add succeed in 1m

    When I start sla protocol
    Then the response is ok
    And sla protocol should started
