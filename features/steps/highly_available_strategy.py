import pyjq
from common import *

use_step_matcher("cfparse")


@when(u'I add a RTO template')
def step_impl(context):
    rto_template_name = "api_rto_" + generate_id()
    template_params = {
        "name": rto_template_name,
        "sla_rto": 300,
        "sla_rto_levels": "10,50,200",
        "sla_rto_te": "500",
        "sla_type": "rto"
    }
    api_request_post(context, "sla/add", template_params)
    context.rto_template_name = {"name": rto_template_name}


@then(
    u'the Highly Available policy list {should_or_not:should_or_not} contains the RTO template'
)
def step_impl(context, should_or_not):
    assert context.rto_template_name != None
    rto_template_name = context.rto_template_name["name"]

    resp = api_get(context, "sla/list")
    match = pyjq.first(
        '.[] | select(."name"=="{0}")'.format(rto_template_name), resp)
    assert (match != None and should_or_not) or (match == None and
                                                 not should_or_not)
