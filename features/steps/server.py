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