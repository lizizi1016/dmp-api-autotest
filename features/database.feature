Feature: database

  @test @case.272
  Scenario: MySQL-001-database/add_group with SIP should succeed
    When I found a valid SIP, or I skip the test
    And I add a MySQL group with the SIP
    Then the response is ok
    And the MySQL group list should contains the MySQL group

  @test @case.272
  Scenario: MySQL-002-database/add_group should succeed
    When I add a MySQL group
    Then the response is ok
    And the MySQL group list should contains the MySQL group

  @test @case.272
  Scenario: MySQL-003-database/remove_group should succeed
    When I found a MySQL group without MySQL instance, or I skip the test
    And I remove the MySQL group
    Then the response is ok
    And the MySQL group list should not contains the MySQL group

  @test @case.272 @slow
  Scenario: MySQL-004-add database instances of m-s should succeed
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
  Scenario: MySQL-005-database/remove instance should succeed
    When I found a running MySQL instance, or I skip the test
    And I remove MySQL instance
    Then the response is ok
    And the MySQL instance list should not contains the MySQL instance

  @test @case.272
  Scenario: MySQL-006-database/start MySQL instance ha enable should succeed
    When I found a running MySQL instance, or I skip the test
    And I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m

  @test @case.272
  Scenario: MySQL-007-database/stop MySQL instance ha enable should succeed
    When I found a running MySQL instance and uguard enable,or I skip the test
    And I stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

  @test @case.272
  Scenario: MySQL-008-database/configure group SIP
    When I found a running MySQL instance, or I skip the test
    And I found a MySQL group without MySQL instance, or I skip the test
    And I configure MySQL group SIP
    Then the response is ok
    And update MySQL group SIP successful in 1m

  @test @case.272
  Scenario: MySQL-009-database/stop MySQL service
    When I found a running MySQL instance, or I skip the test
    And I stop MySQL service
    Then the response is ok
    And stop MySQL service should succeed in 1m

  @test @case.272
  Scenario: MySQL-010-database/reset database instance
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
  Scenario: MySQL-011-database/promote to master
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
  Scenario: MySQL-012-create table in instance
    When I found a running MySQL instance, or I skip the test
    And I execute the MySQL instance "use mysql;create table testcase(id int auto_increment not null primary key ,uname char(8),gender char(2),birthday date );"
    And I query the MySQL instance "select table_name from information_schema.tables where table_name="testcase";"
    Then the MySQL response should be
      | table_name |
      | testcase   |
    When I execute the MySQL instance "use mysql;DROP TABLE testcase;"

  @test
  Scenario: MySQL-013-database/add SLA protocol and start or pause
    When I found a running MySQL instance, or I skip the test
    And I bind SLA protocol to the MySQL group
    Then the response is ok
    And SLA protocol of the MySQL group should be binded

    When I enable the SLA protocol of the MySQL group
    Then the response is ok
    And SLA protocol should started

    When I pause SLA protocol
    Then the response is ok
    And SLA protocol should paused

    When I unbind SLA protocol
    Then the response is ok
    And SLA protocol should not exist

  @test @case.272
  Scenario: MySQL-014-master-slave switching when kill three master pid
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I found alert code "EXCLUDE_INSTANCE_SUCCESS", or I skip the test
    And I kill three master pid

    Then master-slave switching in 1m
    And expect alert code "EXCLUDE_INSTANCE_SUCCESS" in 2m


  @test
  Scenario: MySQL-015-database/create MySQL user should succeed
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
  Scenario: MySQL-016-data/update MySQL user password
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
  Scenario: MySQL-017-database/takeover MySQL instance
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I detach MySQL instance
    Then the response is ok

    Then the MySQL instance should be not exist
    When I takeover MySQL instance
    Then the response is ok
    And the MySQL instance should be listed

  @test
  Scenario: MySQL-018-idempotent exclude and include ha
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

    When I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m

    When I stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

    When I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m


  @test
  Scenario: MySQL-019-SLA downgrade recovery
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add SLA protocol "SLA_RPO_sample"
    Then the response is ok

    Then SLA protocol "SLA_RPO_sample" should added

    When I start the group SLA protocol
    Then the response is ok
    And the group SLA protocol should started

    When I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m
    And group sla level PE3 in 1m
    And expect alert code "SLA_LEVEL_CHANGED" and detail "P1 to PE3" in 3m


    When I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m
    And group sla level P1 in 1m

    When I pause the group SLA protocol
    Then the response is ok
    And the group SLA protocol should paused in 1m
    When I remove the group SLA protocol
    Then the response is ok
    And the group SLA protocol should remove succeed in 1m

    When I add SLA protocol "SLA_RTO_sample"
    Then the response is ok
    And SLA protocol "SLA_RTO_sample" should added
    When I start the group SLA protocol
    Then the response is ok
    And the group SLA protocol should started
    When I exclude ha MySQL instance
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m
    And group sla level TE3 in 1m
    And expect alert code "SLA_LEVEL_CHANGED" and detail "T1 to TE3" in 3m

    When I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m
    And group sla level T1 in 1m

  @test
  Scenario: MySQL-020-restart slave uguard-agent and view instance data
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test

    When I action pause MySQL instance component uguard-agent
    Then the response is ok
    And action pause MySQL instance component uguard-agent should succeed in 1m

    When I create and insert table in master instance "use mysql;create table test55(id int auto_increment not null primary key ,uname char(8));"
    Then the response is ok
    When I query the slave instance "select table_name from information_schema.tables where table_name="test55";"
    Then the MySQL response should be
      | table_name |
      | test55   |
    When I create and insert table in master instance "use mysql;DROP TABLE test55;"
    Then the response is ok
    When I action start MySQL instance component uguard-agent
    Then the response is ok
    And action start MySQL instance component uguard-agent should succeed in 1m

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
    And the MongoDB instance should add succeed in 1m

    When I found a server with components ustats,udeploy,uguard-agent,urman-agent, or I skip the test
    When I add MongoDB instance
    Then the response is ok
    And the MongoDB group should have 1 running MongoDB master and 1 running MongoDB slave in 1m

  Scenario: E2E003-3 stop and start MongoDB instance should succeed
    When I found a running MongoDB instance slave, or I skip the test
    And I action stop the MongoDB instance
    Then the response is ok
    And the MongoDB instance should stopped in 2m

    When I action start the MongoDB instance
    Then the response is ok
    And the MongoDB instance should started in 2m

  Scenario: E2E003-4 remove MongoDB instance should succeed
    When I found a running MongoDB instance slave, or I skip the test
    And I remove MongoDB instance
    Then the response is ok
    And the MongoDB instance list should not contains the MongoDB instance in 2m



  Scenario Outline: MySQL010-update MySQL configuration with host connect should succeed
	  When I found a running MySQL instance, or I skip the test
	  And I update MySQL configuration with host connect "<option>" to "<option_value>"
	  Then the response is ok
	  When I wait for updating MySQL configuration finish in 1m
	  And I query the MySQL instance "show global variables like '<option>'"
	  Then the MySQL response should be
    	| Variable_name      | Value  |
    	| <option>  | <option_value>    |

	Examples:
		| option | option_value |
		| slave_net_timeout | 999 |
		| slave_net_timeout | 998 |
		| slave_net_timeout | 997 |

  Scenario: MGR004 components status when disable HA master-slave instance
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I action stop role STATUS_MYSQL_SLAVE on HA instance
    Then the response is ok
    And the server uguard should running
    When I action stop role STATUS_MYSQL_MASTER on HA instance
    Then the response is ok
    And the server uguard should running


  Scenario:  E2E004-2 takeover MySQL and view data consistent or remove instance
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I detach MySQL instance
    Then the response is ok

    Then the MySQL instance should be not exist
    When I takeover MySQL instance
    Then the response is ok
    And the MySQL instance should be listed

    When I enable the MySQL instance HA
    Then the response is ok
    And MySQL instance HA status should be running in 1m

    When I create and insert table in master instance "use mysql;create table test5(id int auto_increment not null primary key ,uname char(8));"
    Then the response is ok
    When I query the slave instance "select table_name from information_schema.tables where table_name="test5";"
    Then the MySQL response should be
      | table_name |
      | test5   |
    When I create and insert table in master instance "use mysql;DROP TABLE test5;"
    And I stop MySQL instance ha enable
    Then the response is ok
    And MySQL instance ha enable should stopped in 1m

    When I remove MySQL instance
    Then the response is ok
    And the MySQL instance list should not contains the MySQL instance


  Scenario: MGR001-uguard-mgr restart
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add the ip to sip pool

    When I found a valid SIP, or I skip the test
    And I configure MySQL group SIP
    Then the response is ok
    And update MySQL group SIP successful in 1m

    When I action stop component uguard-mgr in server
    Then the response is ok
    And component uguard-mgr should stopped in 1m

    When I action start component uguard-mgr
    Then the response is ok
    And component uguard-mgr should started in 1m

    When I execute the MySQL group "use mysql;create table test10(id int auto_increment not null primary key ,uname char(8));" with sip
    And I query the MySQL group "select table_name from information_schema.tables where table_name="test10";}" with sip
    Then the MySQL response should be
      | table_name |
      | test10   |

    When I execute the MySQL group "use mysql;DROP TABLE test10;" with sip

  Scenario: MGR002- no alarm when enable SLA and disable SLA or HA
    When I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I found alert code "RESTART_REPLICATION", or I skip the test
    And I found alert code "EXCLUDE_INSTANCE_SUCCESS", or I skip the test
    And I add SLA protocol "SLA_RPO_sample"
    Then the response is ok
    And SLA protocol "SLA_RPO_sample" should add succeed in 1m

    When I start the group SLA protocol
    Then the response is ok
    And the group SLA protocol should started

    When I promote slave instance to master
    Then the response is ok
    And promote slave instance to master should succeed in 1m
    And alert code RESTART_REPLICATION should not exist in 1m

    When I action stop role STATUS_MYSQL_SLAVE on HA instance
    Then the response is ok
    And alert code EXCLUDE_INSTANCE_SUCCESS should not exist in 1m

    When I action stop role STATUS_MYSQL_MASTER on HA instance
    Then the response is ok
    And alert code EXCLUDE_INSTANCE_SUCCESS should not exist in 1m

#    When I pause the group SLA protocol
#    Then the response is ok
#    And the group SLA protocol should paused in 1m
#
#    When I start the group SLA protocol
#    Then the response is ok
#    And the group SLA protocol should started

    When I action start role STATUS_MYSQL_MASTER on HA instance
    Then the response is ok
    And alert code RESTART_REPLICATION should not exist in 1m

    When I action start role STATUS_MYSQL_SLAVE on HA instance
    Then the response is ok
    And alert code RESTART_REPLICATION should not exist in 1m

    When I isolate the MySQL instance
    Then the response is ok
    And alert code mysql_slave_sql_thread_down should contains in 1m
    And alert code mysql_slave_io_thread_down should contains in 1m

  @wip
  Scenario: demo
    When I batch takeover the MySQL instance

