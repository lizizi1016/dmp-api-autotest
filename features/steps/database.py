from behave import *
from framework.api import *
import pyjq
import time
import json

use_step_matcher("cfparse")

@when(u'I found a running MySQL instance, or I skip the test')
def step_impl(context):
	mysqls = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	mysql = pyjq.first('.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK")', mysqls)
	if mysql is None:
		context.scenario.skip("Found no MySQL instance without backup rule")
		return

	root_password = api_get(context, "helper/get_mysql_password", {
		"mysql_id": mysql["mysql_id"],
		"password_type": "ROOT",
	})
	mysql["root_password"] = root_password
	context.mysql_instance = mysql

@when(u'I query the MySQL instance "{query:any}"')
def step_impl(context, query):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	resp = api_get(context, "helper/query_mysql", {
		"mysql_id": mysql["mysql_id"],
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

@when(u'I add a MySQL group with the SIP')
def step_impl(context):
	assert context.valid_sip != None
	sip = context.valid_sip

	mysql_group_id = "mysql-group-" + str(int(time.time()))

	api_request_post(context, "database/add_group", {
		"is_sync": True,
		"group_id": mysql_group_id,
		"sip": sip,
		"tag_list": "[]",
	})

	context.mysql_group_id = mysql_group_id


@then(u'the MySQL group list should contains the MySQL group')
def step_impl(context):
	assert context.mysql_group_id != None

	resp = api_get(context, "database/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(context.mysql_group_id), resp)
	assert match != None