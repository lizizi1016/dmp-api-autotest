Feature: Highly Available policy
  
  Scenario: MySQL-030 Highly Available policy add RTO template
	When I add a RTO template
	Then the response is ok
	And the Highly Available policy list should contains the RTO template