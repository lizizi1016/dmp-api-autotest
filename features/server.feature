Feature: server

	@test
	Scenario: server/list should return server list
	  When I get servers list
	  Then the response is a non-empty list
	  And the response list columns are not empty: server_id, server_ip, time_stamp
	  And the response list has a record whose ucore_status is "STATUS_OK(leader)"

	@test
	Scenario Outline: server/install should install component
	  When I found a server without component <component>, or I skip the test
	  And I install a component <component> on the server
	  Then the response is ok
	  And the server should has a component <component> 
	  And the component <component> install directory own user should be "actiontech-universe" and own group should be "actiontech"
	  And the component <component> should run with the pid in pidfile
	  

	Examples: install all components
		| component |
		| ucore |
		| uagent |
		| umc |
		| udeploy |
		| uguard-mgr |
		| uguard-agent |
		| umon |
		| ulogstash |
		| uelasticsearch |
		| urman-mgr |
		| urman-agent |
		| uterm |
		| usql |
		| urds |
		| ustats |
