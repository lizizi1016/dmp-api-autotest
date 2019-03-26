Feature: prepare
  @wip
  Scenario: prepare DMP environment
	When I prepare 16 agent environment
	And I prepare 3 mgr environment
	And I prepare 2 group MySQL 1m1s

  Scenario: prepare three MySQL Single instance
	When I prepare 3 MySQL Single instance

  Scenario: prepare one group MySQL 1m2s
	When I prepare 1 group MySQL 1m2s

  Scenario: prepare one group MySQL 1m3s
    When I prepare 1 group MySQL 1m3s
