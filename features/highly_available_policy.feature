Feature: Highly Available policy
  
  Scenario: MySQL004-Highly Available policy add RTO template
	When I add a RTO template
	Then the response is ok
	And the Highly Available policy list should contains the RTO template
  
  Scenario: MySQL007-update RTO template configuration
	When I found a valid rto template, or I skip the test
	And I modify the rto template configuration, sla_rto: 700, sla_rto_levels: 20,30,400
	Then the response is ok
	And update the rto template configuration successful in 5s