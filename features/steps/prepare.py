from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *
from server import *

use_step_matcher("cfparse")


@when(u'I prepare {count:int} agent environment')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
        When I found a server without components uguard-agent,urman-agent,uguard-mgr, or I skip the test
	    And I prepare the server for uguard
	    Then the response is ok
	    And the server should has components udeploy,ustats,uguard-agent,urman-agent
	    And the server's components udeploy,ustats,uguard-agent,urman-agent should be installed as the standard
		""")


@when(u'I prepare {count:int} mgr environment')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
        When I found a server without components uguard-mgr,urman-mgr,uguard-agent, or I skip the test
	    And I prepare the server for uguard manager
	    Then the response is ok
	    And the server should has components uguard-mgr,urman-mgr
	    And the server's components uguard-mgr,urman-mgr should be installed as the standard
		""")


@when(u'I prepare {count:int} group MySQL 1m1s')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
		When I add a MySQL group
		Then the response is ok
		And the MySQL group list should contains the MySQL group

		When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
		And I found a server with components uguard-agent,urman-agent,ustats,udeploy, or I skip the test
		And I found a valid port, or I skip the test
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
		""")


@when(u'I prepare {count:int} MySQL Single instance')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
		When I add a MySQL group
	    Then the response is ok
	    And the MySQL group list should contains the MySQL group
		When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
		And I found a server with components ustats,udeploy,uguard-agent,urman-agent, or I skip the test
		And I found a valid port, or I skip the test
		And I add MySQL instance in the MySQL group
		Then the response is ok
		And the MySQL group should have 1 running MySQL instance in 30s
		""")


@when('I prepare {count:int} group MySQL 1m2s')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
        When I add a MySQL group
        Then the response is ok
        And the MySQL group list should contains the MySQL group

        When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
        And I found a server with components uguard-agent,urman-agent,ustats,udeploy, or I skip the test
        And I found a valid port, or I skip the test
        And I add MySQL instance in the MySQL group
        Then the response is ok
        And the MySQL group should have 1 running MySQL instance in 11s

        When I found a MySQL master in the MySQL group
        And I make a manual backup on the MySQL instance
        Then the response is ok

        When I add MySQL slave in the MySQL group
        Then the response is ok
        And the MySQL group should have 2 running MySQL instance in 11s
        
        When I add MySQL slave in the MySQL group
        Then the response is ok
        And the MySQL group should have 3 running MySQL instance in 11s
        
        When I enable HA on all MySQL instance in the MySQL group
        Then the response is ok
        And the MySQL group should have 1 running MySQL master and 2 running MySQL slave in 30s 
    		""")


@when('I prepare {count:int} group MySQL 1m3s')
def step_imp(context, count):
    for i in range(0, count):
        context.execute_steps(u"""
        When I add a MySQL group
        Then the response is ok
        And the MySQL group list should contains the MySQL group

        When I found a MySQL group without MySQL instance, and without SIP, or I skip the test
        And I found a server with components uguard-agent,urman-agent,ustats,udeploy, or I skip the test
        And I found a valid port, or I skip the test
        And I add MySQL instance in the MySQL group
        Then the response is ok
        And the MySQL group should have 1 running MySQL instance in 11s

        When I found a MySQL master in the MySQL group
        And I make a manual backup on the MySQL instance
        Then the response is ok

        When I add MySQL slave in the MySQL group
        Then the response is ok
        And the MySQL group should have 2 running MySQL instance in 11s

        When I add MySQL 2 slave in the MySQL group
        Then the response is ok
        And the MySQL group should have 3 running MySQL instance in 11s

        When I add MySQL 3 slave in the MySQL group
        Then the response is ok
        And the MySQL group should have 4 running MySQL instance in 11s

        When I enable HA on all MySQL instance in the MySQL group
        Then the response is ok
        And the MySQL group should have 1 running MySQL master and 3 running MySQL slave in 60s 
            """)
