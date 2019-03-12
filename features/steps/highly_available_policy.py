import pyjq
from common import *

use_step_matcher("cfparse")


@when(u'I add a {type:string} template')
def step_impl(context, type):
    sla_template = "api_{0}_".format(type) + generate_id()
    template_params = {}
    if type == 'rto':
        template_params = {
            "name": sla_template,
            "sla_rto": 300,
            "sla_rto_levels": "10,50,200",
            "sla_rto_te": "500",
            "sla_type": type
        }
    elif type == 'rpo':
        template_params = {
            "name": sla_template,
            "sla_rpo": 0,
            "sla_rpo_levels": "10,50,200",
            "sla_rpo_error_levels": "20,60,600",
            "sla_type": type
        }

    print(template_params)
    api_request_post(context, "sla/add", template_params)
    context.sla_template = {"name": sla_template}


@then(
    u'the Highly Available policy list {should_or_not:should_or_not} contains the {type:string} template'
)
def step_impl(context, should_or_not, type):
    assert context.sla_template != None
    sla_template = context.sla_template["name"]

    resp = api_get(context, "sla/list")
    match = pyjq.first('.[] | select(."name"=="{0}") | select(."sla_type"=="{1}")'.format(sla_template, type),
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
        context.scenario.skip("No valid {0} template found".format(type))
        return
    if type == 'rto':
        context.sla_rto_levels = match['sla_rto_levels']
        context.sla_rto = match['sla_rto']
    elif type == 'rpo':
        context.sla_rpo = match['sla_rpo']
        context.sla_rpo_levels = match['sla_rpo_levels']
        context.sla_rpo_error_levels = match['sla_rpo_error_levels']
    context.sla_template = match["name"]


@when(
    u'I update the {type:string} template configuration, {template_values:option_values}'
)
def step_impl(context, type, template_values):
    assert context.sla_template != None
    template_params = {}
    if type == 'rto':
        template_params = {
            "name": context.sla_template,
            "sla_rto": template_values['sla_rto'],
            "sla_rto_levels": template_values['sla_rto_levels'],
            "sla_rto_te": "500",
            "sla_type": type
        }
        context.sla_rto_levels = template_values['sla_rto_levels']
        context.sla_rto = template_values['sla_rto']
    elif type == 'rpo':
        template_params = {
            "name": context.sla_template,
            "sla_rpo": template_values['sla_rpo'],
            "sla_rpo_levels": template_values['sla_rpo_levels'],
            "sla_rpo_error_levels": template_values['sla_rpo_error_levels'],
            "sla_type": type
        }
        context.sla_rpo = template_values['sla_rpo']
        context.sla_rpo_levels = template_values['sla_rpo_levels']
        context.sla_rpo_error_levels = template_values['sla_rpo_error_levels']

    api_request_post(context, "sla/update", template_params)


@then(u'the {type:string} template {should_or_not:should_or_not} exist')
def step_imp(context, type, should_or_not):
    assert context.sla_template != None
    match = None
    if type == 'rto':
        assert context.sla_rto_levels != None
        assert context.sla_rto != None

        resp = api_get(context, "sla/list")
        condition = '.[] | select(."name"=="{0}") | select(."sla_rto_levels"=="{1}") | select(."sla_rto"=="{2}") | select(."sla_type"=="{3}")'.format(
            context.sla_template, context.sla_rto_levels, context.sla_rto, type)
        match = pyjq.first(condition, resp)
    elif type == 'rpo':
        assert context.sla_rpo != None
        assert context.sla_rpo_levels != None
        assert context.sla_rpo_error_levels != None

        resp = api_get(context, "sla/list")
        condition = '.[] | select(."name"=="{0}") | select(."sla_rpo_levels"=="{1}") | select(."sla_rpo_error_levels"=="{2}") | select(."sla_rpo"=="{3}") | select(."sla_type"=="{4}")'.format(
            context.sla_template, context.sla_rpo_levels, context.sla_rpo_error_levels, context.sla_rpo, type)
        match = pyjq.first(condition, resp)

    assert (match != None and should_or_not) or (match == None and not should_or_not)


@when(u'I remove the {type:string} template')
def step_imp(context, type):
    assert context.sla_template != None
    template_params = {
        "name": context.sla_template,
        "sla_type": type
    }
    api_request_post(context, "sla/remove", template_params)


@then(u'the {type:string} template {should_or_not:should_or_not} exist')
def step_imp(context, type, should_or_not, duration):
    assert context.rto_template != None

    def remove_template(context, flag):
        res = api_get(context, "sla/list")
        match = pyjq.first(
            '.[] | select(."name"=="{0}") | select(."sla_type"=="{1}")'.format(context.rto_template, type), res)

        print(match)
        if (match == None and should_or_not) or (match != None and not should_or_not):
            return True

    waitfor(context, remove_template, duration)
