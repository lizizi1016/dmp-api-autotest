Feature: ushard

	@test
	Scenario: add ushard group should succeed
	  When I found 2 valid ports, or I skip the test
	  And I add a Ushard group
	  Then the response is ok
	  And the Ushard group list should contains the Ushard group
