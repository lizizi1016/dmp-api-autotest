from behave import *
from framework.api import *
from util import *
import parse
import pyjq


@step('I set base URL to "{base_url}"')
def set_base_url(context, base_url):
    if base_url.startswith("context"):
        context.base_url = getattr(context, base_url[8:])
    else:
        context.base_url = base_url.encode('ascii')


@then(u'the response is ok')
def step_impl(context):
    assert context.r.status_code == 200


@when(u'I found a valid port, or I skip the test')
def step_impl(context):
    port = find_valid_ports(context)
    if port != None:
        context.valid_port = str(port)
    else:
        context.scenario.skip("Found no valid port")


@when(u'I found {count:int} valid ports, or I skip the test')
def step_impl(context, count):
    ports = []
    for _ in range(0, count):
        port = find_valid_ports(context, ports)
        if port != None:
            ports.append(port)
        else:
            context.scenario.skip("Found no valid ports")
    context.valid_ports = ports


def find_valid_ports(context, excepts=[]):
    for _ in range(0, 1024):
        port = randint(6000, 65535)

        # MySQL ports
        resp = api_get(context, "database/list_instance", {
            "port": str(port),
        })
        if len(resp["data"]) > 0:
            continue

        # Ushard ports
        resp = api_get(context, "ushard/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first('.data[] | select(.flow_port == "{0}")'.format(port),
                           resp)
        if match != None:
            continue
        match = pyjq.first(
            '.data[] | select(.manage_port == "{0}")'.format(port), resp)
        if match != None:
            continue

        # except ports
        if port in excepts:
            continue

        return port
    return None


def get_installation_file(context, pattern):
    resp = api_get(context, "support/component", {
        "pattern": pattern,
    })
    assert len(resp) > 0
    return resp[-1]["Name"]
