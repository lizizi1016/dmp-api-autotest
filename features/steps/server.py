from behave import *
from framework.api import *
import pyjq

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

@when(u'I found a server without component {comp:string}, or I skip the test')
def step_impl(context, comp):
    resp = api_get(context, "server/list")
    match = pyjq.first('.data[] | select(has("{0}_status") | not)'.format(comp), resp)
    if match is None:
        context.scenario.skip("Found no server without component {0}".format(comp))
    else:
    	context.server = match

@when(u'I install a component {comp:string} on the server')
def step_impl(context, comp):
    server_id = context.server["server_id"]

    installation_files = api_get(context, "support/component", {
        "pattern": comp,
    })
    assert len(installation_files) > 0
    installation_files = pyjq.all('.[] | .name', installation_files)
    installation_file = installation_files[-1]

    api_request_post(context, "server/install", {
        "server_id": server_id,
        "component": comp,
        comp + "_id": comp + "_" + server_id,
        comp + "_install_file": installation_file,
        comp + "_path": context.component_installation_dir + comp,
        "is_sync": "true",
    })

@then(u'the server should has a component {comp:string}')
def step_impl(context, comp):
    server_id = context.server["server_id"]

    resp = api_get(context, "server/list")
    server_has_comp_status = pyjq.first('.data[] | select(."server_id" == "{0}") | has("{1}_status")'.format(server_id, comp), resp)
    assert server_has_comp_status

@then(u'the component {comp:string} should run with the pid in pidfile')
def step_impl(context, comp):
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
    server_id = context.server["server_id"]

    resp = api_get(context, "helper/stat", {
        "server_id": server_id,
        "file": context.component_installation_dir + comp,
    })

    assert resp["own_user_name"] == expect_own_user
    assert resp["own_group_name"] == expect_own_group

@when(u'I found a ip segments xx.xx.0.0/16 which not contains in sip pool')
def step_impl(context):
    resp = api_get(context, "sippool/list")
    exist_ips = pyjq.all('.[] | .sip', resp)

    context.free_ip_segments = None

    for i in range(100,254):
        conflict_with_exist = any(ip.startswith('{0}.'.format(i)) for ip in exist_ips)
        if exist_ips == None or (not conflict_with_exist):
            context.free_ip_segments = '{0}.1'.format(i)
            break

    assert context.free_ip_segments != None

@when(u'I add ip {ip_desc:string} to sip pool')
def step_impl(context, ip_desc):
    assert context.free_ip_segments != None

    ip_desc = ip_desc.replace("xx.xx", context.free_ip_segments)
    api_request_post(context, "sippool/add", {
        "is_sync": "true",
        "sip": ip_desc,
    })

@then(u'the sip pool should have {expect_count:int} ips match {ip_pattern:string}')
def step_impl(context, expect_count, ip_pattern):
    assert context.free_ip_segments != None

    ip_prefix = ip_pattern.rstrip("*").replace("xx.xx", context.free_ip_segments)

    resp = api_get(context, "sippool/list")
    exist_ips = pyjq.all('.[] | .sip', resp)

    count = 0
    for ip in exist_ips:
        if ip.startswith(ip_prefix):
            count += 1

    assert count == expect_count


@then(u'the sip pool should contains {expect_ips:strings+}')
def step_impl(context, expect_ips):
    assert context.free_ip_segments != None

    resp = api_get(context, "sippool/list")
    exist_ips = pyjq.all('.[] | .sip', resp)

    for expect_ip in expect_ips:
        expect_ip = expect_ip.replace("xx.xx", context.free_ip_segments)
        assert expect_ip in exist_ips
