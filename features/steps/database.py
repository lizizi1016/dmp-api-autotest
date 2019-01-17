from behave import *
from framework.api import *
import pyjq
import time
import json

use_step_matcher("cfparse")

@when(u'I found a running MySQL instance, or I skip the test')
def step_impl(context):
	#TODO
	match = {
		"instance_id": "mysql-taxb4w",
		"server_id": "server-udp2",
		"root_password": "123",
	}
	if match is None:
		context.scenario.skip("Found no MySQL instance without backup rule")
	else:
		context.mysql_instance = match

@when(u'I query the MySQL instance "{query:any}"')
def step_impl(context, query):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	resp = api_get(context, "helper/query_mysql", {
		"mysql_id": mysql["instance_id"],
		"query": query,
		"user": "root",
		"password": mysql["root_password"],
	})
	context.mysql_resp = resp

@then(u'the MySQL response should be')
def step_impl(context):
	assert context.mysql_resp != None
	resp = context.mysql_resp

	idx = 0
	for row in context.table:
		actual_row = resp[idx]
		for heading in context.table.headings:
			assert row[heading] == actual_row[heading]
		idx += 1
