Feature: prepare
	@test
	Scenario: prepare agent environment

	  When I found a server without components uguard-agent,urman-agent,uguard-mgr, or I skip the test
	  And I prepare the server for uguard
	  Then the response is ok
	  And the server should has components udeploy,ustats,uguard-agent,urman-agent
	  And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard

	  When I found a server without components uguard-agent,urman-agent,uguard-mgr, or I skip the test
	  And I prepare the server for uguard
	  Then the response is ok
	  And the server should has components udeploy,ustats,uguard-agent,urman-agent
	  And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard

	  When I found a server without components uguard-agent,urman-agent,uguard-mgr, or I skip the test
	  And I prepare the server for uguard
	  Then the response is ok
	  And the server should has components udeploy,ustats,uguard-agent,urman-agent
	  And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard

	  When I found a server without components uguard-agent,urman-agent,uguard-mgr, or I skip the test
	  And I prepare the server for uguard
	  Then the response is ok
	  And the server should has components udeploy,ustats,uguard-agent,urman-agent
	  And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard

	Scenario: prepare mgr environment
	  When I found a server without components uguard-mgr,urman-mgr,uguard-agent, or I skip the test
	  And I prepare the server for uguard manager
	  Then the response is ok
	  And the server should has components uguard-mgr,urman-mgr
	  And the server's components uguard-mgr,urman-mgr should be installed as the standard

	  When I found a server without components uguard-mgr,urman-mgr,uguard-agent, or I skip the test
	  And I prepare the server for uguard manager
	  Then the response is ok
	  And the server should has components uguard-mgr,urman-mgr
	  And the server's components uguard-mgr,urman-mgr should be installed as the standard

	  When I found a server without components uguard-mgr,urman-mgr,uguard-agent, or I skip the test
	  And I prepare the server for uguard manager
	  Then the response is ok
	  And the server should has components uguard-mgr,urman-mgr
	  And the server's components uguard-mgr,urman-mgr should be installed as the standard

	Scenario: prepare two group  1m1s
      When I add a MySQL group
	  Then the response is ok
	  And the MySQL group list should contains the MySQL group

	  When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
	  And I found a server with components uguard-agent,urman-agent,ustats,udeploy, or I skip the test
	  And I found a valid MySQL port, or I skip the test
	  And I add MySQL instance in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 1 running MySQL instance in 11s

	  When I found a MySQL master in the MySQL group
	  And I make a manual backup on the MySQL instance
	  Then the response is ok

	  When I add MySQL slave in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 2 running MySQL instance in 11s

	  When I enable HA on all MySQL instance in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 1 running MySQL master and 1 running MySQL slave in 30s

	  When I add a MySQL group
	  Then the response is ok
	  And the MySQL group list should contains the MySQL group
	  When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
	  And I found a server with components uguard-agent,urman-agent,ustats,udeploy, or I skip the test
	  And I found a valid MySQL port, or I skip the test
	  And I add MySQL instance in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 1 running MySQL instance in 11s

	  When I found a MySQL master in the MySQL group
	  And I make a manual backup on the MySQL instance
	  Then the response is ok

	  When I add MySQL slave in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 2 running MySQL instance in 11s

	  When I enable HA on all MySQL instance in the MySQL group
	  Then the response is ok
	  And the MySQL group should have 1 running MySQL master and 1 running MySQL slave in 30s
