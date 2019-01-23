Feature: database

	@test @case.272
	Scenario: database/add_group should succeed
	  When I found a valid SIP, or I skip the test
	  And I add a MySQL group with the SIP
	  Then the response is ok
	  And the MySQL group list should contains the MySQL group