Feature: dmp cluster
  This feature should only be used when installing DMP cluster

  Scenario: Init DMP
    When I init DMP
    Then the response is ok

  Scenario: Add server
    When I add server from parameter
    Then the response is ok

  Scenario: Install Udeploy,Uguard-agent,Urman-agent on all server
    When I install Udeploy,Uguard-agent,Urman-agent on all server
