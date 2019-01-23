from behave import *
from framework.api import *
import pyjq
import time

use_step_matcher("cfparse")

@when(u'I found a ip segments xx.xx.0.0/16 which not contains in sip pool')
def step_impl(context):
    exist_ips = get_sippool_all_ips(context)

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

@when(u'I remove ip {ip_desc:string} from sip pool')
def step_impl(context, ip_desc):
    assert context.free_ip_segments != None

    ip_desc = ip_desc.replace("xx.xx", context.free_ip_segments)
    api_request_post(context, "sippool/remove", {
        "is_sync": "true",
        "sip": ip_desc,
    })

@then(u'the sip pool should have {expect_count:int} ips match {ip_pattern:string}')
def step_impl(context, expect_count, ip_pattern):
    assert context.free_ip_segments != None
    exist_ips = get_sippool_all_ips(context)

    ip_prefix = ip_pattern.rstrip("*").replace("xx.xx", context.free_ip_segments)
    count = 0
    for ip in exist_ips:
        if ip.startswith(ip_prefix):
            count += 1

    assert count == expect_count


@then(u'the sip pool should contain {expect_ips:strings+}')
def step_impl(context, expect_ips):
    assert context.free_ip_segments != None
    exist_ips = get_sippool_all_ips(context)

    for expect_ip in expect_ips:
        expect_ip = expect_ip.replace("xx.xx", context.free_ip_segments)
        assert expect_ip in exist_ips

@then(u'the sip pool should not contain {expect_ips:strings+}')
def step_impl(context, expect_ips):
    assert context.free_ip_segments != None
    exist_ips = get_sippool_all_ips(context)

    for expect_ip in expect_ips:
        expect_ip = expect_ip.replace("xx.xx", context.free_ip_segments)
        assert not (expect_ip in exist_ips)

@when(u'I found a valid SIP, or I skip the test')
def step_impl(context):
    resp = api_get(context, "sippool/list", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first('.[] | select(.used_by? == null)', resp)
    if match is None:
        context.scenario.skip("Found no MySQL instance without backup rule")
        return
    context.valid_sip = match["sip"]

def get_sippool_all_ips(context):
    resp = api_get(context, "sippool/list", {
        "number": context.page_size_to_select_all,
    })
    return pyjq.all('.[] | .sip', resp)