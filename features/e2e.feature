
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

  Scenario: E2E011-1 add Uproxy group should succeed
    When I found a valid port, or I skip the test
    And I add Uproxy group
    Then the response is ok
    And the Uproxy group list should contains the Uproxy group

  Scenario: E2E011-2 add Uproxy m-s instances should succeed
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

  Scenario: E2E011-3 add Uproxy router should succeed
    When I found 1 Uproxy group with Uproxy instance, or I skip the test
    And I add Uproxy router
    Then the response is ok
    And the Uproxy router list should contains the Uproxy router

  Scenario: E2E011-4 add Uproxy router backend should succeed
    When I found 1 Uproxy router, or I skip the test
    And I found 1 MySQL groups with MySQL HA instances, or I skip the test
    And I add Uproxy router backend
    Then the response is ok
    And the Uproxy router backend list should contains the backend

  Scenario: E2E011-5 remove Uproxy router should succeed
    When I found 1 Uproxy router without backend instance, or I skip the test
    And I remove the Uproxy router
    Then the response is ok
    And Uproxy router should not contains the Uproxy router in 1m

  Scenario: E2E011-6 remove Uproxy group should succeed
    When I found a Uproxy group without Uproxy instance, or I skip the test
    And I remove the Uproxy group
    Then the response is ok
    And the Uproxy group list should not contain the Uproxy group

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

  Scenario Outline: add alert channel
    When I add <type> alert channel
    Then the response is ok
    And the alert channel list should contains the <type> alert channel
    Examples: channel type
	  | type |
	  | smtp  |
	  | wechat  |

  Scenario Outline: update alert channel
    When I found a valid the <type> alert channel, or I skip the test
    And I update the <type> alert channel
    Then the response is ok
    And the <type> alert channel should be updated
    Examples: channel type
	  | type |
	  | smtp  |
	  | wechat  |

  Scenario Outline: remove alert channel
    When I found a valid the <type> alert channel, or I skip the test
    And I remove the <type> alert channel
    Then the response is ok
    And the alert channel list should not contains the <type> alert channel

    Examples: channel type
	  | type |
	  | smtp  |
	  | wechat  |

  Scenario Outline: add alert configuration
    When I found a valid the <type> alert channel, or I skip the test
    And I add the <type> alert configuration
    Then the response is ok
    And the <type> alert configuration list should contains the alert configuration
    Examples: channel type
	  | type |
	  | smtp  |
	  | wechat  |

  Scenario Outline: update alert configuration
    When I found a valid the <type> alert configuration, or I skip the test
    And I update the <type> alert configuration
    Then the response is ok
    And the <type> alert configuration should be updated
    Examples: channel type
	  | type    |
	  | smtp    |
	  | wechat  |

  Scenario Outline: update alert configuration
    When I found a valid the <type> alert configuration, or I skip the test
    And I update the <type> alert configuration
    Then the response is ok
    And the <type> alert configuration should be updated
    Examples: channel type
	  | type    |
	  | smtp    |
	  | wechat  |

  Scenario Outline: remove alert configuration
    When I found a valid the <type> alert configuration, or I skip the test
    And I remove the <type> alert configuration
    Then the response is ok
    And the <type> alert configuration list should not contains the alert configuration
    Examples: channel type
	  | type    |
	  | smtp    |
	  | wechat  |
  Scenario Outline: add alert configuration subkey
    When I found a valid the <type> alert configuration, or I skip the test
    And I add the <type> alert configuration subkey
    Then the response is ok
    And the <type> alert configuration list should contains the alert configuration
    Examples: channel type
	  | type    |
	  | smtp    |
	  | wechat  |
