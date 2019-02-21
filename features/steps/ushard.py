from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *
from common import *

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


@when(u'I found a Ushard group without Ushard instance, or I skip the test')
def step_impl(context):
	resp = api_get(context, "ushard/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_instance_num == "0")', resp)
	if match is None:
		context.scenario.skip("Found no Ushard group without Ushard instance")
	else:
		context.ushard_group = match

@when(u'I remove the Ushard group')
def step_impl(context):
	assert context.ushard_group != None
	group_id = context.ushard_group["group_id"]

	api_request_post(context, "ushard/remove_group", {
		"is_sync": True,
		"group_id": group_id,
	})

@when(u'I add Ushard instance in the Ushard group')
def step_impl(context):
	assert context.ushard_group != None
	assert context.server != None
	print(context.server)
	ushard_id = "ushard-" + generate_id()

	install_params = {
		"is_sync": True,
		"group_id": context.ushard_group["group_id"],
		"ushard_id": ushard_id,
		"server_id": context.server["server_id"],
		"cpu_cores": "1",
		"direct_memory": "0",
		"memory_heap_initial_capacity": "1024",
		"memory_heap_max_capacity": "4096",
		"ushard_path": "/opt/ushard",
		"ushard_install_file": get_ushard_installation_file(context),
		"dble_path": "/opt/ushard",
		"dble_install_file": get_dble_installation_file(context)
	}
	api_request_post(context, "ushard/add_instance", install_params)

def get_ushard_installation_file(context):
	return get_installation_file(context, "ushard")

def get_dble_installation_file(context):
	return get_installation_file(context, "dble")

@then(u'the Ushard group should have {expect_count:int} running Ushard instance in {duration:time}')
def step_impl(context, expect_count, duration):
    assert context.ushard_group != None
    group_id = context.ushard_group["group_id"]

    def condition(context, flag):
        resp = api_get(context, "ushard/list_instance", {
            "group_id": group_id,
        })
        data = resp["data"]
        assert len(data) == expect_count
        condition = '.data[] | select(."mysql_status" != "STATUS_MYSQL_HEALTH_OK" or ."replication_status" != "STATUS_MYSQL_REPL_OK")'
        match = pyjq.first(condition, resp)
        if match is not None:
            return True

    waitfor(context, condition, duration)

@when(u'I found a server without ushard')
def step_impl(context):
    resp = api_get(context, "server/list", {
        "number": context.page_size_to_select_all,
    })
    for server in pyjq.all('.data[]', resp):
    	resp = api_get(context, "ushard/list_instance", {
    		"server_id": server["server_id"]
    	})
    	match = pyjq.first('.data[] | .', resp)
    	if match is None:
    		context.server = server
    		return
    
    assert False