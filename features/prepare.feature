Feature: prepare

  Scenario: prepare DMP environment
    When I prepare 16 agent environment
    And I prepare 3 mgr environment

  Scenario: prepare an empty Mysql group
    When I add a MySQL group
    Then the response is ok
    Then the MySQL group list should contains the MySQL group

  Scenario: prepare valid ips to sip pool
    When I add the ip to sip pool
    Then the response is ok
    Then the sip pool should contain the added IP

  Scenario: add ushard group should succeed
    When I found 2 valid ports, or I skip the test
    And I add a Ushard group
    Then the response is ok
    And the Ushard group list should contains the Ushard group

  Scenario: prepare MySQL group and instance
    When I prepare 3 group MySQL 1m1s
    And I prepare 4 MySQL Single instance
#    And I prepare 1 group MySQL 1m2s
#    And I prepare 1 group MySQL 1m3s

  Scenario: add_backup_rule should succeed
    When I found a MySQL instance without backup rule, or I skip the test
    And I add a backup rule to the MySQL instance, which will be triggered in 2m
    Then the response is ok
    And the MySQL instance should have a backup rule
    And the MySQL instance should have a new backup set in 3m

