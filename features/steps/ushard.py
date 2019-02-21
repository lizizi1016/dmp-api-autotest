from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *

use_step_matcher("cfparse")

@when(u'I add a Ushard group')
def step_impl(context):
	assert context.valid_ports != None
	assert len(context.valid_ports) >= 2
	flow_port, manage_port = context.valid_ports[0], context.valid_ports[1]

	group_id = "ushard-group-" + generate_id()

	api_request_post(context, "ushard/add_group", {
		"is_sync": True,
		"group_id": group_id,
		"admin_user": "root_user",
		"admin_password": "root_password",
		"flow_port": flow_port,
		"manage_port": manage_port,
		"charset": "utf8",
		"version": "5.6.23",
	})

	context.ushard_group = {"group_id": group_id}

@then(u'the Ushard group list {should_or_not:should_or_not} contains the Ushard group')
def step_impl(context, should_or_not):
	assert context.ushard_group != None
	group_id = context.ushard_group["group_id"]

	resp = api_get(context, "ushard/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(group_id), resp)
	assert (match != None and should_or_not) or (match == None and not should_or_not)
