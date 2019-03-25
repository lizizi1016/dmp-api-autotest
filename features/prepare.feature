Feature: prepare
  
  Scenario: prepare DMP environment
	When I prepare four agent environment
	And I prepare three mgr environment
	And I prepare two group MySQL 1m1s
  
  Scenario: prepare three MySQL Single instance
	When I prepare three MySQL Single instance
  
  Scenario: prepare one group MySQL 1m2s
	When I prepare one group MySQL 1m2s
