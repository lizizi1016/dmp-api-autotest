Feature: urman

	@test @case.272 @slow
	Scenario: urman_rule/add_backup_rule should succeed
	  When I found a MySQL instance without backup rule, or I skip the test
	  And I add a backup rule to the MySQL instance, which will be triggered in 1m
	  Then the response is ok
	  And the MySQL instance should have a backup rule
	  And the MySQL instance should have a new backup set in 2m