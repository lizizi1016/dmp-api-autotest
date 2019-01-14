Feature: server

	@test @case.272
	Scenario: server/list should return server list
	  When I get servers list
	  Then the response is a non-empty list
	  And the response list columns are not empty: server_id, server_ip, time_stamp
	  And the response list has a record whose ucore_status is "STATUS_OK(leader)"

	@test @case.272
	Scenario Outline: server/install should install component
	  When I found a server without component <component>, or I skip the test
	  And I install a component <component> on the server
	  Then the response is ok
	  And the server should has component <component> 
	  And the server's component <component> should be installed as the standard
	  

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

	@test @case.272
	Scenario: server/prepare_server_env_for_guard should install components
	  When I found a server without components udeploy,ustats,uguard-agent,urman-agent, or I skip the test
	  And I prepare the server for uguard
	  Then the response is ok
	  And the server should has components udeploy,ustats,uguard-agent,urman-agent
	  And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard

	@test @case.272
	Scenario: sippool/add and sippool/remove should succeed
	  When I found a ip segments xx.xx.0.0/16 which not contains in sip pool
	  And I add ip xx.xx.1.2 to sip pool
	  Then the response is ok
	  And the sip pool should contain xx.xx.1.2

	  When I add ip xx.xx.1.3-xx.xx.1.5 to sip pool
	  Then the response is ok
	  And the sip pool should contain xx.xx.1.3,xx.xx.1.4,xx.xx.1.5

	  When I add ip xx.xx.1.6,xx.xx.1.8 to sip pool
	  Then the response is ok
	  And the sip pool should contain xx.xx.1.6,xx.xx.1.8

	  When I add ip xx.xx.1.9,xx.xx.1.10-xx.xx.1.20 to sip pool
	  Then the response is ok
	  And the sip pool should contain xx.xx.1.10,xx.xx.1.20
	  And the sip pool should have 18 ips match xx.xx.1.*

	  When I add ip xx.xx.2.0/24 to sip pool
	  Then the response is ok
	  And the sip pool should contain xx.xx.2.1,xx.xx.2.123,xx.xx.2.123
	  And the sip pool should have 254 ips match xx.xx.2.*

	  When I remove ip xx.xx.2.0/24 from sip pool
	  Then the response is ok
	  And the sip pool should not contain xx.xx.2.1,xx.xx.2.123,xx.xx.2.123
	  And the sip pool should have 0 ips match xx.xx.2.*

	  When I remove ip xx.xx.1.9,xx.xx.1.10-xx.xx.1.20 from sip pool
	  Then the response is ok
	  And the sip pool should not contain xx.xx.1.10,xx.xx.1.20

	  When I remove ip xx.xx.1.6,xx.xx.1.8 from sip pool
	  Then the response is ok
	  And the sip pool should not contain xx.xx.1.6,xx.xx.1.8

	  When I remove ip xx.xx.1.3-xx.xx.1.5 from sip pool
	  Then the response is ok
	  And the sip pool should not contain xx.xx.1.3,xx.xx.1.4,xx.xx.1.5
	  
	  When I remove ip xx.xx.1.2 from sip pool
	  Then the response is ok
	  And the sip pool should not contain xx.xx.1.2