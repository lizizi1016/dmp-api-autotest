Feature: server

	@test
	Scenario: GET server/list should return server list
	  When I get servers list
	  Then the response is a non-empty list
	  And the response list columns are not empty: server_id, server_ip, time_stamp
	  And the response list has a record whose ucore_status is "STATUS_OK(leader)"