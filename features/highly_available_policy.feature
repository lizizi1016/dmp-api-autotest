Feature: Highly Available policy
  
  Scenario: MySQL004-Highly Available policy add RTO template
	When I add a rto template
	Then the response is ok
	And the Highly Available policy list should contains the rto template
  
  Scenario: MySQL007-update RTO template configuration
	When I found a valid rto template, or I skip the test
	And I modify the rto template configuration, sla_rto: 700, sla_rto_levels: 20,30,400
	Then the response is ok
	And update the rto template configuration successful in 5s
  
  Scenario: MySQL008-remove a Highly Available policy template
	When I found a valid rto template, or I skip the test
	And I remove the rto template
	Then the response is ok
	And the rto template should be removed successfully in 5s