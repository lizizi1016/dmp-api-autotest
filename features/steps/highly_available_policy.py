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
    match = pyjq.first('.[] | select(."name"=="{0}")'.format(rto_template_name),
                       resp)
    assert (match != None and should_or_not) or (match == None and
                                                 not should_or_not)


@when(u'I found a valid {type:string} template, or I skip the test')
def step_impl(context, type):
    condition = '.[] | select(."valid"=="1") | select(."sla_type"=="{0}")'.format(
        type)
    resp = api_get(context, "sla/list")
    match = pyjq.first(condition, resp)
    if match is None:
        context.scenario.skip("No valid rto template found")
        return
    context.rto_template_name = match["name"]
    context.sla_rto_levels = match["sla_rto_levels"]
    context.sla_rto = match["sla_rto"]


@when(
    u'I modify the {type:string} template configuration, {template_values:option_values}'
)
def step_impl(context, type, template_values):
    assert context.rto_template_name != None
    assert context.sla_rto_levels != None
    assert context.sla_rto != None

    template_params = {
        "name": context.rto_template_name,
        "sla_rto": template_values['sla_rto'],
        "sla_rto_levels": template_values['sla_rto_levels'],
        "sla_rto_te": "500",
        "sla_type": type
    }
    api_request_post(context, "sla/update", template_params)
    context.sla_rto_levels = template_values['sla_rto_levels']
    context.sla_rto = template_values['sla_rto']


@then(
    u'update the {type:string} template configuration successful in {duration:time}'
)
def step_imp(context, type, duration):
    assert context.rto_template_name != None
    assert context.sla_rto_levels != None
    assert context.sla_rto != None

    def condition(context, flag):
        resp = api_get(context, "sla/list")
        condition = '.[] | select(."name"=="{0}") | select(."sla_rto_levels"=="{1}") | select(."sla_rto"=="{2}") | select(."sla_type"=="{3}")'.format(
            context.rto_template_name, context.sla_rto_levels, context.sla_rto,
            type)
        match = pyjq.first(condition, resp)

        if match == None:
            return
        if match != None:
            return True

    waitfor(context, condition, duration)
