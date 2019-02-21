Feature: ushard

	@test
	Scenario: add ushard group should succeed
	  When I found 2 valid ports, or I skip the test
	  And I add a Ushard group
	  Then the response is ok
	  And the Ushard group list should contains the Ushard group

	@test
	Scenario: remove ushard should succeed
	  When I found a Ushard group without Ushard instance, or I skip the test
	  And I remove the Ushard group
	  Then the response is ok
	  And the Ushard group list should not contains the Ushard group