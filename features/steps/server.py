from behave import *
from framework.api import *
import pyjq
import parse

use_step_matcher("cfparse")

@parse.with_pattern(r"[^\s]+[\s,]*")
def parse_strings(text):
    return text.strip(" ,")

register_type(strings=parse_strings)

@parse.with_pattern(r"[^\s]+")
def parse_string(text):
    return text.strip()

register_type(string=parse_string)


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

    # TODO find component install file first

    api_post(context, "server/install", {
        "server_id": server_id,
        "component": comp,
        comp + "_id": comp + "_" + server_id,
        comp + "_install_file": comp + "-9.9.9.9-qa.x86_64.rpm",
        comp + "_path": "/opt/" + comp,
        "is_sync": "true",
    })


@then(u'the response is ok')
def step_impl(context):
    assert context.r.status_code == 200


@then(u'the server should has a component {comp:string}')
def step_impl(context, comp):
    server_id = context.server["server_id"]

    resp = api_get(context, "server/list")
    server_has_comp_status = pyjq.first('.data[] | select(."server_id" == "{0}") | has("{1}_status")'.format(server_id, comp), resp)
    assert server_has_comp_status
