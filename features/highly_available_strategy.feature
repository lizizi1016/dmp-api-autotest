Feature: Highly Available strategy
  
  @wip
  Scenario: MySQL-030 Highly Available strategy add RTO templates
	When I add a RTO templates, name: autotest_rto, type: rto, sla_rto: 300, sla_rto_levels: 10,50,200
	Then assert create RTO templates succeed, name: autotest_rto, type: rto, sla_rto: 300, sla_rto_levels: 10,50,200