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
    And I start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started in 1m

  @test @case.272
  Scenario: database/stop MySQL instance ha enable should succeed
    When I found a running MySQL instance and uguard enable,or I skip the test
    And I stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

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
    And I stop MySQL service
    Then the response is ok
    And stop MySQL service should succeed in 1m

  @test @case.272
  Scenario: database/reset database instance
    When I found a running MySQL instance, or I skip the test
    And I make a manual backup on the MySQL instance
    Then the response is ok

    When I stop MySQL service
    Then the response is ok
    And stop MySQL service should succeed in 1m

    When I reset database instance
    Then the response is ok
    And reset database instance should succeed in 2m

  @test @case.272
  Scenario: database/promote to master
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I promote slave instance to master
    Then the response is ok
    And promote slave instance to master should succeed in 1m

  @test @case.272
  Scenario Outline: view slave staus
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
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
    And I execute the MySQL instance "use mysql;create table testcase(id int auto_increment not null primary key ,uname char(8),gender char(2),birthday date );"
    And I query the MySQL instance "select table_name from information_schema.tables where table_name="testcase";"
    Then the MySQL response should be
      | table_name |
      | testcase   |
    When I execute the MySQL instance "use mysql;DROP TABLE testcase;"

  @test
  Scenario: database/add sla protocol and start
    When I found a running MySQL instance, or I skip the test
    And I add sla protocol
    Then the response is ok
    And sla protocol should add succeed in 1m

    When I start sla protocol
    Then the response is ok
    And sla protocol should started

  @test @case.272
  Scenario: master-slave switching when kill three master pid
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I found alert code "EXCLUDE_INSTANCE_SUCCESS", or I skip the test
    And I kill three master pid

    Then master-slave switching in 1m
    And expect alert code "EXCLUDE_INSTANCE_SUCCESS" in 2m


  @test
  Scenario: database/create MySQL user should succeed
    When I found a running MySQL instance, or I skip the test
    And I create MySQL user "testcase" and grants "all privileges on *.*"
    Then the response is ok

    When I query the MySQL instance "show grants for 'testcase';"
    Then the MySQL response should be
      |Grants for testcase@%|
      |GRANT ALL PRIVILEGES ON *.* TO 'testcase'@'%'|

    When I create MySQL user "testcase" and grants "select on *.*"
    Then the response is ok

    When I query the MySQL instance "show grants for 'testcase';"
    Then the MySQL response should be
      |Grants for testcase@%|
      |GRANT ALL PRIVILEGES ON *.* TO 'testcase'@'%'|

  @test
  Scenario: data/update MySQL user password
    When I found a running MySQL instance, or I skip the test
    And I create MySQL user "test55" and grants "all privileges on *.*"
    Then the response is ok
    When I query the MySQL instance "show grants for 'test55';"
    Then the MySQL response should be
      |Grants for test55@%|
      |GRANT ALL PRIVILEGES ON *.* TO 'test55'@'%'|

    When I update MySQL user "test55" and password "test"
    Then the response is ok

    When I query the MySQL instance use user "test55" "show grants for 'test55';"
    Then the MySQL response should be
      |Grants for test55@%|
      |GRANT ALL PRIVILEGES ON *.* TO 'test55'@'%'|

  @test
  Scenario: database/takeover MySQL instance
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I detach MySQL instance
    Then the response is ok

    Then the MySQL instance should be detached in 2m
    When I takeover MySQL instance
    Then the response is ok
    And takeover MySQL instance should succeed in 2m

  @test
  Scenario: idempotent exclude and include ha
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

    When I start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started in 1m

    When I stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

    When I start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started in 1m


  @test
  Scenario: SLA downgrade recovery
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add sla protocol "SLA_RPO_sample"
    Then the response is ok
    And sla protocol "SLA_RPO_sample" should add succeed in 1m

    When I start the group SLA protocol
    Then the response is ok
    And the group SLA protocol should started

    When I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m
    And group sla level PE3 in 1m
    And expect alert code "SLA_LEVEL_CHANGED" and detail "P1 to PE3" in 3m


    When I start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started in 1m
    And group sla level P1 in 1m

    When I pause the group SLA protocol
    Then the response is ok
    And the group SLA protocol should paused in 1m
    When I remove the group SLA protocol
    Then the response is ok
    And the group SLA protocol should remove succeed in 1m

    When I add sla protocol "SLA_RTO_sample"
    Then the response is ok
    And sla protocol "SLA_RTO_sample" should add succeed in 1m
    When I start the group SLA protocol
    Then the response is ok
    And the group SLA protocol should started
    When I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m
    And group sla level TE3 in 1m
    And expect alert code "SLA_LEVEL_CHANGED" and detail "T1 to TE3" in 3m

    When I start MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should started in 1m
    And group sla level T1 in 1m

  @test
  Scenario: restart slave uguard-agent and view instance data
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add the ip "10.20.30.111" to sip pool
    Then the response is ok

    When I found a valid SIP, or I skip the test
    And I configure MySQL group SIP
    Then the response is ok
    And update MySQL group SIP successful in 1m

    When I action pause MySQL instance component uguard-agent