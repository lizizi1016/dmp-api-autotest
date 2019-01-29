Feature: prepare
	@test
	Scenario: prepare environment
	  When I found a ip segments xx.xx.0.0/16 which not contains in sip pool
	  And I add ip xx.xx.1.2 to sip pool
	  Then the response is ok

	  When I add a MySQL group
	  Then the response is ok
