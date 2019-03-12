Feature: Highly Available policy
  
  @wip
  Scenario Outline: MySQL004-Highly Available policy add RTO/RPO template
	When I add a <type> template
	Then the response is ok
	And the Highly Available policy list should contains the <type> template
	
	Examples: sla type
	  | type |
	  | rto  |
	  | rpo  |
  
  @wip
  Scenario Outline: MySQL007-update RTO/RPO template configuration
	When I found a valid <type> template, or I skip the test
	And I update the <type> template configuration, <config>
	Then the response is ok
	And the <type> template should exist
	
	Examples: update config
	  | type | config                                                                 |
	  | rto  | sla_rto: 700, sla_rto_levels: 20,30,400                                |
	  | rpo  | sla_rpo: 1, sla_rpo_levels: 10,40,500, sla_rpo_error_levels: 20,50,500 |
  
  
  Scenario Outline: MySQL008-remove a Highly Available policy template
	When I found a valid <type> template, or I skip the test
	And I remove the <type> template
	Then the response is ok
	And the <type> template should not exist

	Examples: sla type
	  | type |
	  | rto  |
	  | rpo  |