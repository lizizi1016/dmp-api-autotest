Feature: dmp cluster
  This feature should only be used when installing DMP cluster

  Scenario: Init DMP
    When I init DMP
    Then the response is ok
