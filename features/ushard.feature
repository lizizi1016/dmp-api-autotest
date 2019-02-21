Feature: ushard

	@test
	Scenario: add ushard group should succeed
	  When I found 2 valid ports, or I skip the test
	  And I add a Ushard group
	  Then the response is ok
	  And the Ushard group list should contains the Ushard group

	@test
	Scenario: add ushard m-s instances should succeed
	  When I found a Ushard group without Ushard instance, or I skip the test
	  And I found a server without ushard
	  And I add Ushard instance in the Ushard group
	  Then the response is ok
	  And the Ushard group should have 1 running Ushard instance in 11s

	  When I found a server without ushard
	  And I add Ushard instance in the Ushard group
	  Then the response is ok
	  And the Ushard group should have 2 running Ushard instance in 11s

	@test
	Scenario: remove ushard should succeed
	  When I found a Ushard group without Ushard instance, or I skip the test
	  And I remove the Ushard group
	  Then the response is ok
	  And the Ushard group list should not contains the Ushard group

