Feature: prepare

  Scenario: prepare DMP environment
    When I prepare 3 agent environment
    And I prepare 3 mgr environment

  Scenario: prepare an empty Mysql group
    When I add a MySQL group
    Then the response is ok
    Then the MySQL group list should contains the MySQL group

  Scenario: prepare valid ips to sip pool
    When I add the ip to sip pool
    Then the response is ok
    Then the sip pool should contain the added IP

  Scenario: prepare MySQL group and instance
    When I prepare 2 group MySQL 1m1s
    And I prepare 3 MySQL Single instance
#    And I prepare 1 group MySQL 1m2s
#    And I prepare 1 group MySQL 1m3s

