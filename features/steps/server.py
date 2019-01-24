from behave import *
from framework.api import *
import pyjq
import time

use_step_matcher("cfparse")

@when("I get servers list")
def step_impl(context):
	api_request_get(context, "server/list")

@then(u'the response is a non-empty list')
def step_impl(context):
	resp = api_get_response(context)
	assert resp['total_nums'] > 0
	assert len(resp['data']) > 0 

@then(u'the response list columns are not empty: {cols:strings+}')
def step_impl(context, cols):
	resp = api_get_response(context)
	for col in cols:
		has_empty = pyjq.first('.data | any(."{0}" == null)'.format(col), resp)
		assert not has_empty

@then(u'the response list has a record whose {col:string} is "{expect_val:string}"')
def step_impl(context, col, expect_val):
	resp = api_get_response(context)
	has_match = pyjq.first('.data | any(."{0}" == "{1}")'.format(col, expect_val), resp)
	assert has_match

@when(u'I found a server without component{s:s?} {comps:strings+}, or I skip the test')
def step_impl(context, s, comps):
	resp = api_get(context, "server/list", {
		"number": context.page_size_to_select_all,
	})
	conditions = map(lambda comp: 'select(has("{0}_status") | not)'.format(comp), comps)
	condition = '.data[] | ' + " | ".join(conditions)

	match = pyjq.first(condition, resp)
	if match is None:
		context.scenario.skip("Found no server without components {0}".format(comps))
	else:
		context.server = match

@when(u'I found a server with component{s:s?} {comps:strings+}, or I skip the test')
def step_impl(context, s, comps):
    resp = api_get(context, "server/list", {
        "number": context.page_size_to_select_all,
    })
    conditions = map(lambda comp: 'select(has("{0}_status"))'.format(comp), comps)
    condition = '.data[] | ' + " | ".join(conditions)

    match = pyjq.first(condition, resp)
    if match is None:
        context.scenario.skip("Found no server with components {0}".format(comps))
    else:
        context.server = match

@when(u'I found a server with component{s:s?} {comps:strings+}, except {except_servers:strings+}')
def step_impl(context, s, comps, except_servers):
    resp = api_get(context, "server/list", {
        "number": context.page_size_to_select_all,
    })
    comp_conds = map(lambda comp: 'select(has("{0}_status"))'.format(comp), comps)
    server_conds = map(lambda except_server: 'select(.server_id != "{0}")'.format(except_server), except_servers)
    condition = '.data[] | ' + " | ".join(comp_conds) + " | " + " | ".join(server_conds)

    match = pyjq.first(condition, resp)
    assert match != None
    context.server = match

def get_installation_file(context, comp):
	installation_files = api_get(context, "support/component", {
		"pattern": comp,
	})
	assert len(installation_files) > 0
	installation_files = pyjq.all('.[] | .Name', installation_files)
	installation_file = installation_files[-1]
	assert installation_file != None
	return installation_file

@when(u'I install a component {comp:string} on the server')
def step_impl(context, comp):
	assert context.server != None
	server_id = context.server["server_id"]

	installation_file = get_installation_file(context, comp)

	api_request_post(context, "server/install", {
		"server_id": server_id,
		"component": comp,
		comp + "_id": comp + "_" + server_id,
		comp + "_install_file": installation_file,
		comp + "_path": context.component_installation_dir + comp,
		"is_sync": "true",
	})

@then(u'the server should has component{s:s?} {comps:strings+}')
def step_impl(context, s, comps):
	assert context.server != None
	server_id = context.server["server_id"]

	resp = api_get(context, "server/list", {
		"number": context.page_size_to_select_all,
	})
	conditions = map(lambda comp: 'select(has("{0}_status"))'.format(comp), comps)
	condition = '.data[] | select(."server_id" == "{0}") | '.format(server_id) + " | ".join(conditions)
	server_has_comp_status = pyjq.first(condition, resp)
	assert server_has_comp_status

@then(u'the component {comp:string} should run with the pid in pidfile')
def step_impl(context, comp):
	assert context.server != None
	server_id = context.server["server_id"]

	pids = api_get(context, "helper/pgrep", {
		"server_id": server_id,
		"pattern": comp,
	})
	pidfile = api_get(context, "helper/cat", {
		"server_id": server_id,
		"file": context.component_installation_dir + "{0}/{0}.pid".format(comp),
	})
	
	assert pidfile in pids

@then(u'the component {comp:string} install directory own user should be "{expect_own_user:string}" and own group should be "{expect_own_group:string}"')
def step_impl(context, comp, expect_own_user, expect_own_group):
	assert context.server != None
	server_id = context.server["server_id"]

	resp = api_get(context, "helper/stat", {
		"server_id": server_id,
		"file": context.component_installation_dir + comp,
	})

	assert resp["own_user_name"] == expect_own_user
	assert resp["own_group_name"] == expect_own_group

@when(u'I prepare the server for uguard')
def step_impl(context):
	server = context.server
	assert server != None

	params = {
		"is_sync": "true",
		"server_id": server["server_id"],
	}

	for comp in ["udeploy", "ustats", "uguard-agent", "urman-agent"]:
		if not comp + "_status" in server:
			installation_file = get_installation_file(context, comp)
			params["is_installed_" + comp] = "uninstalled"
			params[comp + "_id"] = comp + "_" + server["server_id"]
			params[comp + "_install_file"] = installation_file
			params[comp + "_path"] = context.component_installation_dir + comp
			if comp == "urman-agent":
				params["max-backup-concurrency-num"] = "2"

	api_request_post(context, "server/prepare_server_env_for_guard", params)

@when(u'I prepare the server for uguard manager')
def step_impl(context):
	server = context.server
	assert server != None

	params = {
		"is_sync": "true",
		"server_id": server["server_id"],
	}

	for comp in ["uguard-mgr", "urman-mgr"]:
		if not comp + "_status" in server:
			installation_file = get_installation_file(context, comp)
			params["is_installed_" + comp] = "uninstalled"
			params[comp + "_id"] = comp + "_" + server["server_id"]
			params[comp + "_install_file"] = installation_file
			params[comp + "_path"] = context.component_installation_dir + comp

	api_request_post(context, "server/prepare_server_env_for_guard_manager", params)


@then(u'the component {comp:string} should be running in {duration:time}')
def step_impl(context, comp, duration):
	assert context.server != None
	server_id = context.server["server_id"]
	
	for i in range(1, duration * context.time_weight * 10):
		resp = api_get(context, "server/list", {
			"number": context.page_size_to_select_all,
		})
		condition = '.data[] | select(."server_id" == "{0}") | ."{1}_status"'.format(server_id, comp)
		match = pyjq.first(condition, resp)
		if match != None and (match in ["STATUS_OK", "STATUS_OK(leader)", "STATUS_OK(master)"]):
			return
		time.sleep(0.1)
	assert False


@then(u'the server\'s component{s:s?} {comps:strings+} should be installed as the standard')
def step_impl(context, s, comps):
	for comp in comps:
		context.execute_steps(u"""
			Then the component {component} install directory own user should be "actiontech-universe" and own group should be "actiontech"
			And the component {component} should run with the pid in pidfile
			And the component {component} should be running in 11s
		""".format(component=comp))
